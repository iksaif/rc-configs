# rc-configs

Personal RC flight-controller configurations, tracked in git so I can sync
between machines, diff across firmware versions, and not lose a working
tune to a flash corruption.

Public repo but mostly for my own use — nothing here is supported or
warrantied. Pick through at your own risk.

## Fleet

| Plane     | Airframe                                | Status              | FC target                |
|-----------|-----------------------------------------|---------------------|--------------------------|
| Baloo     | FliteTest Sea Duck (foam, amphib twin)  | Not flown yet       | `SPEEDYBEEF405WING`      |
| Swordfish | AtomRC Swordfish 1200 mm (twin V-tail)  | **Flies — reference tune** | `ATOMRCF405NAVI` |
| Dolphin   | AtomRC Dolphin Pro 800 mm (elevon pusher)| Not flown yet      | `ATOMRCF405NAVI_DELUX`   |

All three run **INAV 9.0.1**, CRSF link (TBS Crossfire / ExpressLRS
compatible), AVATAR HD video, and share a single harmonized OSD + aux-mode
map so I don't have to re-learn them when I swap airframes.

Each plane folder keeps the latest dump plus archive versions back to
whichever firmware the plane was on at purchase.

## Layout

```
planes/
├── baloo/         # FT Sea Duck
├── swordfish/     # AtomRC Swordfish (old gen)
└── dolphin/       # AtomRC Dolphin Pro
tango2/
├── model5.plane.yaml          # TBS Tango 2 / FreedomTX model config
├── model-schema.md            # schema for the YAML above
└── design/                    # mode-layout design docs
```

Each plane folder: the **most recent filename** (highest `INAV_<ver>_cli_<date>` suffix) is the live config. Older files are preserved for history.

## Applying a config

1. Open the INAV Configurator, connect to the FC, go to the **CLI** tab.
2. Paste the contents of the `.txt` verbatim.
3. Type `save` (the last line of every dump already does this) and wait
   for reboot.

For a fresh flash: start from `AtomRC Swordfish Diff All (USE WITH
CAUTION - UNTUNED).txt` (factory baseline) or the equivalent stock dump
for that board, then paste one of my tuned configs on top.

## Unified aux-mode map (all three planes)

Tango 2 switches → INAV modes:

| Tango 2 switch     | Position | Mode                     |
|--------------------|----------|--------------------------|
| SD (top-right 2-pos)| HIGH    | ARM                      |
| SB (top-left 3-pos) | LOW     | ANGLE                    |
| SB                 | MID      | (no flight-mode aux = ACRO fallback) |
| SB                 | HIGH     | MANUAL                   |
| SC (top-right 3-pos)| LOW     | NAV POSHOLD (loiter)     |
| SC                 | MID      | —                        |
| SC                 | HIGH     | NAV RTH                  |
| SA (top-left 2-pos) | HIGH    | NAV LAUNCH (opt-in)      |
| SE (shoulder)      | press    | BEEPER (hold)            |
| SF (shoulder)      | toggle   | AUTO TUNE (via Logical Switch L01, sticky) |

Channel mapping (Tango 2 mixer → CRSF):

| Channel | Source | Role       |
|---------|--------|------------|
| CH5     | SD     | ARM        |
| CH6     | SB     | Flight mode|
| CH7     | SC     | NAV        |
| CH8     | SA     | Launch     |
| CH9     | L01    | Auto tune  |
| CH10    | SE     | Beeper     |

Full rationale + alternate layouts (one per LLM agent) in
[`tango2/design/`](./tango2/design/).

## Unified OSD layout (AVATAR HD60, 60×22)

```
Top-left:     sats · flymode · craft name
Top-center:   heading strip · flytime
Top-right:    home arrow · home distance
Crosshair row: GPS speed · AH · altitude · VSI
Sidebar tapes: speed (left) · altitude (right)
Bottom-left:  battery V · cell V · mAh · efficiency
Bottom-center:messages
Bottom-right: RSSI% · CRSF LQ
Bottom row:   wind · trip dist · (Dolphin only: g-force)
```
