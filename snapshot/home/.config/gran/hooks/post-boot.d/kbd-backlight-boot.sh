#!/bin/bash

# Restore the user's preferred keyboard backlight level after boot.

DEFAULT_FILE="$HOME/.local/state/gran/indicators/kbd-backlight-default"
level=$(cat "$DEFAULT_FILE" 2>/dev/null || echo 1)
[[ "$level" =~ ^[0-9]+$ ]] || level=1
brightnessctl -d asus::kbd_backlight set "$level" >/dev/null 2>&1