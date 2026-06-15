#!/usr/bin/env bash
# HVA local watch loop — the always-on, volume-triggered read mechanism.
#
# Polls Meta insights every `hva.read_cadence_minutes`, runs the deterministic
# scorer (scripts/hva-score.py), and applies each creative's resolved
# autonomy_action. It drives the SAME Desk → scorer → autonomy gate as the
# on-demand /hva-review command and the hourly routine; it differs only in cadence.
#
# Autonomy (.gtm/config.json → hva.autonomy) is law:
#   recommend  → read-only: write decisions + print recommendations, NEVER touch the account
#   cut-auto   → auto-pause losers (saves money, reversible); recommend scales
#   full-auto  → auto-pause losers + bounded auto-scale winners
#
# Usage:  scripts/hva-watch.sh <campaign> <adset_id> [--once]
# Requires: meta CLI, python3, jq. Reads ACCESS_TOKEN/AD_ACCOUNT_ID from .env.gtm.
set -uo pipefail

CAMPAIGN="${1:?usage: hva-watch.sh <campaign> <adset_id> [--once]}"
ADSET_ID="${2:?usage: hva-watch.sh <campaign> <adset_id> [--once]}"
ONCE="${3:-}"

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCORER="$ROOT/scripts/hva-score.py"
CONFIG=".gtm/config.json"
HVADIR=".gtm/hva/$CAMPAIGN"
READS="$HVADIR/reads"
AUDIT="$HVADIR/audit.md"
mkdir -p "$READS"
[ -f "$ROOT/.env.gtm" ] && set -a && . "$ROOT/.env.gtm" && set +a

cfg() { python3 -c "import json,sys;print(json.load(open('$CONFIG')).get('$1',{}).get('$2',''))" 2>/dev/null; }
AUTONOMY="$(cfg hva autonomy)"; AUTONOMY="${AUTONOMY:-recommend}"
CADENCE="$(cfg hva read_cadence_minutes)"; CADENCE="${CADENCE:-60}"
MAXPCT="$(cfg hva max_daily_budget_increase_pct)"; MAXPCT="${MAXPCT:-20}"

log() { printf '%s\n' "$*"; }
audit() { printf '%s\n' "$*" >>"$AUDIT"; }

echo "HVA watch loop — campaign=$CAMPAIGN adset=$ADSET_ID autonomy=$AUTONOMY cadence=${CADENCE}m"
[ "$AUTONOMY" = "recommend" ] && echo "  recommend mode: read-only, no account writes."

read_cycle() {
  local stamp snap dec
  stamp="$(date +%Y%m%dT%H%M%S)"
  snap="$READS/snapshot-$stamp.json"
  dec="$READS/decision-$stamp.json"

  meta ads insights get --adset-id "$ADSET_ID" --level ad --output json \
    --fields ad_id,ad_name,impressions,spend,ctr,frequency,quality_ranking,actions \
    --date-preset last_3d >"$snap" 2>/dev/null
  local rc=$?
  case $rc in
    0) : ;;
    3) log "AUTH ERROR (exit 3): refresh ACCESS_TOKEN — skipping cycle"; return 0 ;;
    4) log "META API ERROR (exit 4): retrying once in 30s"; sleep 30
       meta ads insights get --adset-id "$ADSET_ID" --level ad --output json \
         --fields ad_id,ad_name,impressions,spend,ctr,frequency,quality_ranking,actions \
         --date-preset last_3d >"$snap" 2>/dev/null || { log "still failing — skipping cycle"; return 0; } ;;
    *) log "unexpected exit $rc — skipping cycle"; return 0 ;;
  esac

  # Normalize raw Meta insights for the scorer: map the actions[] array to the configured
  # qualifying event (conversions) and micro events (micro_conversions), convert Meta's
  # percent CTR to a fraction, and set the CAPI clean flag. WITHOUT this, every row reads as
  # 0 conversions and the dirty-feed gate never fires -> mass false cuts in auto modes.
  # This is the same mapping /hva-review does in its prep step.
  local norm="$READS/snapshot-$stamp-norm.json" totals
  PRIMARY="$(cfg targets primary_event)"; PRIMARY="${PRIMARY:-LEAD}"
  totals="$(python3 - "$snap" "$norm" "$PRIMARY" "$CONFIG" <<'PY'
import json, sys
snap, out_path, primary, config_path = sys.argv[1:5]
try: targets = json.load(open(config_path)).get("targets", {})
except Exception: targets = {}
micro = [m.lower() for m in (targets.get("micro_events") or [])]
prim = primary.lower()
raw = json.load(open(snap))
rows = raw.get("data", raw) if isinstance(raw, dict) else raw
norm = []
for r in rows:
    conv = mic = 0.0
    for a in (r.get("actions") or []):
        at = str(a.get("action_type", "")).lower(); val = float(a.get("value", 0) or 0)
        if prim in at: conv += val
        elif any(m in at for m in micro): mic += val
    norm.append({
        "ad_id": r.get("ad_id") or r.get("ad_name") or "unknown",
        "name": r.get("ad_name", r.get("ad_id", "")),
        "impressions": float(r.get("impressions", 0) or 0),
        "spend": float(r.get("spend", 0) or 0),
        "ctr": float(r.get("ctr", 0) or 0) / 100.0,   # Meta returns CTR as a percentage
        "frequency": float(r.get("frequency", 0) or 0),
        "quality_ranking": r.get("quality_ranking"),
        "conversions": conv, "micro_conversions": mic, "clean": True,
    })
