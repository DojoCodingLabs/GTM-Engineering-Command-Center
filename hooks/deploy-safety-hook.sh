#!/bin/bash
# GTM Deploy Safety Hook
# Warns before any API write operations that could spend money or send emails
# Runs as PreToolUse hook for Bash commands

TOOL_INPUT="$1"

# Check for Meta Ads write operations
if echo "$TOOL_INPUT" | grep -qE "graph\.facebook\.com.*(POST|DELETE)|/campaigns|/adsets|/ads|/adcreatives|/adimages"; then
  if echo "$TOOL_INPUT" | grep -qE "POST|DELETE|PUT|PATCH"; then
    echo "⚠️  GTM Safety: Meta Ads API write detected. This may create or modify live ad campaigns." >&2
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
