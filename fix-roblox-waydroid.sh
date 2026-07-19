#!/usr/bin/env bash
# Re-exec under bash if invoked as `sh fix-roblox-waydroid.sh` — uses bashisms.
if [ -z "${BASH_VERSION:-}" ]; then
  exec /usr/bin/env bash "$0" "$@"
fi
# fix-roblox-waydroid.sh — spoof a Waydroid container so Roblox's Hyperion
# anticheat runs. Sets Pixel-5 (redfin) build props + hides emulator hints in
# waydroid_base.prop, plus fake touch/wifi. Companion to `rbx`; install the APK
# with install-roblox-uptodown.sh. ARM translation (libhoudini) is a prereq —
# this only checks for it. See CLAUDE.md.
set -euo pipefail

CFG=/var/lib/waydroid/waydroid.cfg
PROP=/var/lib/waydroid/waydroid_base.prop
BACKUP=/var/lib/waydroid/.roblox-fix-backup
PKG=${ROBLOX_PKG:-com.roblox.client}

dry=0; mode=apply
for a in "$@"; do
  case $a in
    --uninstall|--revert) mode=revert ;;
    --dry-run)            dry=1 ;;
    -h|--help) echo "Usage: sudo $0 [--uninstall|--revert] [--dry-run]"; exit 0 ;;
    *) echo "error: unknown arg: $a" >&2; exit 2 ;;
  esac
done
run() { (( dry )) && printf 'DRY  %s\n' "$*" || "$@"; }

[[ $EUID -eq 0 ]]              || { echo "run as root: sudo $0 $*" >&2; exit 1; }
command -v waydroid >/dev/null || { echo "waydroid not installed" >&2; exit 1; }

# ro.* build props go in waydroid_base.prop (survive restart); persist.* runtime.
BUILD=(
  ro.product.brand=google ro.product.manufacturer=Google "ro.product.model=Pixel 5"
  ro.product.device=redfin ro.product.name=redfin ro.build.product=redfin
  ro.product.board=redfin ro.board.platform=msmnile ro.hardware=redfin
  "ro.build.fingerprint=google/redfin/redfin:13/TQ3A.230901.001/10750268:user/release-keys"
  "ro.build.description=redfin-user 13 TQ3A.230901.001 10750268 release-keys"
  ro.build.display.id=TQ3A.230901.001 ro.build.type=user ro.build.tags=release-keys
  ro.debuggable=0 ro.adb.secure=1 ro.secure=1 ro.kernel.qemu=0 ro.kernel.qemu.gles=0
  ro.boot.hardware=redfin ro.boot.vbmeta.device_state=locked ro.boot.verifiedbootstate=green
  ro.boot.flash.locked=1 ro.boot.veritymode=enforcing
)
RUNTIME=( "persist.waydroid.fake_touch=$PKG" 'persist.waydroid.fake_wifi=*' )

if [[ $mode == revert ]]; then
  if [[ -f $BACKUP/waydroid_base.prop ]]; then run cp "$BACKUP/waydroid_base.prop" "$PROP"; echo "restored $PROP from $BACKUP"
  else echo "no backup at $BACKUP — nothing to restore"; fi
  for kv in "${BUILD[@]}" "${RUNTIME[@]}"; do run waydroid prop set "${kv%%=*}" "" 2>/dev/null || true; done
  run waydroid session stop 2>/dev/null || true
  run systemctl restart waydroid-container 2>/dev/null || true
  echo "reverted — start a session with: waydroid session start"; exit 0
fi

echo "=== Roblox Waydroid spoof (arch: $(uname -m)) ==="
grep -qE 'lib(houdini|ndk_translation)\.so' "$PROP" "$CFG" 2>/dev/null \
  || echo "warning: no ARM translation layer — Roblox is ARM; install libhoudini via waydroid_script first."
[[ -d $BACKUP ]] || { run mkdir -p "$BACKUP"; run cp "$PROP" "$BACKUP/" 2>/dev/null || true; }
run waydroid session stop 2>/dev/null || true

echo "writing spoof + hardening props to $PROP…"
for kv in "${BUILD[@]}"; do
  k=${kv%%=*} v=${kv#*=}
  if grep -q "^${k}=" "$PROP" 2>/dev/null; then run sed -i "s|^${k}=.*|${k}=${v}|" "$PROP"
  elif (( dry )); then echo "DRY  append ${k}=${v} to $PROP"
  else printf '%s=%s\n' "$k" "$v" >> "$PROP"; fi
done
for kv in "${RUNTIME[@]}"; do run waydroid prop set "${kv%%=*}" "${kv#*=}" 2>/dev/null || true; done

run systemctl restart waydroid-container 2>/dev/null || true
(( dry )) || sleep 3
run bash -c 'waydroid session start >/dev/null 2>&1 &' || true
echo "=== Done === install the APK: install-roblox-uptodown.sh; launch via rbx. Revert: sudo $0 --uninstall"
