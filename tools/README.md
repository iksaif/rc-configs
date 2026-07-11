# tools/ — pre-tune calculator

`pretune.py` derives a safe *starting* INAV config for a fixed-wing from its
physical shape, mass and power — instead of guessing or blindly copying
another plane. Swordfish (the flight-proven "reference tune") is the
calibration anchor; the other planes are scaled from it by dimensional
similarity, so the unknown aero coefficients cancel in the ratios.

## Why bother — autotune doesn't set most of this

INAV's fixed-wing autotune only touches roll/pitch **FF + P**. Everything
else — cruise speed, reference airspeed, throttle band, loiter radius, bank
limit, launch, CG — it never sets, yet those are exactly what stalls a maiden
RTH or fails launch detection. The calculator's real payoff is those
physics-exact numbers; the PID output is just a sane seed autotune refines.

## Use

```sh
./pretune.py                    # all planes: rationale table + CLI diff
./pretune.py dolphin            # one plane
./pretune.py --diff-only baloo  # just the paste-able `set` block
./pretune.py > /tmp/pretune.txt # capture for review
```

It **never edits the plane dumps** — review the CLI block, paste what you
trust into the Configurator CLI, `save`, then fly.

Output confidence:

- `●` **physics-exact** — from mass/area/geometry only (cruise speed, loiter
  radius, bank, CG target). Trust these.
- `○` **similarity-scaled** — PID/rates seeded from Swordfish × plant-gain and
  agility ratios. A safe starting point; one autotune flight dials them in.
  For a maiden on an untested plane, consider starting rates ~30% lower.

## Inputs — `planes/*.yaml`

One file per plane. Fields flagged `ESTIMATE` in the comments only affect the
amber PID/CG scaling — refine them (measure wing area, surface areas, static
thrust) to tighten those, but the green nav numbers are already solid.
`swordfish.yaml` additionally carries `anchor_params` (its known-good values);
edit those only if you re-tune Swordfish itself.

Physics anchors: `Vstall = √(2mg/ρS·CLmax)`, cruise = 1.35·Vstall, loiter
`R = V²/(g·tanφ)`, bank capped to hold a 15% stall margin in the turn,
climb `sinγ = T/W − 1/(L/D)` with a 0.6 forward-thrust derate.
