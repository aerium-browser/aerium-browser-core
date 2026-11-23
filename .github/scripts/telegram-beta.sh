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

release="$GITHUB_WORKSPACE/release"

docker run -d --name tgapi -p 127.0.0.1:8081:8081 \
  -e TELEGRAM_API_ID -e TELEGRAM_API_HASH -e TELEGRAM_LOCAL=1 \
  -v "$release:/release:ro" \
  aiogram/telegram-bot-api:latest > /dev/null
docker image inspect --format 'Telegram Bot API image {{index .RepoDigests 0}}' aiogram/telegram-bot-api:latest || true

api="http://127.0.0.1:8081/bot$TELEGRAM_BOT_TOKEN"
ready=0
for i in $(seq 1 60); do
  if curl -s "$api/getMe" | grep -q '"ok":true'; then ready=1; break; fi
  sleep 5
done
if [ "$ready" != 1 ]; then
  echo "The local Telegram Bot API server did not start"
  docker logs --tail 40 tgapi 2>&1 | sed "s/$TELEGRAM_BOT_TOKEN/***/g" || true
  docker rm -f tgapi > /dev/null 2>&1 || true
  exit 1
fi

report() {
  local out=$1 code=$2
  echo "  curl exit $code, response: $(sed "s/$TELEGRAM_BOT_TOKEN/***/g" <<<"${out:0:300}")"
}

send() {
  local file=$1 caption=$2 out code name
  name=$(basename "$file")
  for i in 1 2 3; do
    code=0
    out=$(curl -sS --max-time 1800 \
      --form-string chat_id="$TELEGRAM_CHAT_ID" \
      --form-string document="file:///release/$name" \
      --form-string caption="$caption" \
      "$api/sendDocument" 2>&1) || code=$?
    if grep -q '"ok":true' <<<"$out"; then
      echo "Sent $name to Telegram."
      return 0
    fi
    echo "Attempt $i to send $name from disk failed"
    report "$out" "$code"
    code=0
    out=$(curl -sS --max-time 1800 \
      --form-string chat_id="$TELEGRAM_CHAT_ID" \
      -F document=@"$file" \
      --form-string caption="$caption" \
      "$api/sendDocument" 2>&1) || code=$?
    if grep -q '"ok":true' <<<"$out"; then
      echo "Sent $name to Telegram."
      return 0
    fi
    echo "Attempt $i to upload $name failed"
    report "$out" "$code"
    sleep $((i * 30))
  done
  echo "Telegram upload of $name failed"
  docker logs --tail 40 tgapi 2>&1 | sed "s/$TELEGRAM_BOT_TOKEN/***/g" || true
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
