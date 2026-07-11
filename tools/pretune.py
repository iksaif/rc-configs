#!/usr/bin/env python3
"""Static pre-tune calculator for INAV fixed-wing planes.

Derives a safe starting configuration from airframe geometry, mass and power
instead of guessing or blindly copying another plane. Two kinds of output:

  GREEN  parameters computed directly from physics (cruise speed, loiter
         radius, bank limit, launch, CG target). These are the real win —
         autotune never touches them, and they're what stalls a maiden RTH.

  AMBER  roll/pitch/yaw PID + rates, scaled by dimensional *similarity* from
         a flight-proven anchor plane (Swordfish). A sane starting point;
         one autotune flight still refines the final numbers.

Usage:
    ./pretune.py                      # all planes, rationale + CLI diff
    ./pretune.py dolphin              # one plane
    ./pretune.py --diff-only baloo    # just the paste-able CLI block
    ./pretune.py > /tmp/pretune.txt   # capture for review (never edits dumps)

Inputs live in tools/planes/*.yaml. Nothing here mutates the plane .txt dumps;
review the CLI block, then paste what you trust into the Configurator.
"""
from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("pretune: needs PyYAML  ->  python3 -m pip install pyyaml")

G = 9.81
PLANES_DIR = Path(__file__).parent / "planes"

# ANSI colour, disabled when not a TTY so redirected output stays clean.
_TTY = sys.stdout.isatty()
def _c(code: str, s: str) -> str:
    return f"\033[{code}m{s}\033[0m" if _TTY else s
GREEN = lambda s: _c("32", s)
AMBER = lambda s: _c("33", s)
BOLD  = lambda s: _c("1", s)
DIM   = lambda s: _c("2", s)


class Plane:
    """One airframe plus every physical quantity we derive from it."""

    def __init__(self, spec: dict):
        self.spec = spec
        self.name = spec["name"]
        self.config = spec["config"]
        self.anchor = spec.get("anchor", False)

        g = spec["geometry"]
        self.b = g["span_mm"] / 1000.0                 # span, m
        self.S = g["wing_area_dm2"] / 100.0            # wing area, m^2
        self.mac = g["mac_mm"] / 1000.0                # mean aero chord, m
        self.AR = self.b ** 2 / self.S                 # aspect ratio

        self.m = spec["mass"]["auw_g"] / 1000.0        # flying mass, kg
        self.cg_pct = spec["mass"]["cg_pct_mac"]

        a = spec["aero"]
        self.cl_max = a["cl_max"]
        self.cd0 = a["cd0"]
        self.e = a["oswald"]
        self.rho = a["rho"]

        p = spec["power"]
        self.cells = p["cells"]
        self.capacity = p["capacity_mah"]
        self.thrust_N = p["static_thrust_g"] / 1000.0 * G

        self.surf = spec["surfaces"]
        self._aero()

    # --- core aerodynamics (GREEN: depends only on m, S, CL, geometry) ---
    def _aero(self):
        w = self.m * G
        self.wing_loading = self.m * 1000 / (self.S * 100)   # g/dm^2
        # Stall: level, 1g. Cruise: 1.35 * stall is a safe fast-cruise anchor.
        self.v_stall = math.sqrt(2 * w / (self.rho * self.S * self.cl_max))
        self.v_cruise = 1.35 * self.v_stall
        self.q_cruise = 0.5 * self.rho * self.v_cruise ** 2   # dynamic pressure

        # Cruise drag and lift/drag ratio.
        cl_cruise = w / (self.q_cruise * self.S)
        cd = self.cd0 + cl_cruise ** 2 / (math.pi * self.e * self.AR)
        self.drag_cruise = self.q_cruise * self.S * cd
        self.ld_cruise = cl_cruise / cd

        # A prop keeps only ~60% of its static thrust by cruise speed, and
        # thrust ≈ static·throttle². So throttle to hold level flight:
        thrust_fwd = self.thrust_N * 0.60
        self.cruise_thr_frac = min(0.95, math.sqrt(self.drag_cruise / thrust_fwd))
        # Steady full-throttle climb:  sin γ = T/W − 1/(L/D).
        sin_climb = thrust_fwd / w - 1.0 / self.ld_cruise
        self.climb_deg = max(0.0, math.degrees(math.asin(min(0.6, sin_climb))))

        # Inertia proxies (∝, constants cancel in ratios).
        self.I_roll = self.m * self.b ** 2
        self.I_pitch = self.m * (self.spec["geometry"]["length_mm"] / 1000.0) ** 2

        # Control-power proxies: aero moment per unit stick ∝ area·arm·deflection.
        self.cp_roll = self._cp("roll")
        self.cp_pitch = self._cp("pitch")

        # Max bank so the 1g-stall margin still holds at cruise:
        #   v_cruise >= 1.15 * v_stall / sqrt(cos φ)   ->   solve for φ.
        ratio = (self.v_cruise / (1.15 * self.v_stall)) ** 2
        cos_phi = min(1.0, 1.0 / ratio) if ratio > 0 else 1.0
        self.bank_deg = min(45.0, math.degrees(math.acos(cos_phi)))
        # Min coordinated-turn radius at that bank.
        self.turn_radius = self.v_cruise ** 2 / (G * math.tan(math.radians(self.bank_deg)))

    def _cp(self, axis: str):
        s = self.surf.get(axis)
        if not isinstance(s, dict):
            return None
        return (s["area_dm2"] / 100.0) * (s["arm_mm"] / 1000.0) * math.radians(s["max_defl_deg"])


