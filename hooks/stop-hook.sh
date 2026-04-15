#!/usr/bin/env bash
# GTM Command Center — Stop Hook
# Runs on session end to log a timestamped entry to the GTM learnings directory.
# This script MUST always exit 0 to never block session exit.

set -euo pipefail

# Find the project's .gtm directory by walking up from the current working directory.
# The hook runs in the user's project directory, not the plugin directory.
find_gtm_dir() {
  local dir="$PWD"
  while [ "$dir" != "/" ]; do
    if [ -d "$dir/.gtm" ]; then
      echo "$dir/.gtm"
      return 0
    fi
    dir="$(dirname "$dir")"
  done
  return 1
}

GTM_DIR=$(find_gtm_dir 2>/dev/null) || {
  # No .gtm directory found in the project tree — nothing to do.
  exit 0
}

LEARNINGS_DIR="$GTM_DIR/learnings"
SESSION_LOG="$LEARNINGS_DIR/session-log.md"

# Ensure the learnings directory exists
mkdir -p "$LEARNINGS_DIR"

# Build the timestamp
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
DATE_SHORT=$(date -u +"%Y-%m-%d")

# If the session log does not exist, create it with a header
if [ ! -f "$SESSION_LOG" ]; then
  cat > "$SESSION_LOG" << 'HEADER'
# GTM Session Log

Timestamped entries auto-appended by the GTM Command Center stop hook.
Each entry records when a session ended and which agents were active.

---

HEADER
fi

# Detect which GTM artifacts were modified during this session.
# We check git status for .gtm/ files that are new or modified.
CHANGED_FILES=""
if command -v git &>/dev/null && git rev-parse --is-inside-work-tree &>/dev/null 2>&1; then
  CHANGED_FILES=$(git status --porcelain "$GTM_DIR" 2>/dev/null | head -20 || true)
fi

# Determine which areas were touched based on changed files
AREAS_TOUCHED=""
if echo "$CHANGED_FILES" | grep -q "plans/" 2>/dev/null; then
  AREAS_TOUCHED="${AREAS_TOUCHED}plans, "
fi
if echo "$CHANGED_FILES" | grep -q "creatives/" 2>/dev/null; then
  AREAS_TOUCHED="${AREAS_TOUCHED}creatives, "
fi
if echo "$CHANGED_FILES" | grep -q "metrics/" 2>/dev/null; then
  AREAS_TOUCHED="${AREAS_TOUCHED}metrics, "
fi
if echo "$CHANGED_FILES" | grep -q "strategies/" 2>/dev/null; then
  AREAS_TOUCHED="${AREAS_TOUCHED}strategies, "
fi
if echo "$CHANGED_FILES" | grep -q "campaigns/" 2>/dev/null; then
  AREAS_TOUCHED="${AREAS_TOUCHED}campaigns, "
fi
if echo "$CHANGED_FILES" | grep -q "learnings/" 2>/dev/null; then
  AREAS_TOUCHED="${AREAS_TOUCHED}learnings, "
fi
if echo "$CHANGED_FILES" | grep -q "config.json" 2>/dev/null; then
  AREAS_TOUCHED="${AREAS_TOUCHED}config, "
fi

# Trim trailing comma and space
AREAS_TOUCHED=$(echo "$AREAS_TOUCHED" | sed 's/, $//')

# Count changed files
CHANGE_COUNT=0
if [ -n "$CHANGED_FILES" ]; then
  CHANGE_COUNT=$(echo "$CHANGED_FILES" | wc -l | tr -d ' ')
fi

# Append the session entry
{
  echo "## Session: ${TIMESTAMP}"
  echo ""
  if [ -n "$AREAS_TOUCHED" ]; then
    echo "- **Areas touched:** ${AREAS_TOUCHED}"
  else
    echo "- **Areas touched:** none detected"
  fi
  echo "- **Files changed:** ${CHANGE_COUNT}"
  if [ -n "$CHANGED_FILES" ]; then
    echo "- **Changes:**"
    echo '```'
    echo "$CHANGED_FILES"
    echo '```'
  fi
  echo ""
  echo "---"
  echo ""
} >> "$SESSION_LOG"

# Always exit successfully — never block session exit
exit 0