json.dump({"creatives": norm}, open(out_path, "w"))
ti = sum(c["impressions"] for c in norm); tc = sum(c["conversions"] for c in norm)
print(f"{int(ti)} {int(tc)} {len(norm)}")
PY
)" || { log "normalization failed — skipping cycle"; return 0; }
  read -r TOTAL_IMP TOTAL_CONV NADS <<<"$totals"; TOTAL_IMP="${TOTAL_IMP:-0}"; TOTAL_CONV="${TOTAL_CONV:-0}"

  # Safety net: many impressions but zero qualifying events across the WHOLE batch usually
  # means a tracking break (CAPI/EMQ), not a batch of true losers. Acting would mass-pause
  # live ads. Hold the cycle and alert instead (mirrors the routine's EMQ hard-block).
  if [ "$TOTAL_IMP" -ge 5000 ] && [ "$TOTAL_CONV" -eq 0 ]; then
    log "⚠️  ${TOTAL_IMP} impressions, 0 qualifying events across ${NADS} ads — likely a tracking break (CAPI/EMQ). Skipping cycle to avoid mass false cuts."
    audit "## $(date -u +%Y-%m-%dT%H:%M:%SZ) — SKIPPED ($AUTONOMY): suspected tracking break (${TOTAL_IMP} imp, 0 conv)"
    return 0
  fi

  if ! python3 "$SCORER" "$norm" --config "$CONFIG" --out "$dec" 2>/tmp/hva-score.err; then
    log "scorer error: $(cat /tmp/hva-score.err)"; return 0
  fi

  # Render decisions to a temp file and iterate in THIS shell (not a pipe subshell) so the
  # one-scale-per-cycle guard persists across rows.
  local actions_tsv="$READS/.actions-$stamp.tsv"
  python3 -c "
import json
d = json.load(open('$dec'))
for c in d['creatives']:
    print('\t'.join([c['ad_id'], c['autonomy_action'], c['verdict'], c['triggering_signal']]))
" >"$actions_tsv" 2>/dev/null || { log "could not render decisions"; return 0; }

  audit "## $(date -u +%Y-%m-%dT%H:%M:%SZ) — autonomy $AUTONOMY"
  local scaled_adset=""
  while IFS=$'\t' read -r ad_id action verdict signal; do
    case "$action" in
      auto-pause)
        meta ads ad update "$ad_id" --status PAUSED --output json >/dev/null 2>&1 \
          && { log "PAUSED $ad_id ($signal)"; audit "- $ad_id: CUT ($signal) -> auto-paused"; } \
          || { log "FAILED to pause $ad_id"; audit "- $ad_id: CUT ($signal) -> pause FAILED"; } ;;
      auto-scale)
        # One bounded budget bump per ad set per cycle (Rule 3: never compound past the cap).
        if [ -n "$scaled_adset" ]; then
          log "SKIPPED second scale for adset $ADSET_ID this cycle (one-bump-per-cycle rule)"
          audit "- $ad_id: SCALE ($signal) -> skipped (adset already bumped this cycle)"
        else
          cur="$(meta ads adset get "$ADSET_ID" --output json 2>/dev/null | python3 -c 'import json,sys;print(json.load(sys.stdin).get("daily_budget",0))' 2>/dev/null)"
          if [ -n "$cur" ] && [ "$cur" -gt 0 ] 2>/dev/null; then
            new=$(( cur + cur * MAXPCT / 100 ))
            meta ads adset update "$ADSET_ID" --daily-budget "$new" --output json >/dev/null 2>&1 \
              && { log "SCALED adset $ADSET_ID $cur->$new cents ($signal, $ad_id)"; audit "- $ad_id: SCALE ($signal) -> adset budget $cur->$new cents (+${MAXPCT}%)"; scaled_adset="$ADSET_ID"; } \
              || { log "FAILED to scale adset"; audit "- $ad_id: SCALE -> budget update FAILED"; }
          else
            log "no per-ad-set daily_budget (CBO?) — cannot bump; skipping scale for $ad_id"
            audit "- $ad_id: SCALE ($signal) -> skipped (no ad-set daily_budget; CBO?)"
          fi
        fi ;;
      recommend-pause) log "RECOMMEND pause $ad_id ($signal)"; audit "- $ad_id: CUT ($signal) -> RECOMMENDED (awaiting approval)" ;;
      recommend-scale) log "RECOMMEND scale $ad_id ($signal)"; audit "- $ad_id: SCALE ($signal) -> RECOMMENDED (awaiting approval)" ;;
      hold) : ;;
    esac
  done <"$actions_tsv"
  rm -f "$actions_tsv"
  log "cycle complete -> $dec"
}

while true; do
  read_cycle
  [ "$ONCE" = "--once" ] && break
  sleep "$(( CADENCE * 60 ))"
done