def gain_ratio(new: Plane, ref: Plane, axis: str):
    """Similarity factor for FF/P/D on an axis.

    Both feedforward and P invert the plant gain (aero_moment / inertia), so
    to hold the closed-loop response constant across airframes:

        gain_new / gain_ref = (I_new/I_ref) * (q_ref/q_new) * (cp_ref/cp_new)

    Unknown coefficients (CL_δ, servo geometry, air) cancel because they sit
    in both cp terms. Returns None if we lack a control-power estimate.
    """
    I = new.I_roll if axis == "roll" else new.I_pitch
    Iref = ref.I_roll if axis == "roll" else ref.I_pitch
    cp = new.cp_roll if axis == "roll" else new.cp_pitch
    cpref = ref.cp_roll if axis == "roll" else ref.cp_pitch
    if not cp or not cpref:
        return None
    return (I / Iref) * (ref.q_cruise / new.q_cruise) * (cpref / cp)


def rate_ratio(new: Plane, ref: Plane, axis: str):
    """Agility factor for a stick-rate limit ∝ control_power / inertia."""
    I = new.I_roll if axis == "roll" else new.I_pitch
    Iref = ref.I_roll if axis == "roll" else ref.I_pitch
    cp = new.cp_roll if axis == "roll" else new.cp_pitch
    cpref = ref.cp_roll if axis == "roll" else ref.cp_pitch
    if not cp or not cpref:
        return None
    return (cp / I) / (cpref / Iref)


class Row:
    __slots__ = ("key", "val", "unit", "why", "green")
    def __init__(self, key, val, unit, why, green):
        self.key, self.val, self.unit, self.why, self.green = key, val, unit, why, green


