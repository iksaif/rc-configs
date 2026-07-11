# docs/ — reference material

Enough context for a future agent (or future me) to pick up work in this
repo without external lookups. Everything here is reference-only — the
live configs live under [`../planes/`](../planes/) and [`../tango2/`](../tango2/).

## Contents

- **[`inav/`](./inav/)** — INAV 9.0 CLI reference: full `settings-9.0.yaml`,
  box-id table, OSD item table, command list, feature names, aux-format
  cheat sheet, and a copy of INAV's upstream `Cli.md`. See
  `inav/README.md` for provenance and GPL attribution.
- **[`tango2/`](./tango2/)** — schema for the TBS Tango 2 / FreedomTX
  `model5.plane.yaml` config (both human-readable `.md` and machine
  `.json` variants).

## Using this from a fresh agent session

When starting a Claude / ChatGPT / Gemini session to modify these configs,
paste a short brief and point it at this folder. Minimum useful context:

```
Please help me modify the INAV configurations under ./planes/.

Reference material lives under ./docs/. In particular:
- ./docs/inav/settings-9.0.yaml — every valid `set` key, type, range
- ./docs/inav/boxIds.json       — flight-mode ids for `aux` lines
- ./docs/inav/osdItems.json     — ordinals for `osd_layout` lines
- ./docs/inav/commands.json     — CLI command list + arg signatures
- ./docs/inav/features.json     — valid `feature` names
- ./docs/inav/cli-aux-format.md — aux-line format + mode interactions
- ./docs/inav/Cli.md            — INAV's own CLI reference
- ./docs/tango2/model-schema.md — schema for the Tango 2 yaml

The repo's README has the fleet overview + the unified aux and OSD maps.
```
