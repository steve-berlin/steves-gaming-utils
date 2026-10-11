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

# Why not pyautogui.mouseDown() / mouseUp()? Before each click they secretly
# "move" the mouse to where they last saw it. In Minecraft, any mouse movement
# turns the camera, so every click nudged the view a little. After many clicks
# the player ended up looking at the floor. Instead we send only the button
# press and release, with no movement, so the camera stays still.
#
# To do that we talk to X11 directly through Xlib, the same library pyautogui
# uses under the hood on Linux. X11 is the system that draws windows and
# passes mouse and keyboard input to them. _display is our connection to it.
# XTEST is an X11 feature that lets a program pretend to be a real mouse.
_display = Display()
LEFT = 1  # X11 numbers mouse buttons: 1 = left, 2 = middle, 3 = right


def button(event: int) -> None:
    """Press (X.ButtonPress) or release (X.ButtonRelease) the left button."""
    # fake_input comes from XTEST. It tells X11 "act as if this happened on
    # the real mouse or keyboard". Here we pass three things: our connection,
    # what happened (press or release) and which button (LEFT). We give no
    # position, so X11 clicks wherever the pointer already is and nothing moves.
    fake_input(_display, event, LEFT)
    _display.sync()  # send it now instead of waiting in a queue


HOTBAR = set("123456789")


def ask(prompt: str, default: str = "") -> str:
    shown = f" [{default}]" if default else ""
    return input(f"{prompt}{shown}: ").strip() or default


def ask_num(prompt: str, default: str = "", kind: type = int, minimum: float = 1):
    """No default means blank is a real answer (endless) and returns None.

    kind is what sort of number we want, and it's also the function that
    turns the typed text into that number. Python's int and float both work
    that way: int("3") gives 3, float("0.5") gives 0.5. Seconds use float so
    half a second is allowed. Counts use int (the default), because "2.5
    cycles" makes no sense.
    """
    while True:
        raw = ask(prompt, default)
        if not raw:
            return None
        try:
            # Same as int(raw) or float(raw). Text that isn't a number of that
            # kind, like "abc" or "2.5" for int, raises ValueError.
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
