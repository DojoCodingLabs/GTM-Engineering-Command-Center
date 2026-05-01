#!/bin/bash
# GTM Deploy Safety Hook
# Warns before any API write operations that could spend money or send emails
# Runs as PreToolUse hook for Bash commands

TOOL_INPUT="$1"

# Check for Meta Ads write operations via raw Graph API (curl)
if echo "$TOOL_INPUT" | grep -qE "graph\.facebook\.com.*(POST|DELETE)|/campaigns|/adsets|/ads|/adcreatives|/adimages"; then
  if echo "$TOOL_INPUT" | grep -qE "POST|DELETE|PUT|PATCH"; then
    echo "⚠️  GTM Safety: Meta Ads API write detected (raw Graph API). This may create or modify live ad campaigns." >&2
  fi
fi

# Check for Meta Ads write operations via the official `meta ads` CLI
# Resources: campaign, adset, ad, creative, catalog, dataset, adimage
# Actions that mutate state: create, update, delete, connect, disconnect, assign-user
if echo "$TOOL_INPUT" | grep -qE "(^|[[:space:]])meta[[:space:]]+(ads[[:space:]]+(campaign|adset|ad|creative|catalog|dataset|adimage)|auth)[[:space:]]+(create|update|delete|connect|disconnect|assign-user|login)"; then
  echo "⚠️  GTM Safety: Meta Ads CLI write detected. This may create or modify live ad campaigns, datasets, or catalogs." >&2

  # Extra-loud warning if --force is present (skips CLI confirmation prompts)
  if echo "$TOOL_INPUT" | grep -qE "[[:space:]]--force([[:space:]]|$)"; then
    echo "🚨 GTM Safety: --force flag detected. The CLI will skip confirmation prompts. Verify the command is correct before approving." >&2
  fi
fi

# Check for email send operations
if echo "$TOOL_INPUT" | grep -qiE "resend\.emails\.send|sendgrid.*send|postmark.*send|/api/send-email"; then
  echo "⚠️  GTM Safety: Email send operation detected. This will deliver real emails to real people." >&2
fi

# Check for Stripe write operations
if echo "$TOOL_INPUT" | grep -qiE "stripe.*create|stripe.*update|stripe.*delete"; then
  echo "⚠️  GTM Safety: Stripe write operation detected. This may affect billing or subscriptions." >&2
fi

exit 0
