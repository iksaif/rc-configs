# Model editor YAML schema

Generated from `ModelEditorData` (the UI/IPC DTO). Arrays in exported YAML use the compact `{ i: N, ...fields }` form: `N` is the original zero-based index; any field equal to its default is omitted.

## ModelEditorData

Flat DTO for the model editor page. Mixers are included as a full 64-row list (the UI filters empty ones client-side) since that's ~10 KB of JSON — well under the Tauri IPC threshold.

- **`active`** — *boolean* — Whether this slot is listed as "active" in `RADIO/models.txt` (i.e. selectable from the radio's model list at runtime).
- **`curves`** — *array of [CurveEditData](#curveeditdata)* — Up to 32 curves referenced by mixers and expos (`curve_type > 0` ⇒ referenced by id; `curve_value` is the point array offset).
- **`custom_functions`** — *array of [CustomFunctionEditData](#customfunctioneditdata)* — Up to 64 "Special Functions" — switch-driven actions such as playing a sound, resetting a timer, adjusting a GVar, overriding a channel, etc.
- **`expos`** — *array of [ExpoEditData](#expoeditdata)* — Input expos — shape raw stick/pot deflection into the values that the mixer sees. Up to 64 rows.
- **`filename`** — *string* — Filename of the model on disk, typically `modelN.bin`.
- **`flight_modes`** — *array of [FlightModeEditData](#flightmodeeditdata)* — Up to 9 flight modes. `flight_modes[0]` is the default mode (always active when no other FM's switch is); 1..=8 activate by switch.
- **`limits`** — *array of [LimitEditData](#limiteditdata)* — Per-output-channel clamps, offsets, inversion and optional curve. One row per channel (CH1..CH16+).
- **`logical_switches`** — *array of [LogicalSwitchEditData](#logicalswitcheditdata)* — 64 logical switches (L1..L64). A logical switch is a boolean computed from other switches/sources/sensors/timers; it can then be used anywhere a real switch can.
- **`mixers`** — *array of [MixerEditData](#mixereditdata)* — Full 64-row mixer table. Each row combines a source (stick, switch, channel, ...) into a destination channel with weight/offset/curve. Rows with `src_raw == 0` are empty/unused.
- **`name`** — *string* — Model name shown on the TX screen. Up to 10 characters (zchar-encoded in the binary; plain UTF-8 here).
- **`slot`** — *integer* — Zero-based index of this model's slot on the SD card (0 = first).
- **`telemetry_sensors`** — *array of [TelemetrySensorEditData](#telemetrysensoreditdata)* — Up to 60 telemetry sensors streamed by the RX/receiver. Most fields are populated by the firmware at runtime; only `label` is user-editable.
- **`timers`** — *array of [TimerEditData](#timereditdata)* — The three user-configurable timers. `timers[0]` is Timer 1 on the radio.

## CurveEditData

One curve definition referenced by mixers and expos. Curve points live in a shared point buffer on-disk; editing individual points is not yet wired up in the UI — only the metadata (type, smooth, name, point count) is.

- **`curve_type`** — *integer* — 0 = standard (X-axis symmetric), 1 = custom (explicit X positions).
- **`index`** — *integer* — Zero-based curve index (0..=31). Reference this id from `MixerEditData.curve_value` etc.
- **`name`** — *string* — Optional 3-character curve label.
- **`points_minus_5`** — *integer* — Number of points minus 5 (firmware convention). So 0 = 5 points, 8 = 13 points, etc. Signed 6-bit.
- **`smooth`** — *integer* — 1 = smooth interpolation between points, 0 = linear.

## CustomFunctionEditData

One `CustomFunctionData` entry — the "Special Functions" tab. Binds a switch condition to an action (play sound, reset timer, adjust a GVar, override a channel, etc). SF1 = `index 0`, SF64 = `index 63`.

- **`active`** — *integer* — Enable flag (1 bit). Only meaningful for functions below `FUNC_FIRST_WITHOUT_ENABLE` (= 10). For higher indices the firmware repurposes this byte (e.g. repeat counter for play functions).
- **`all_mode`** — *integer* — `all` variant — `mode` byte (secondary parameter, e.g. GVar adjust mode: constant/incr/source).
- **`all_param`** — *integer* — `all` variant — `param` byte (tertiary parameter, e.g. GVar id, timer id).
- **`all_spare`** — *integer* — `all` variant — spare 32-bit slot reserved for future expansions.
- **`all_val`** — *integer* — `all` variant — numeric operand `val`. For SET_TIMER it's the seconds; for ADJUST_GVAR it's the value; for OVERRIDE_CHANNEL the channel value.
- **`func`** — *integer* — Action id — see `FUNC_*` constants. A few common ones on Tango: 0 OVERRIDE_CHANNEL, 3 RESET, 4 SET_TIMER, 5 ADJUST_GVAR, 10 PLAY_SOUND, 11 PLAY_TRACK, 14 PLAY_SCRIPT, 16 BACKGND_MUSIC.
- **`index`** — *integer* — Zero-based SF index (0 = SF1).
- **`payload_raw`** — *array of integer* — Raw 8-byte union payload — the source of truth for variants the editor doesn't decode explicitly yet. Preserved across save so custom variants aren't zeroed out on round-trip.
- **`play_name`** — *string* — Sound / script filename for PLAY_TRACK / PLAY_SCRIPT / BACKGND_MUSIC. Up to 6 ASCII chars (no extension); resolved at runtime as `SOUNDS/<lang>/<name>.wav` etc.
- **`switch`** — *integer* — Signed 9-bit switch reference (SWSRC). The function activates when this switch is true. 0 = disabled.
- **`switch_label`** — *string* — Resolved switch label.

## ExpoEditData

One `ExpoData` row — the "Inputs" tab in the OpenTX companion. Expos shape how a raw stick / pot deflection is mapped to the input that the mixer later reads. Typical use: add exponential curves to the sticks.

- **`carry_trim`** — *integer* — Trim handling: signed 6-bit. Negative values disable trim from this source; 0 = use the default trim for the stick.
- **`chn`** — *integer* — Zero-based destination input channel (0 = I1).
- **`curve_type`** — *integer* — Curve type: 0 = standard, >0 = custom curve id.
- **`curve_value`** — *integer* — Curve amount (for standard) or curve id (for custom).
- **`flight_modes`** — *integer* — Flight-mode bitmask — a bit set here disables the expo in that mode.
- **`index`** — *integer* — Row position in the expo table (0..=63).
- **`mode`** — *integer* — Activation mode (2 bits): 0 = disabled, 1 = positive-only, 2 = negative-only, 3 = both halves of the stick active.
- **`name`** — *string* — Optional 6-character expo label.
- **`offset`** — *integer* — Expo offset in percent.
- **`scale`** — *integer* — Input scale factor (14 bits). Rarely changed — use `weight` for normal gain adjustments.
- **`src_label`** — *string* — Resolved human-readable label for `src_raw`.
- **`src_raw`** — *integer* — Raw mix-source index used as the input (usually a stick or pot).
- **`switch`** — *integer* — Signed 9-bit switch reference — expo is only active when this switch is ON. 0 = always active.
- **`weight`** — *integer* — Expo weight in percent, signed (-100..=100).

## FlightModeEditData

One `FlightModeData` entry. FM0 (index 0) is the default — always active unless another FM's switch supersedes it. FM1..FM8 activate when their `switch` becomes true.

- **`fade_in`** — *integer* — Fade-in time when this FM becomes active, in tenths of a second.
- **`fade_out`** — *integer* — Fade-out time when leaving this FM, in tenths of a second.
- **`gvars`** — *array of integer* — Values for the 9 global variables (GVars 1..9) while this FM is active. `gvars[i]` is the raw signed value for GVar i+1.
- **`index`** — *integer* — Zero-based flight-mode index (0 = default FM0).
- **`name`** — *string* — Optional 6-character FM label shown on the TX screen.
- **`switch`** — *integer* — Signed 9-bit switch reference that activates this FM. Unused for FM0.

## LimitEditData

- **`channel`** — *integer* — Zero-based output channel (0 = CH1).
- **`curve`** — *integer* — Optional output curve applied after mixing, as a signed id into the curve table. 0 = straight-through.
- **`max`** — *integer* — Upper clamp on the output (+1023 = +100%).
- **`min`** — *integer* — Lower clamp on the output, as a signed 11-bit value (-1024 = -100%).
- **`name`** — *string* — Optional 4-character channel label (e.g. "AIL", "RUD").
- **`offset`** — *integer* — Output offset applied after clamping.
- **`ppm_center`** — *integer* — Sub-trim: PPM pulse-width offset around the 1500 µs centre, in µs. Range roughly -500..=500.
- **`revert`** — *integer* — 1 = invert output polarity for this channel.
- **`symetrical`** — *integer* — 1 = symmetrical trim (trim centres between `min` and `max` rather than 0). 0 = asymmetric.

## LogicalSwitchEditData

One `LogicalSwitchData` entry — a derived boolean switch that can be used anywhere a real switch can. L1 = `index 0`, L64 = `index 63`.

- **`andsw`** — *integer* — Optional extra AND/OR switch gating the final result.
- **`andsw_label`** — *string* — Resolved label for `andsw`.
- **`andsw_type`** — *integer* — How `andsw` combines with the primary condition: 0 = AND, 1 = OR.
- **`delay`** — *integer* — Activation delay in tenths of a second after the condition becomes true.
- **`duration`** — *integer* — How long the switch stays ON after activation, in tenths of seconds. 0 = indefinite (stays true as long as the condition holds).
- **`func`** — *integer* — Operator / function — see `LS_FUNC_*` constants. Broad groups: 0 = off; 1..=7 compare a source to a constant (`V<`, `V>`, range, ...); 8..=10,18 boolean ops (AND/OR/XOR/STICKY); 11 EDGE; 12..=14 compare two sources (`a == b` / `a > b` / `a < b`); 15..=16 DIFF functions; 17 TIMER.
- **`index`** — *integer* — Zero-based logical-switch index (0 = L1, 63 = L64).
- **`v1`** — *integer* — First operand. Interpretation depends on `func`: mix source (compares), switch source (AND/OR/EDGE), or integer (TIMER seconds).
- **`v1_label`** — *string* — Resolved label for `v1` (e.g. "Thr", "SA↑", "#17").
- **`v2`** — *integer* — Second operand. Typically a constant value for threshold compares, a switch for boolean ops, a source id for two-source compares, or a time for EDGE / TIMER.
- **`v3`** — *integer* — Third operand — only used by EDGE (`time_max`) and DIFF (threshold). Zero for other functions.
- **`v3_label`** — *string* — Resolved label for `v3`.

## MixerEditData

- **`carry_trim`** — *integer* — If non-zero, exclude the source's trim contribution from this row.
- **`curve_type`** — *integer* — Curve type: 0 = standard (differential/expo curve), >0 = custom curve selected by `curve_value`.
- **`curve_value`** — *integer* — Meaning depends on `curve_type`: for standard, the curve amount (expo percent); for custom, the signed curve id referencing `curves[]`.
- **`delay_down`** — *integer* — Fall-time delay, in tenths of a second.
- **`delay_up`** — *integer* — Rise-time delay before the output follows the input, in tenths of a second. 0 = instant.
- **`dest_ch`** — *integer* — Zero-based destination channel (0 = CH1, 1 = CH2, ...).
- **`flight_modes`** — *integer* — Flight-mode bitmask — a bit set here DISABLES the row when that flight mode is active. 0 = always active regardless of flight mode.
- **`index`** — *integer* — Row position in the mixer table (0..=63).
- **`mltpx`** — *integer* — How this row combines with earlier rows targeting the same channel: 0 = add (`+=`), 1 = multiply (`*=`), 2 = replace (`:=`).
- **`name`** — *string* — Optional 6-character label displayed in the mixer list.
- **`offset`** — *integer* — Constant added after the weight is applied, as a signed 14-bit value mapped to percent (-8192 = -100%).
- **`speed_down`** — *integer* — Fall-rate limit, in tenths of a second per unit.
- **`speed_up`** — *integer* — Rise-rate limit (slew) in tenths of a second per unit. 0 = instant.
- **`src_label`** — *string* — Resolved human-readable label for `src_raw` (e.g. "Rud", "CH1", "L3"). Computed by the backend; round-trip ignores this field on import.
- **`src_raw`** — *integer* — Raw source index — sticks (Rud/Thr/Ele/Ail), pots, switches, channels, logical switches, telemetry sensors, etc. Use `src_label` for the human-readable name.
- **`switch`** — *integer* — Signed 9-bit switch reference (SWSRC). The row is only active while this switch is ON. 0 = always active.
- **`weight`** — *integer* — Weight applied to the source, as a signed 11-bit value mapped to percent: -1024 = -100%, 0 = 0%, 1023 = +100%. Full range -1024..=1023.

## TelemetrySensorEditData

One telemetry sensor — usually auto-populated by the receiver over CRSF. Only `label` is routinely user-edited; the other fields are read-mostly.

- **`auto_offset`** — *integer* — 1 = auto-tare / zero-reference on model load.
- **`filter`** — *integer* — 1 = apply the firmware's low-pass filter before display.
- **`id`** — *integer* — Physical/logical sensor id (CRSF type code or protocol-specific id).
- **`index`** — *integer* — Zero-based sensor slot (0..=59).
- **`instance`** — *integer* — Sensor instance — lets multiple sensors of the same type coexist.
- **`label`** — *string* — User-facing sensor label, up to 4 characters (zchar on-disk).
- **`logs`** — *integer* — 1 = include this sensor in SD telemetry logs.
- **`only_positive`** — *integer* — 1 = clamp displayed values to >= 0.
- **`persistent`** — *integer* — 1 = save last value across power cycles.
- **`prec`** — *integer* — Number of decimal places when displaying this sensor (0..=3).
- **`sensor_type`** — *integer* — 0 = custom (streamed from RX), 1 = calculated (derived from other sensors on-radio).
- **`sub_id`** — *integer* — Sub-id of the physical sensor (firmware internal).
- **`unit`** — *integer* — 6-bit unit code (see FreedomTX `TelemetryUnit` enum — volts, amps, celsius, feet, metres, knots, rpm, ...).

## TimerEditData

- **`countdown_beep`** — *integer* — Countdown notification style: 0 = off, 1 = beep, 2 = voice, 3 = haptic.
- **`minute_beep`** — *integer* — If non-zero, emit a beep every minute of the timer.
- **`mode`** — *integer* — Timer mode / source. 0 = off; positive values reference a switch or channel that runs the timer while ON; negative = inverted.
- **`name`** — *string* — Optional 3-character label shown on the timer bar.
- **`persistent`** — *integer* — Persistence: 0 = don't persist, 1 = per-flight (reset on "new flight"), 2 = per-model (saved across power cycles).
- **`start`** — *integer* — Starting value in seconds. Used as the countdown start for countdown timers; ignored (stays at 0) for stopwatch mode.

