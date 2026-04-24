# Tango 2 + INAV mode layout — proposal (ChatGPT)

## 1) Tango 2 channel map

* **CH5 / AUX1 = SD** → **ARM**
* **CH6 / AUX2 = SB** → **Flight mode**
* **CH7 / AUX3 = SC** → **NAV mode stack**
* **CH8 / AUX4 = SA** → **NAV LAUNCH**
* **CH9 / AUX5 = LS1** → **AUTO TUNE** (LS1 = sticky logical switch toggled by momentary SF)
* **CH10 / AUX6 = SE** → **BEEPER** (momentary)

## 2) Switch meaning

### SB — top-left 3-pos = flight mode

* **SB↑ = ANGLE**
* **SB– = ACRO** (no aux active = ACRO fallback)
* **SB↓ = MANUAL**

### SC — top-right 3-pos = NAV

* **SC↑ = NAV POSHOLD / LOITER**
* **SC– = no NAV override**
* **SC↓ = NAV RTH**  ← RTH on down = natural panic flip

### SD — top-right 2-pos = ARM

* **SD↑ = disarmed**
* **SD↓ = armed**

### SA — top-left 2-pos = NAV LAUNCH

* **SA↑ = launch off**
* **SA↓ = launch armed**

### SF — lower-right momentary = AUTO TUNE toggle

Drives sticky logical switch LS1 feeding CH9.

### SE — lower-left momentary = BEEPER

## 3) Pasteable INAV `aux` block

Using 900-1200 / 1300-1700 / 1800-2100 windows:

```
aux 0 0  0 1800 2100    # ARM         on AUX1 / CH5 / SD high
aux 1 1  1  900 1200    # ANGLE       on AUX2 / CH6 / SB low
aux 2 12 1 1800 2100    # MANUAL      on AUX2 / CH6 / SB high
aux 3 11 2  900 1200    # NAV POSHOLD on AUX3 / CH7 / SC low
aux 4 10 2 1800 2100    # NAV RTH     on AUX3 / CH7 / SC high
aux 5 36 3 1800 2100    # NAV LAUNCH  on AUX4 / CH8 / SA high
aux 6 21 4 1800 2100    # AUTO TUNE   on AUX5 / CH9 / LS1 high
aux 7 13 5 1800 2100    # BEEPER      on AUX6 / CH10 / SE high
```

## 4) Finger picture

### Left hand
* **SB** = "how I fly": up=ANGLE, mid=ACRO, down=MANUAL
* **SA** = "only before a hand-launch": down/on = NAV LAUNCH

### Right hand
* **SC** = "automation rescue": up=LOITER, mid=off, down=RTH
* **SD** = ARM only

### Shoulders
* **SE** = hold for BEEPER
* **SF** = tap to toggle AUTO TUNE

## 5) EdgeTX logical-switch sketch for AUTO TUNE

Don't put AUTO TUNE on a raw momentary. Use SF to toggle a sticky logical switch, feed to CH9.

* **L01 = Sticky(SF, SF)** → first press ON, next press OFF
* **CH9 mix**: source = L01, weight 100

**Strong recommendation:** add voice callouts ("Auto tune on" / "Auto tune off"). You really don't want to forget it's active.

## 6) Conflicts / gotchas

* **RTH vs LOITER**: opposite ends of same 3-pos, no overlap.
* **NAV overrides MANUAL/ACRO**: expected — keeps RTH as true rescue.
* **NAV LAUNCH re-entry** (biggest operational gotcha): SA left on in flight re-enters launch. Operational rule: SA on ONLY for launch setup, return to off once climbing.
* **AUTO TUNE**: only at altitude, calm air, SC centered (no nav active). Not during launch/landing/LOITER/RTH.

## 7) Beyond the asked list

* **BEEPER: yes** — momentary is the perfect place.
* **PREARM: optional, not in baseline** — Tango 2 is switch-limited if you also want dedicated ARM/LAUNCH/2× 3-pos/BEEPER/AUTOTUNE. Skip PREARM for now. If you later want it more than dedicated launch, reclaim SA for PREARM and move LAUNCH to a logical condition.
* **AIRMODE aux: no** — set per-airframe in config.
* **Failsafe aux: no** — stays in RX/FC config.

## 8) Final map

* **SD** = ARM
* **SB** = ANGLE / ACRO / MANUAL
* **SC** = LOITER / OFF / RTH
* **SA** = LAUNCH
* **SF** = AUTO TUNE toggle via LS
* **SE** = BEEPER
