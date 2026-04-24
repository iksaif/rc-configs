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
| CH5     | SA     | **ARM**                             | "A for Arm" — left 2-pos, binary, never shared |
| CH6     | SB     | Flight mode: ANGLE / — / MANUAL     | mid = no aux active = ACRO fallback |
| CH7     | SC     | Nav: — / LOITER / RTH               | LOITER on MID detent; RTH on HIGH end-stop; LOW = no nav (clean boot) |
| CH8     | SD     | NAV LAUNCH                          | right 2-pos, deliberately opt-in |
| CH9     | SF (→ L01) | AUTO TUNE                       | needs sticky Logical Switch — see below |
| CH10    | SE     | BEEPER                              | hold-to-beep |

CH5 = INAV AUX1, CH6 = AUX2, and so on (AUX is zero-indexed in the `aux` command).

## Muscle memory

- **Left hand** — thumb on gimbal, index on **SA (ARM)**, middle/ring on SB (flight mode). Pull-toward-you = ANGLE, push-away = MANUAL.
- **Right hand** — thumb on gimbal, index on SC (nav — center for LOITER, push for RTH, pull for nothing), middle on **SD (LAUNCH)**.
- **Shoulders** — SE for beeper, SF for autotune toggle.

## Sticky Logical Switch for AUTO TUNE

SF is momentary — it jumps back to off the instant you release. To turn it into a press-once-on / press-again-off toggle, configure a Logical Switch and remap CH9 to it:

1. **Logical Switches → L01**
   - Func: `Sticky`
   - V1: `SF↓` (button press event — on this Tango, `↓` = PWM high = pressed)
   - V2: `SF↓` (same event toggles it off next time)
2. **Mixes → CH9**
   - Replace the current `SF` source with `L01`
   - Weight 100, no curve

Tango 2 switch-notation quick reference: in the radio's menus, `S*↑` means
PWM low (toward the ↑-arrow plastic label, unpressed for momentaries); `S*↓`
means PWM high (toward the ↓-arrow, pressed). Same convention across SA-SF.

**Strongly recommended:** add a Special Function playing a voice clip ("Auto tune on" / "Auto tune off") when L01 transitions. You really don't want to forget AUTO TUNE is active.

## Schema

`model5.plane.yaml` follows the `ModelEditorData` DTO documented in
[`../docs/tango2/model-schema.md`](../docs/tango2/model-schema.md) (JSON variant: `model-schema.json`).

## Tango 2 → radio sync

The YAML isn't flashed directly to the radio — use FreedomTX Companion
(or the equivalent EdgeTX fork) to load the corresponding `.bin` onto the
SD card, then reload the model on the Tango. The checked-in YAML is the
"source of truth" for diffs and rollback.
