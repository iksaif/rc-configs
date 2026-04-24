# INAV `aux` format — quick reference

```
aux <slot> <permanent_id> <aux_channel> <start_us> <end_us>
```

- `slot` — 0..N, one row per slot. Duplicates in a slot replace the earlier row.
- `permanent_id` — mode id; see `inav-box-ids.json`.
- `aux_channel` — **zero-based**. AUX1 = 0, AUX2 = 1, …, AUX7 = 6. For a CRSF receiver, AUX1 is the first channel after the four sticks: CH5 → AUX1.
- `start_us` / `end_us` — pulse-width window (microseconds). Stored on the FC in 25 µs steps, so round to multiples of 25. Mode engages when the channel's pulse falls inside [start, end].

Typical 3-position switch bands:
| Position | Pulse (µs) | Suggested window      |
|----------|------------|------------------------|
| LOW      | ~1000      | `900 1300`             |
| MID      | ~1500      | `1300 1700` (skip 1700 to avoid overlap with HIGH) |
| HIGH     | ~2000      | `1800 2100`            |

## Interaction notes

- If no flight-mode aux is active, the plane is in **ACRO** (rates-only, no self-level).
- **NAV RTH** and **NAV POSHOLD** override manual/flight-mode aux when engaged. RTH outranks POSHOLD.
- Modes can be combined: `NAV POSHOLD + ANGLE` gives a leveled loiter around the current GPS position (fixed-wing: orbit). `NAV RTH + ANGLE` is redundant — RTH already handles attitude.
- **NAV LAUNCH**: once armed, exits automatically when the plane clears the launch thresholds (pitch down + altitude). Leaving the switch engaged after the bird is flying is harmless; it just means the next disarm→arm will re-enter launch mode.
- **AUTO TUNE**: engage only in flight, preferably in ANGLE or ACRO, with plenty of altitude. The firmware induces oscillations on pitch and roll.
- **Arming gates**: `nav_extra_arming_safety = ALLOW_BYPASS` (default in 9.x) lets you arm without a GPS fix by holding full-right yaw while flipping the arm switch. Only matters if a GPS-dependent mode is in any aux slot.

## Example — simple 3-switch setup

```
aux 0 0  0 1800 2100   # ARM on AUX1 HIGH
aux 1 1  1  900 1300   # ANGLE on AUX2 LOW
aux 2 10 2 1800 2100   # NAV RTH on AUX3 HIGH
```

## What the radio sends

For CRSF (Crossfire / ExpressLRS), the first four channels are the sticks (T/A/E/R in CH1-4). CH5..CH16 are user-assignable aux channels sent as 11-bit values mapped into the 988..2012 µs range (roughly).

Position breakpoints on a stock EdgeTX 3-pos switch are at -100%, 0%, +100%, which produce ~988 / 1500 / 2012 µs at the FC. A window of 900-1300 comfortably captures LOW; 1800-2100 captures HIGH; 1300-1700 captures MID without overlap.
