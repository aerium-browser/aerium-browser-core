#!/usr/bin/env bash
# Copyright 2026 Aerium Browser
# SPDX-License-Identifier: GPL-3.0-only
set -euo pipefail

for v in TELEGRAM_BOT_TOKEN TELEGRAM_CHAT_ID TELEGRAM_API_ID TELEGRAM_API_HASH; do
  if [ -z "${!v:-}" ]; then echo "$v is not set"; exit 1; fi
done

apk=$(find "$GITHUB_WORKSPACE/release" -maxdepth 1 \( -name 'aerium-*.apk' -o -name 'aerium-*.aab' \) | sort | head -n1)
[ -n "$apk" ] || { echo "Nothing to send"; exit 1; }
label=beta
[ "${AERIUM_KIND:-}" = bundle ] && label="app bundle"
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

send() {
  local file=$1 caption=$2 out
  for i in 1 2 3; do
    out=$(curl -s --max-time 1800 \
      -F chat_id="$TELEGRAM_CHAT_ID" \
      -F document=@"$file" \
      -F caption="$caption" \
      "$api/sendDocument" || true)
    if grep -q '"ok":true' <<<"$out"; then
      echo "Sent $(basename "$file") to Telegram."
      return 0
    fi
    sleep 20
  done
  echo "Telegram upload of $(basename "$file") failed"
  return 1
}

ok=0
if send "$apk" "Aerium $version $label, build $GITHUB_RUN_NUMBER
sha256 $sum"; then
  ok=1
fi

if [ "$ok" = 1 ] && [ "${AERIUM_KIND:-}" = bundle ]; then
  if [ -f "$apk.mapping" ]; then
    send "$apk.mapping" "Deobfuscation file for Play Console, build $GITHUB_RUN_NUMBER" || true
  fi
  symbols=$(find "$GITHUB_WORKSPACE/release" -maxdepth 1 -name 'aerium-*-native-debug-symbols.zip' | head -n1)
  if [ -n "$symbols" ]; then
    send "$symbols" "Native debug symbols for Play Console, build $GITHUB_RUN_NUMBER" || true
  fi
fi

docker rm -f tgapi > /dev/null 2>&1 || true
[ "$ok" = 1 ] || exit 1
