#!/usr/bin/env python3
"""Minecraft autoclicker with hotbar re-equip.

Holds left mouse button for a while, releases, waits, repeats. Optionally
presses a hotbar number key every N cycles to rotate between tools.

Dependency: pyautogui (apt install python3-pyautogui, or pip in a venv).
"""

from __future__ import annotations

import sys
from itertools import cycle
from time import sleep

import pyautogui
from Xlib import X
from Xlib.display import Display
from Xlib.ext.xtest import fake_input

pyautogui.PAUSE = 0  # drop pyautogui's implicit 0.1 s delay after every call

# pyautogui.mouseDown/mouseUp re-read position() and fake a MotionNotify to it
# before every button event. Minecraft grabs the pointer and reads relative
# motion, so each warp to that stale point turns the camera; it adds up and the
# player ends up staring at the floor. Send bare button events instead.
_display = Display()
LEFT = 1


def button(event: int) -> None:
    fake_input(_display, event, LEFT)
    _display.sync()


HOTBAR = set("123456789")


def ask(prompt: str, default: str = "") -> str:
    shown = f" [{default}]" if default else ""
    return input(f"{prompt}{shown}: ").strip() or default


def ask_num(prompt: str, default: str = "", kind: type = int, minimum: float = 1):
    """No default means blank is a real answer (endless) and returns None."""
    while True:
        raw = ask(prompt, default)
        if not raw:
            return None
        try:
            value = kind(raw)
        except ValueError:
            print(f"  need a {'whole ' if kind is int else ''}number")
            continue
        if value >= minimum:
            return value
        print(f"  need >= {minimum}")


def ask_slots(prompt: str) -> list[str]:
    """Blank means no re-equip, so this prompt deliberately has no default."""
    while True:
        raw = ask(prompt).replace(",", " ").split()
        if not raw:
            return []
        if all(s in HOTBAR for s in raw):
            return raw
        print("  hotbar slots are 1-9")


def main() -> int:
    hold = ask_num("hold seconds", "2", float, 0)
    rest = ask_num("rest seconds", "1", float, 0)
    slots = ask_slots("hotbar slots to rotate e.g. 1,2, blank for none")
    every = ask_num("cycles per slot before re-equip", "1") if slots else 0
    total = ask_num("total cycles, blank for endless")

    slot_iter = cycle(slots)
    done = 0
    try:
        while total is None or done < total:
            if slots and done % every == 0:
                pyautogui.press(next(slot_iter))
            pyautogui.failSafeCheck()  # bare XTEST skips pyautogui's own check
            button(X.ButtonPress)
            sleep(hold)
            button(X.ButtonRelease)
            sleep(rest)
            done += 1
    except KeyboardInterrupt:
        pass
    finally:
        button(X.ButtonRelease)  # never leave the button stuck down
    print(f"\n{done} cycles done")
    return 0


if __name__ == "__main__":
    sys.exit(main())
