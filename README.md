# TP-Link Switch LED

Minimal custom Home Assistant integration for TP-Link Easy Smart switch LED control.

This version intentionally does **not** read the current LED state. It only sends:
- login POST to `/logon.cgi`
- LED GET to `/led_on_set.cgi`

The switch entity uses optimistic state (`assumed_state`).
