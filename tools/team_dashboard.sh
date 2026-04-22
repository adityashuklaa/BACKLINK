#!/bin/bash
# Live team status dashboard
TEAM="backlink-quality-planning"
TEAM_DIR="$HOME/.claude/teams/$TEAM"
START_TS=$(stat -c %Y "$TEAM_DIR/config.json" 2>/dev/null || echo 0)

while true; do
  clear
  NOW=$(date +%s)
  ELAPSED=$((NOW - START_TS))
  MIN=$((ELAPSED / 60))
  SEC=$((ELAPSED % 60))

  echo "====================================================="
  echo "  TEAM DASHBOARD — $TEAM"
  echo "  Elapsed: ${MIN}m ${SEC}s   |   $(date +%H:%M:%S)"
  echo "====================================================="
  echo ""

  echo "MEMBERS:"
  if [ -f "$TEAM_DIR/config.json" ]; then
    grep -E '"name"|"agentType"|"model"' "$TEAM_DIR/config.json" \
      | paste - - - \
      | awk -F'"' '{printf "  %-15s %-20s %s\n", $4, $8, $12}'
  fi
  echo ""

  echo "INBOX ACTIVITY:"
  for inbox in "$TEAM_DIR/inboxes"/*.json; do
    [ -f "$inbox" ] || continue
    NAME=$(basename "$inbox" .json)
    SIZE=$(stat -c %s "$inbox" 2>/dev/null)
    MTIME=$(stat -c %Y "$inbox" 2>/dev/null)
    AGO=$((NOW - MTIME))
    MSG_COUNT=$(grep -o '"type"' "$inbox" 2>/dev/null | wc -l)
    printf "  %-15s %4d msgs   %6db   last activity %ds ago\n" "$NAME" "$MSG_COUNT" "$SIZE" "$AGO"
  done
  echo ""

  echo "LATEST FROM TEAM-LEAD INBOX (last 3 msgs):"
  if [ -f "$TEAM_DIR/inboxes/team-lead.json" ]; then
    python3 -c "
import json, sys
try:
    with open(r'$TEAM_DIR/inboxes/team-lead.json') as f:
        data = json.load(f)
    msgs = data if isinstance(data, list) else data.get('messages', [])
    for m in msgs[-3:]:
        sender = m.get('from', m.get('sender', '?'))
        summary = m.get('summary', m.get('content', ''))[:80]
        print(f'  [{sender}] {summary}')
except Exception as e:
    print(f'  (parse error: {e})')
" 2>/dev/null
  fi
  echo ""
  echo "-----------------------------------------------------"
  echo "  Refreshes every 5s. Ctrl+C to exit."

  sleep 5
done