def compute(plane: Plane, ref: Plane) -> list[Row]:
    rows: list[Row] = []
    G_, A_ = True, False

    # --- GREEN: cruise / nav / launch, from physics ---
    vc = round(plane.v_cruise * 100)          # cm/s for INAV
    rows.append(Row("nav_fw_cruise_speed", vc, "cm/s",
                    f"1.35·Vstall ({plane.v_stall:.1f} m/s) = {plane.v_cruise:.1f} m/s", G_))
    rows.append(Row("fw_reference_airspeed", vc, "cm/s", "= cruise speed", G_))

    rows.append(Row("nav_fw_bank_angle", round(plane.bank_deg), "deg",
                    f"keeps 15% stall margin in the turn (WL {plane.wing_loading:.0f} g/dm²)", G_))
    rows.append(Row("nav_fw_loiter_radius", round(plane.turn_radius * 100), "cm",
                    f"V²/(g·tan {round(plane.bank_deg)}°) so loiter can't stall", G_))

    cruise_pwm = round(1000 + plane.cruise_thr_frac * 1000)
    rows.append(Row("nav_fw_cruise_throttle", cruise_pwm, "pwm",
                    f"level drag {plane.drag_cruise:.1f} N ≈ {plane.cruise_thr_frac*100:.0f}% thrust", A_))
    rows.append(Row("nav_fw_min_throttle", max(1150, cruise_pwm - 250), "pwm", "cruise − margin", A_))
    rows.append(Row("nav_fw_max_throttle", 1850, "pwm", "climb/headroom cap", A_))

    launch_climb = max(15, min(35, round(plane.climb_deg)))
    rows.append(Row("nav_fw_launch_climb_angle", launch_climb, "deg",
                    f"best steady climb ≈ {plane.climb_deg:.0f}° (T/W-limited)", G_))
    if plane.config == "conventional":
        rows.append(Row("nav_fw_launch_max_angle", 45, "deg", "ROG/gentle launch; not a chuck", A_))
    else:
        rows.append(Row("nav_fw_launch_max_angle", 45, "deg", "hand-launch detection window", A_))
    rows.append(Row("nav_fw_launch_thr", 1700, "pwm", "brisk launch throttle", A_))

    rows.append(Row("battery_capacity", plane.capacity, "mAh", "for accurate mAh-used OSD", G_))

    # --- AMBER: PID + rates, similarity-scaled from the anchor ---
    ap = ref.spec["anchor_params"]
    for axis, keys in (("roll", ("fw_ff_roll", "fw_p_roll", "fw_d_roll")),
                       ("pitch", ("fw_ff_pitch", "fw_p_pitch", "fw_d_pitch"))):
        gr = gain_ratio(plane, ref, axis)
        if gr is None:
            continue
        for k in keys:
            if k in ap:
                rows.append(Row(k, max(1, round(ap[k] * gr)), "",
                                f"{ap[k]} (Swordfish) × {gr:.2f} plant-gain ratio", A_))
        rr = rate_ratio(plane, ref, axis)
        rk = f"{axis}_rate"
        if rr is not None and rk in ap:
            val = max(4, min(40, round(ap[rk] * math.sqrt(rr))))  # sqrt: damp the swing
            rows.append(Row(rk, val, "deg/s·2",
                            f"{ap[rk]} × √{rr:.2f} agility ratio", A_))

    # --- CG target (GREEN-ish): tail-volume neutral point estimate ---
    if plane.config in ("conventional", "vtail") and isinstance(plane.surf.get("pitch"), dict):
        St = plane.surf["pitch"]["area_dm2"] / 100.0
        lt = plane.surf["pitch"]["arm_mm"] / 1000.0
        Vh = (lt * St) / (plane.mac * plane.S)          # horizontal tail volume
        # NP ≈ wing AC (25%) + tail contribution; SM target 8–12% MAC.
        np_pct = 25 + min(35, Vh * 100 * 0.9)
        cg_target = round(np_pct - 10)
        rows.append(Row("# CG target", f"{cg_target}% MAC", "",
                        f"NP≈{np_pct:.0f}% (tail vol {Vh:.2f}) − 10% static margin", G_))
    elif plane.config == "elevon":
        rows.append(Row("# CG target", "15–18% MAC", "",
                        "delta/elevon: fwd CG + reflex; verify by glide test", G_))

    return rows


def render(plane: Plane, ref: Plane, rows: list[Row], diff_only: bool):
    if not diff_only:
        print(BOLD(f"\n═══ {plane.name}  ({plane.config}, {plane.config != ref.config and 'scaled from Swordfish' or 'ANCHOR'}) ═══"))
        print(DIM(f"    span {plane.b*1000:.0f} mm · {plane.m:.2f} kg · WL {plane.wing_loading:.0f} g/dm² · "
                  f"Vstall {plane.v_stall:.1f} / Vcruise {plane.v_cruise:.1f} m/s · AR {plane.AR:.1f}"))
        print(f"\n    {'PARAMETER':<26}{'VALUE':>9}  {'':<6} WHY")
        for r in rows:
            tag = GREEN("●") if r.green else AMBER("○")
            unit = f"{r.unit}" if r.unit else ""
            print(f"  {tag} {r.key:<26}{str(r.val):>9}  {unit:<6} {DIM(r.why)}")
        print(DIM(f"\n    {GREEN('●')} physics-exact   {AMBER('○')} similarity-scaled starting point (autotune refines)"))

    # Paste-able CLI block (skips comment/CG rows).
    print(f"\n# --- pretune diff: {plane.name}  (review before pasting) ---")
    for r in rows:
        if r.key.startswith("#"):
            print(f"#   {r.key[2:]}: {r.val}  ({r.why})")
        else:
            print(f"set {r.key} = {r.val}")
    print()


def load(name: str) -> dict:
    f = PLANES_DIR / f"{name}.yaml"
    if not f.exists():
        sys.exit(f"pretune: no spec for '{name}' at {f}")
    return yaml.safe_load(f.read_text())


def main():
    ap = argparse.ArgumentParser(description="Static INAV fixed-wing pre-tune calculator")
    ap.add_argument("planes", nargs="*", help="plane names (default: all)")
    ap.add_argument("--diff-only", action="store_true", help="print only the CLI block")
    args = ap.parse_args()

    ref = Plane(load("swordfish"))

    names = args.planes or sorted(p.stem for p in PLANES_DIR.glob("*.yaml"))
    for name in names:
        plane = Plane(load(name))
        if plane.anchor and len(names) > 1:
            continue                       # don't re-tune the anchor in a full run
        render(plane, ref, compute(plane, ref), args.diff_only)


if __name__ == "__main__":
    main()
