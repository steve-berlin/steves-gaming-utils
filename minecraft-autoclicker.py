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

pyautogui.PAUSE = 0  # drop pyautogui's implicit 0.1 s delay after every call

HOTBAR = set("123456789")


def ask(prompt: str, default: str = "") -> str:
    shown = f" [{default}]" if default else ""
    return input(f"{prompt}{shown}: ").strip() or default


def ask_float(prompt: str, default: str) -> float:
    while True:
        try:
            value = float(ask(prompt, default))
        except ValueError:
            print("  need a number")
            continue
        if value < 0:
            print("  need >= 0")
            continue
        return value


def ask_int(prompt: str, default: str, minimum: int = 1) -> int:
    while True:
        try:
            value = int(ask(prompt, default))
        except ValueError:
            print("  need a whole number")
            continue
        if value < minimum:
            print(f"  need >= {minimum}")
            continue
        return value


def ask_opt_int(prompt: str, minimum: int = 1) -> int | None:
    """Blank means endless, so this prompt deliberately has no default."""
    while True:
        raw = ask(prompt)
        if not raw:
            return None
        try:
            value = int(raw)
        except ValueError:
            print("  need a whole number, or blank")
            continue
        if value < minimum:
            print(f"  need >= {minimum}, or blank")
            continue
        return value


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
    hold = ask_float("hold seconds", "2")
    rest = ask_float("rest seconds", "1")
    slots = ask_slots("hotbar slots to rotate e.g. 1,2, blank for none")
    every = ask_int("cycles per slot before re-equip", "1") if slots else 0
    total = ask_opt_int("total cycles, blank for endless")

    slot_iter = cycle(slots) if slots else None
    done = 0
    try:
        while total is None or done < total:
            if slot_iter and done % every == 0:
                pyautogui.press(next(slot_iter))
            pyautogui.mouseDown()
            sleep(hold)
            pyautogui.mouseUp()
            sleep(rest)
            done += 1
    except KeyboardInterrupt:
        pass
    finally:
        pyautogui.mouseUp()  # never leave the button stuck down
    print(f"\n{done} cycles done")
    return 0


if __name__ == "__main__":
    sys.exit(main())
