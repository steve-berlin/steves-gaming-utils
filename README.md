# steves-gaming-utils

Gaming scripts for a ThinkPad T480 on Debian 13 (trixie). All idempotent, all
`--dry-run`-able. Paths are hard-coded — `/games/steam` (sda3),
`/games/minecraft` (sda4); elsewhere, edit the constants at the script's top.

## Installers (repo root)

| Script | Does | Extra modes |
|---|---|---|
| `install-steam.sh` | i386 multiarch + `contrib non-free non-free-firmware`, then `steam-installer` | `--reinstall` `--uninstall` |
| `install-tld.sh` | The Long Dark (AppID `305620`) via Steam URL handlers, through `stm` | `--reinstall` `--verify` |
| `install-scrcpy.sh` | Upstream scrcpy into `/usr/local`, shadowing the lagging distro build | `--reinstall` `--uninstall` |
| `install-nic-tuning.sh` | Permanent zero-power-cost NIC tuning: BBR + fq, bigger buffers, TFO, MTU probing, WoL off, max rings | `--uninstall` |
| `fix-roblox-waydroid.sh` | Pixel 5 spoof so Roblox's Hyperion anticheat accepts the Waydroid container | `--uninstall` |
| `install-roblox-uptodown.sh` | Resolves + installs the Roblox APK from Uptodown into a **running** session | — |

Roblox order: spoof, start session, install APK.

## Launchers (`launchers/`)

Copy to `~/.local/bin/`. Each game launcher applies the same session
performance profile first — TLP stopped, `vm.swappiness=10`, governor
`performance` — all reverting on reboot. Assumes `sudo` is NOPASSWD for exactly
those three commands. (`nic-boost` is the exception; it only touches the NIC.)

| Launcher | Launches |
|---|---|
| `stm` | Steam, after registering `/games/steam` as a library. Deliberately not `gamemoderun`-wrapped — use `gamemoderun %command%` per game. |
| `rbx` | Roblox on Waydroid: container, nested weston on X11, session, app launch. Package via `$RBX_PKG`. |
| `rbxvm` | The Roblox Android-x86 VM under QEMU/KVM, from `discontinued/install-android-vm.sh`. |
| `nic-boost` | Not a game launcher: turns WiFi power-save and ethernet EEE off for lower latency, at a battery cost. `--revert`, or reboot. Deployed by `install-nic-tuning.sh`. |

Minecraft uses a zsh alias instead, `skl` — same three sudo lines, then
`gamemoderun java -jar ~/Desktop/SKlauncher-3.2.18.jar --workDir /games/minecraft`.

## `minecraft-autoclicker.py`

Holds left mouse in a loop; optional re-equip presses a hotbar key every N
cycles to rotate tools.

```bash
sudo apt install python3-pyautogui   # only dependency
./minecraft-autoclicker.py
```

Prompts: hold seconds, rest seconds, slots (blank = no re-equip), cycles per
slot, total cycles (blank = endless). Ctrl+C or pointer-to-top-left-corner
stops it and releases the button. Input is faked over X11 XTEST, so on a Wayland
session it reaches XWayland clients (Minecraft Java default), not native-Wayland
games. Walkthrough: [`docs/minecraft-autoclicker.md`](docs/minecraft-autoclicker.md).

## `discontinued/`

Reference only: `install-roblox.sh` (interactive Waydroid + APK setup),
`check-roblox-prereqs.sh` (binder/kernel gate), `install-android-vm.sh` (QEMU +
Android-x86 ISO + qcow2 for `rbxvm`).

## Related

- [steves-debian-setup](https://github.com/steve-berlin/steves-debian-setup) — rest of the box
- [steves-redmi-setup](https://github.com/steve-berlin/steves-redmi-setup) — Redmi 4A debloater + `redmi-gaming`
- `CLAUDE.md` — gotchas and the "why" per script
