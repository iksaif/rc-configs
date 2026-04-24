# TBS Tango 2

FreedomTX / EdgeTX-fork model config for my three-plane fleet.

## Physical switch inventory

| Logical | Physical location          | Type       |
|---------|-----------------------------|------------|
| SA      | top-left grip               | 2-position |
| SB      | top-left grip               | 3-position |
| SC      | top-right grip              | 3-position |
| SD      | top-right grip              | 2-position |
| SE      | left shoulder (lower)       | momentary  |
| SF      | right shoulder (lower)      | momentary  |

Plus two gimbals (mode 2), trim wheel, and menu rocker. That's the whole switch budget — no more.

## Channel map (CH5–CH10)

| Channel | Source | Role                                | Notes |
|---------|--------|-------------------------------------|-------|
| CH5     | SD     | **ARM**                             | binary — never shared |
| CH6     | SB     | Flight mode: ANGLE / — / MANUAL     | mid = no aux active = ACRO fallback |
| CH7     | SC     | Nav: LOITER / — / RTH               | RTH on HIGH end-stop |
| CH8     | SA     | NAV LAUNCH                          | deliberately opt-in |
| CH9     | SF (→ L01) | AUTO TUNE                       | needs sticky Logical Switch — see below |
| CH10    | SE     | BEEPER                              | hold-to-beep |

CH5 = INAV AUX1, CH6 = AUX2, and so on (AUX is zero-indexed in the `aux` command).

## Muscle memory

- **Left hand** — thumb on gimbal, index on SA (launch enable), middle/ring on SB (flight mode). Pull-toward-you = ANGLE, push-away = MANUAL.
- **Right hand** — thumb on gimbal, index on SC (nav — pull for LOITER, push for RTH), middle on SD (ARM).
- **Shoulders** — SE for beeper, SF for autotune toggle.

## Sticky Logical Switch for AUTO TUNE

SF is momentary — it jumps back to off the instant you release. To turn it into a press-once-on / press-again-off toggle, configure a Logical Switch and remap CH9 to it:

1. **Logical Switches → L01**
   - Func: `Sticky`
   - V1: `SF↑` (button press event)
   - V2: `SF↑` (same event toggles it off next time)
2. **Mixes → CH9**
   - Replace the current `SF` source with `L01`
   - Weight 100, no curve

**Strongly recommended:** add a Special Function playing a voice clip ("Auto tune on" / "Auto tune off") when L01 transitions. You really don't want to forget AUTO TUNE is active.

## Schema

`model5.plane.yaml` follows the `ModelEditorData` DTO documented in
[`../docs/tango2/model-schema.md`](../docs/tango2/model-schema.md) (JSON variant: `model-schema.json`).

## Tango 2 → radio sync

The YAML isn't flashed directly to the radio — use FreedomTX Companion
(or the equivalent EdgeTX fork) to load the corresponding `.bin` onto the
SD card, then reload the model on the Tango. The checked-in YAML is the
"source of truth" for diffs and rollback.
