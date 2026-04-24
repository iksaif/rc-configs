# Tango 2 + INAV mode layout — proposal (Claude)

## Tango 2 channel map

| CH  | AUX | Source            | Role                                                  |
|-----|-----|-------------------|-------------------------------------------------------|
| CH5 | 1   | **SA** (L 2-pos)  | ARM                                                   |
| CH6 | 2   | **SB** (L 3-pos)  | NAV — LOITER · — · RTH                                |
| CH7 | 3   | **SC** (R 3-pos)  | MODE — ANGLE · ACRO · MANUAL                          |
| CH8 | 4   | **SD** (R 2-pos)  | NAV LAUNCH                                            |
| CH9 | 5   | **SE** (shoulder) | BEEPER (hold)                                         |
| CH10| 6   | **SF** (shoulder) | AUTO TUNE (via sticky logical switch — see below)     |

## Aux block — paste into all three plane configs

```
# Unified modes across Baloo / Swordfish / Dolphin (Tango 2 gamepad)
aux 0  0  0 1800 2100    # ARM          on SA HIGH
aux 1 11  1  900 1300    # NAV POSHOLD  on SB LOW   (loiter)
aux 2 10  1 1800 2100    # NAV RTH      on SB HIGH  (safety)
aux 3  1  2  900 1300    # ANGLE        on SC LOW   (default)
aux 4 12  2 1800 2100    # MANUAL       on SC HIGH  (expert)
aux 5 36  3 1800 2100    # NAV LAUNCH   on SD HIGH  (opt-in)
aux 6 13  4 1800 2100    # BEEPER       on SE press (momentary)
aux 7 21  5 1800 2100    # AUTO TUNE    on SF→LS-latched (see below)
```

ACRO = the no-aux fallback (SC MID). Don't burn a switch position on it.

## Finger map

- **Left hand** = safety hand. Thumb on gimbal, index on SA (arm), middle/ring on SB (nav — LOITER pull-toward-you, RTH push-away). In a panic you flip SB with just your left fingers without letting go of the right stick.
- **Right hand** = flying hand. Thumb on gimbal, index on SC (flight mode — ANGLE pull-toward-you, MANUAL push-away), middle on SD (launch — only flipped up pre-throw).
- **Shoulders** SE/SF sit under your middle/ring fingers while gripping. Hold to activate.

## Why this layout

- **ARM on SA (2-pos, binary)** — matches the hardware. A 2-pos flip = armed or not. One switch, one role, never shared.
- **LOITER + RTH on the same 3-pos (SB)** — both are nav safety nets, both need one-finger access. Putting them at opposite extremes means your hand physically can't hit the wrong one by accident, and the neutral mid position gives you "no nav override, fly normally".
- **ANGLE/ACRO/MANUAL on SC** — right-hand flight-mode control. Pulling SC toward your palm (LOW) = ANGLE, the safest choice; the panic flinch is toward you.
- **NAV LAUNCH on SD (2-pos)** — deliberate: you flip it up right before you throw, flip it down after take-off. The 2-pos toggle matches the "on-or-off, one-time-per-flight" usage pattern exactly.
- **BEEPER on SE** — momentary hold-to-beep. Perfect fit: release = silence.
- **AUTO TUNE on SF with a sticky trick** — a bare momentary doesn't give INAV the sustained aux band it needs (see below).

## Caveats / must-knows

1. **RTH + LOITER asked at once**: RTH wins. Flipping SB through MID from LOW to HIGH briefly passes through "no nav", which is normal.
2. **NAV LAUNCH re-entry mid-flight**: if you leave SD HIGH after the throw and your throttle drops below the launch threshold, INAV can re-enter launch state. After every takeoff, habit: flip SD back to LOW.
3. **AUTO TUNE accident**: if SF's sticky latch is on unintentionally, the plane starts inducing oscillations. Keep the latch OFF unless you're doing a tuning pass. Altitude is your friend; if it happens, flip the latch back off.
4. **SA single-bump ARM**: one deliberate switch flip = armed. If that worries you, switch to a two-stage scheme via a logical switch that requires SA HIGH **and** throttle-low for >1 s.

## Sticky AUTO TUNE — EdgeTX logical switch

SF rests at low and jumps to high only while pressed. To make it a toggle (press = on, press again = off), use an EdgeTX Sticky LS:

```
L1 (Logical Switch 1)
  Func:  STICKY
  V1:    SF↑        (press event — SF crosses into high)
  V2:    SF↑        (same condition releases the sticky on the next press)
  AND:   none
```

Then in the mixer, replace the `SF` source on CH10 with `L1`. Pressing SF once latches CH10 HIGH (L1 = 1 → CH10 ≈ 2000 µs); pressing again unlatches. That's what INAV needs for AUTO TUNE to work as a session mode.

**Alternative** if you'd rather not fiddle with the Tango logic: keep AUTO TUNE unmapped normally, and when you need it, temporarily swap LAUNCH ↔ AUTO TUNE on SD in the aux block for that single session. Simpler, at the cost of 30 seconds of CLI swap before a tuning flight.

## Bonus I added uninvited

- **BEEPER on SE** — tiny cost, huge payoff the first time you lawn-dart into tall grass.

## Things I considered and rejected

- **PREARM (two-stage arm)** — SA is deliberate enough; adding a two-stage flip adds friction that doesn't pay for itself on a hobby setup.
- **AIRMODE runtime toggle** — each plane already picks the right AIRMODE state as a master setting; runtime toggle invites accidental changes.
- **FAILSAFE mode aux** — overrides your `failsafe_procedure` setting; RTH already configured as FS behaviour declaratively in the master block.

## Per-plane differences

None. Same aux block, same finger layout, three planes.
