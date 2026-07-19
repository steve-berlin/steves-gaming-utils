#!/usr/bin/env bash
# Re-exec under bash if invoked as `sh install-roblox-uptodown.sh` — uses bashisms.
if [ -z "${BASH_VERSION:-}" ]; then
  exec /usr/bin/env bash "$0" "$@"
fi
# install-roblox-uptodown.sh — install the Roblox APK into Waydroid from Uptodown.
# Roblox isn't on the (deliberately GApps-free) container, so grab the APK from
# Uptodown and `waydroid app install` it. Run fix-roblox-waydroid.sh first for
# the device spoof. Needs a RUNNING Waydroid session. See CLAUDE.md.
#
# Arg forms:  <file.apk> | <https://…apk> | (none → resolve latest from Uptodown)
# Override the source page with UPTODOWN_URL.
set -euo pipefail

UPTODOWN_URL=${UPTODOWN_URL:-https://roblox.en.uptodown.com/android/download}
UA='Mozilla/5.0 (X11; Linux x86_64)'
dry=0; src=""
for a in "$@"; do
  case $a in
    --dry-run) dry=1 ;;
    -h|--help) echo "Usage: $0 [file.apk | url] [--dry-run]"; exit 0 ;;
    -*) echo "error: unknown arg: $a" >&2; exit 2 ;;
    *) src=$a ;;
  esac
done
run() { (( dry )) && printf 'DRY  %s\n' "$*" || "$@"; }

command -v waydroid >/dev/null || { echo "waydroid not installed" >&2; exit 1; }
command -v curl >/dev/null     || { echo "curl not installed" >&2; exit 1; }

tmp=$(mktemp -d); trap 'rm -rf "${tmp:-}"' EXIT
apk=""
case "$src" in
  *.apk) [[ -f $src ]] && apk=$src || { echo "no such file: $src" >&2; exit 1; } ;;
  http*) apk=$tmp/roblox.apk; run curl -fSL -A "$UA" -o "$apk" "$src" ;;
  "")    # Resolve the direct APK link off the Uptodown download page.
         echo "resolving latest Roblox APK from Uptodown…"
         url=$(curl -fsSL -A "$UA" "$UPTODOWN_URL" \
               | grep -oE 'https://dl\.uptodown\.com/[^"'"'"' ]+' | head -n1 || true)
         [[ -n $url ]] || { echo "couldn't resolve APK link — pass a file/URL: $0 <file.apk|url>" >&2; exit 1; }
         apk=$tmp/roblox.apk; run curl -fSL -A "$UA" -o "$apk" "$url" ;;
  *)     echo "unrecognised arg: $src (want a .apk, a URL, or nothing)" >&2; exit 1 ;;
esac

waydroid status 2>/dev/null | grep -qE '^Session:[[:space:]]+RUNNING' \
  || echo "warning: no running Waydroid session — start one (or rbx) before install."

echo "installing $apk into Waydroid…"
run waydroid app install "$apk"
echo "done — launch via rbx, or: waydroid app launch com.roblox.client"
