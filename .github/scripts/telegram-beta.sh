#!/usr/bin/env bash
# Copyright 2026 Aerium Browser
# SPDX-License-Identifier: GPL-3.0-only
set -euo pipefail

for v in TELEGRAM_BOT_TOKEN TELEGRAM_CHAT_ID TELEGRAM_API_ID TELEGRAM_API_HASH; do
  if [ -z "${!v:-}" ]; then echo "$v is not set"; exit 1; fi
done

apk=$(ls "$GITHUB_WORKSPACE"/release/aerium-*.apk | grep -v mapping | head -n1)
version=$(tr -d '[:space:]' < "$GITHUB_WORKSPACE/release/version.txt" 2>/dev/null || echo "")
sum=$(sha256sum "$apk" | cut -c1-16)

curl -s "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/logOut" > /dev/null || true

docker run -d --name tgapi -p 127.0.0.1:8081:8081 \
  -e TELEGRAM_API_ID -e TELEGRAM_API_HASH \
  aiogram/telegram-bot-api:latest > /dev/null

api="http://127.0.0.1:8081/bot$TELEGRAM_BOT_TOKEN"
for i in $(seq 1 60); do
  if curl -s "$api/getMe" | grep -q '"ok":true'; then break; fi
  sleep 5
done

ok=0
for i in 1 2 3; do
  out=$(curl -s --max-time 1800 \
    -F chat_id="$TELEGRAM_CHAT_ID" \
    -F document=@"$apk" \
    -F caption="Aerium $version beta, build $GITHUB_RUN_NUMBER
sha256 $sum" \
    "$api/sendDocument" || true)
  if grep -q '"ok":true' <<<"$out"; then ok=1; break; fi
  sleep 20
done

docker rm -f tgapi > /dev/null 2>&1 || true
[ "$ok" = 1 ] || { echo "Telegram upload failed"; exit 1; }
echo "Sent $(basename "$apk") to Telegram."
