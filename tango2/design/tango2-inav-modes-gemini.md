# Tango 2 + INAV mode layout — proposal (Gemini)

Designing a unified layout for the Tango 2 requires balancing its unique ergonomics—specifically the reliance on two-position switches and momentary buttons—with the complex mode hierarchy of INAV.

## 1. Tango 2 Channel Map (EdgeTX/FreedomTX)

This map assigns your physical switches to **CH5 through CH10**.

| CRSF Channel | INAV Aux | Switch | Type | Function |
| :--- | :--- | :--- | :--- | :--- |
| **CH5** | AUX 1 | **SD** (Top-Right) | 2-Pos | **ARM** (Down = Armed) |
| **CH6** | AUX 2 | **SB** (Top-Left) | 3-Pos | **Flight Mode** (ANGLE / ACRO / MANUAL) |
| **CH7** | AUX 3 | **SC** (Top-Right) | 3-Pos | **Navigation** (RTH / OFF / LOITER) |
| **CH8** | AUX 4 | **SA** (Top-Left) | 2-Pos | **NAV LAUNCH** (Down = Active) |
| **CH9** | AUX 5 | **SE** (Left Button) | Momentary | **BEEPER** |
| **CH10** | AUX 6 | **SF** (Right Button) | Toggle* | **AUTO TUNE** (via Logical Switch) |

## 2. Unified `aux` CLI Block

```bash
# AUX 1 (CH5): ARM (SD Switch)
aux 0 0 0 1800 2100

# AUX 2 (CH6): Flight Modes (SB Switch)
# Low = ANGLE, Mid = ACRO (no mode), High = MANUAL
aux 1 1 1 900 1300
aux 2 12 1 1700 2100

# AUX 3 (CH7): Nav Modes (SC Switch)
# Low = RTH, Mid = OFF, High = POSHOLD (Loiter)
aux 3 10 2 900 1300
aux 4 11 2 1700 2100

# AUX 4 (CH8): NAV LAUNCH (SA Switch)
aux 5 36 3 1700 2100

# AUX 5 (CH9): BEEPER (SE Momentary)
aux 6 13 4 1700 2100

# AUX 6 (CH10): AUTO TUNE (SF Toggle)
aux 7 21 5 1700 2100

save
```

## 3. Finger-to-Position Visualization

* **Left Hand (Index/Middle):**
  * **SB (3-pos):** Primary flight stick. **Push Away** for ANGLE (Safe). **Center** for ACRO. **Pull Toward** for MANUAL.
  * **SA (2-pos):** Launch enable. Flick **Down** before you throw; flick **Up** once you're climbing.
  * **SE (Button):** Emergency beeper.
* **Right Hand (Index/Middle):**
  * **SC (3-pos):** The "Save Me" switch. **Push Away** for instant RTH. **Pull Toward** to Loiter.
  * **SD (2-pos):** The Arm switch.
  * **SF (Button):** The Auto Tune trigger.

## 4. EdgeTX "Sticky" Toggle for Auto Tune

1. **Logical Switches (L01):**
   * **Function:** `Sticky`
   * **V1:** `SF↓`
   * **V2:** `SF↓`
2. **Mixes (CH10):**
   * **Source:** `L01`
   * **Weight:** `100`

## 5. Design Notes & Conflicts

* **RTH Priority:** RTH (AUX 3 Low) overrides SB flight modes.
* **Manual Warning:** SB HIGH = no stabilization.
* **Launch Safety:** NAV LAUNCH on dedicated 2-pos (SA).
* **Airmode:** Firmware defaults per plane.
