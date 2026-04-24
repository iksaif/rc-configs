# INAV reference data — `docs/inav/`

Files in this folder are pinned snapshots from the
**[iNavFlight/inav](https://github.com/iNavFlight/inav)** project, tag
`9.0.1`. They're kept here so this repo is self-contained — a future agent
(human or LLM) can do meaningful work on the plane configs without needing
the INAV source tree.

## Files and provenance

| File                  | Source (in the INAV tree)                           | Purpose                                      |
|-----------------------|-----------------------------------------------------|----------------------------------------------|
| `settings-9.0.yaml`   | `src/main/fc/settings.yaml` @ tag 9.0.1             | Authoritative list of every `set` key with type, range, default, enum table, and description. |
| `boxIds.json`         | Extracted from `src/main/fc/fc_msp_box.c` + `src/main/io/piniobox.h` | Flight-mode permanent-id → name table, used in `aux` lines. |
| `osdItems.json`       | Extracted from `osd_items_e` in `src/main/io/osd.h` | OSD element ordinal → name table, used in `osd_layout` lines. |
| `commands.json`       | Extracted from `CLI_COMMAND_DEF(...)` macros in `src/main/fc/cli.c` | CLI commands, their descriptions, and arg-help strings. |
| `features.json`       | Extracted from `featureNames[]` in `src/main/fc/cli.c` | Valid names for `feature` lines.             |
| `Cli.md`              | Verbatim from `docs/Cli.md` @ tag 9.0.1             | Human-readable CLI reference.                |
| `cli-aux-format.md`   | My own quick-reference for the `aux` command format and INAV mode interaction semantics. | Complement to `Cli.md` for the aux-specific bits. |

## Regenerating

The JSON files were produced by the scripts bundled with my INAV CLI VS
Code extension (see [`iksaif/inav-cli-vscode`](https://github.com/iksaif/inav-cli-vscode),
`scripts/add-version.sh`). To refresh against a new INAV release:

```sh
git -C ~/dev/inav fetch --depth 1 origin tag <NEW_TAG>
# in the inav-cli-vscode repo:
scripts/add-version.sh <NEW_TAG> <major.minor>
# then copy schemas/<major.minor>/*.json and settings.yaml back into this folder
```

## Licensing

The extracted files and `Cli.md` come from INAV, which is licensed
**GPL-3.0**. They are redistributed here under that same license.
The rest of this repository (plane configs, Tango 2 model, readmes) is
MIT-licensed (see `/LICENSE` at the repo root).

Original INAV copyright notice: `Copyright © Konstantin Sharlaimov and
the iNavFlight contributors. See https://github.com/iNavFlight/inav for
the full source, LICENSE, and author list.`
