# minecraft-autoclicker.py — explained (ELI11)

Holds your **left mouse button** down for you, over and over: long tunnels,
walls of stone, hoe-farming while you do something else. New part: it can
**re-equip** — press a hotbar number key between batches of clicking, so
pickaxe → shovel → pickaxe, forever.

## Install

Needs one library, `pyautogui`, to reach your mouse and keyboard:

```bash
sudo apt install python3-pyautogui
```

If apt lacks it, use a venv (private package folder, system Python untouched):

```bash
python3 -m venv ~/.venvs/autoclicker
~/.venvs/autoclicker/bin/pip install pyautogui
~/.venvs/autoclicker/bin/python minecraft-autoclicker.py
```

## Run

`./minecraft-autoclicker.py`, then five questions. Enter accepts the
`[bracketed]` default.

| Question | Means | Example |
|---|---|---|
| `hold seconds [2]` | How long the button stays pressed. | `2` breaks stone with a decent pickaxe |
| `rest seconds [1]` | Wait after releasing, before next press. | `1` |
| `hotbar slots to rotate e.g. 1,2, blank for none` | Hotbar keys to cycle. **Blank = click only, no swapping.** | `1,2` |
| `cycles per slot before re-equip [1]` | Press-and-release rounds per slot before switching. Asked only if you gave slots. | `10` |
| `total cycles, blank for endless` | Total rounds. Blank = until you stop it. | `100` |

## What re-equip looks like

Answers hold `2`, rest `1`, slots `1,2`, cycles per slot `3`:

```
key 1 (pickaxe) -> 3x [hold 2s, rest 1s]
key 2 (shovel)  -> 3x [hold 2s, rest 1s]
key 1 (pickaxe) -> 3x ... round and round
```

Slot list loops (`itertools.cycle`), so `1,2,3` goes 1, 2, 3, 1, 2, 3…

## Stopping

**Ctrl+C.** The script catches it, releases the button, prints the round count,
quits. The release matters — a script dying mid-hold leaves your mouse stuck
clicking. Second panic switch, built into `pyautogui`: shove the real pointer
into the screen's **top-left corner**, which raises `FailSafeException` and also
releases.

## Wayland warning

This box runs a **Wayland** session; `pyautogui` fakes input through the old X11
XTEST feature. Minecraft Java via **XWayland** (the default) works. A **native
Wayland** game gets nothing — no crash, no clicks, no error. That silence is the
symptom. Fix for that case is `ydotool` (talks to the kernel input layer, so
desktop type stops mattering), unused here because it needs a background service
and root-ish permissions.

## Playing fair

Single-player or your own server: nobody cares. Public servers often ban macros
— check their rules first.

## Why the code looks like that

- **`pyautogui.PAUSE = 0`** — library otherwise sleeps 0.1 s after *every* call,
  making a 2 s hold really 2.1 s. We do our own timing.
- **`try / except KeyboardInterrupt / finally`** — `finally` runs however the
  loop ends (done, Ctrl+C, crash), so `mouseUp()` always happens.
- **`while total is None or done < total`** — one loop serves "100 times" and
  "forever". Old version had two near-copies and the endless one was unreachable.
- **Blank slot prompt has no default** — blank is itself a real answer ("don't
  re-equip"); a default would make "no" impossible to say.
- **`ask_slots` accepts only `1`-`9`** — the hotbar's nine slots are named by
  those keys. Typo `x` is re-asked, not pressed mid-game.

## Bugs fixed from version 1

| Was | Why broken |
|---|---|
| `from pyautogui` | Not valid Python; needs `import pyautogui`. File couldn't start. |
| `for i in range(1, iRep)` | Missing `:` — syntax error. Also `range(1, n)` runs `n-1` times, one short. |
| `int(reeq)` on a skipped question | Enter gives `""`, and `int("")` crashes. |
| `if iRep is None:` | `input()` never returns `None`; endless branch was dead code. |
| `int(t1)` for seconds | Refused `0.5`. Now `float`, so sub-second timing works. |
