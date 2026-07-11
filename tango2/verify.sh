#!/usr/bin/env bash
# Sanity-check script: bake model5.plane.yaml → model5.bin using tango-util
# and diff the produced binary against the on-device dump so we can catch
# corruption before flashing to the radio.
#
# Usage:  ./verify.sh [/path/to/sd/root]
# Defaults to ~/dev/Tango/Tango/D (the user's dump). Slot 4 is model5.bin.
set -euo pipefail

SD_ROOT="${1:-$HOME/dev/Tango/Tango/D}"
BIN_ORIG="$SD_ROOT/MODELS/model5.bin"
YAML_IN="$(dirname "$0")/model5.plane.yaml"
BIN_OUT="$(dirname "$0")/model5.bin"
TANGO_UTIL="$HOME/dev/tango-util/target/release/tango-util"

if [ ! -x "$TANGO_UTIL" ]; then
    TANGO_UTIL="$HOME/dev/tango-util/target/debug/tango-util"
fi
if [ ! -x "$TANGO_UTIL" ]; then
    echo "ERROR: tango-util binary not found under ~/dev/tango-util/target/" >&2
    exit 1
fi

echo "== baking YAML → .bin =="
"$TANGO_UTIL" --apply-yaml "$SD_ROOT" 4 "$YAML_IN" "$BIN_OUT"

echo
echo "== sanity checks =="
python3 - <<PY
import json, subprocess, sys, os

orig = "$BIN_ORIG"
new  = "$BIN_OUT"
cli  = os.path.expanduser("$TANGO_UTIL").replace("tango-util", "tango-cli")
if not os.path.exists(cli):
    cli = os.path.expanduser("~/dev/tango-util/target/debug/tango-cli")

with open(orig, 'rb') as f: a = f.read()
with open(new,  'rb') as f: b = f.read()

fail = 0
def check(name, ok, detail=""):
    global fail
    print(f"  [{'OK' if ok else 'FAIL'}] {name}{': ' + detail if detail else ''}")
    if not ok: fail += 1

check("size == 6443", len(a) == len(b) == 6443, f"old={len(a)} new={len(b)}")
check("header otxD/0xdb/'M'",
      a[:4] == b[:4] == b"otxD" and a[4] == b[4] == 0xdb and a[5] == b[5] == 0x4d)

diffs = sum(1 for x, y in zip(a, b) if x != y)
check(f"byte diff < 5% of file ({diffs} bytes, {100*diffs/len(a):.2f}%)", diffs < len(a) * 0.05)

new_j = json.loads(subprocess.check_output([cli, "model", new]))
ls0 = new_j["logical_switches"][0]
check("L01 = STICKY(SF↓, SF↓)",
      ls0["func"] == 18 and ls0["v1_raw"] == 18 and ls0["v2"] == 18,
      f"func={ls0['func']} v1={ls0['v1_raw']} v2={ls0['v2']}")
mx8 = new_j["mixers"][8]
check("CH9 mixer src = L01 (95)", mx8["src_raw"] == 95 and mx8["dest_ch"] == 8)
t0 = new_j["timers"][0]
check("Timer1 = SA↓ (mode 7), per-flight, minute beep",
      t0["mode"] == 7 and t0["persistent"] == 1 and t0["minute_beep"] == 1)
check("switch warnings SA-SD active, SE/SF disabled",
      new_j["switch_warning_state"] == 0 and new_j["switch_warning_enable"] == 0b110000,
      f"state={new_j['switch_warning_state']:#x} enable={new_j['switch_warning_enable']:#b}")

expected_cf = [(0,'armed'), (1,'manmod'), (2,'angmod'), (3,'acrmod'),
               (4,'navrth'), (5,'loiter'), (6,'takeof'), (7,'disarm'),
               (8,'gyroon'), (9,'gyroof')]
cfs = new_j["custom_functions"]
for i, want in expected_cf:
    name = bytes(c for c in cfs[i]["payload"][:6] if c).decode("ascii", "replace")
    check(f"CF{i+1} play_name == {want!r}", name == want, f"got {name!r}")

# L01 special-function switches
check("CF9 fires on L01 active (swsrc 27)", cfs[8]["swtch_raw"] == 27)
check("CF10 fires on !L01 (swsrc 485 = -27 as 9-bit)", cfs[9]["swtch_raw"] == 485)

print()
print(f"== result: {'all OK' if fail == 0 else f'{fail} FAILURE(s)'} ==")
sys.exit(1 if fail else 0)
PY
