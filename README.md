# Sorption component models in TESPy

Example models of the absorption cycle components and working pairs of
[TESPy][] on the [feature/sorption-components][] branch: standalone absorbers,
desorbers and a rectifier, and closed single-effect absorption chillers with
LiBr-water and NH3-water.

## Contents

| File | Description |
|------|-------------|
| `libr_water_absorber.py` | `Absorber`: outlet enthalpy, mass flow, temperature and composition specifications, approach to equilibrium `td_eq` |
| `libr_water_absorber_cooled.py` | `CooledAbsorber` with cooling water: vapor mass flow, terminal temperature difference and heat flow specifications |
| `libr_water_desorber.py` | `Desorber`: the `vapor_state` options and outlet specifications |
| `libr_water_desorber_heated.py` | `HeatedDesorber` with heating water |
| `libr_water_chiller.py` | Closed single-effect LiBr-water chiller with solution heat exchanger, sweep of the generator temperature |
| `libr_water_reference.py` | Reference states of a single-effect cycle from the LiBr-water pair, inputs of the LiBr-water component examples |
| `nh3_water_absorber.py` | `Absorber` with NH3-water, the refrigerant vapor is a solution connection |
| `nh3_water_generator_rectifier.py` | `Desorber` and `Rectifier`: purification of the generator vapor, sweep of the refrigerant purity |
| `nh3_water_chiller.py` | Closed NH3-water chiller with rectifier, solution and refrigerant heat exchanger (CoolSolve Library CSL-0249), sweep of the evaporation temperature |
| `working_pair_properties.py` | Duehring chart of LiBr-water and bubble and dew lines of NH3-water, written to `working_pair_properties.svg` |
| `run_examples.py` | Runs all examples and reports the convergence of every solve |

## Modeling notes

- Solution streams are `SolutionConnection`s of a working pair, the mixing
  rule `"libr-water"` (Patek and Klomfar 2006, IAPWS-95 reference state) or
  `"nh3-water"` (IAPWS G4-01 on the kernel of the optional dependency teqp).
  Naming the pair on one solution connection of a circuit is sufficient.
- `xi` is the mass fraction of the key component: LiBr for LiBr-water, NH3 for
  NH3-water. Solution connections report `xi`, the vapor mass fraction `x`, the
  bubble point `T_bubble` and the subcooling `td_bubble`.
- With LiBr-water the vapor is pure water on a plain `Connection`, with
  NH3-water it is a `SolutionConnection`.
- The vapor leaving a desorber is in equilibrium with the entering solution by
  default (`vapor_state="inlet-equilibrium"`), alternatives are
  `"outlet-equilibrium"` and `"free"`.
- In a closed solution circuit the connection after the `CycleCloser` needs
  `fluid_balance=True`.
- The `Rectifier` does not impose its pressure on the reflux, the reflux
  returns to the generator through a `Merge` or gets a pressure
  specification.
- The refrigerant heat exchanger of CSL-0249 is infeasible (cold outlet above
  the hot inlet temperature): TESPy reproduces the reference state and warns
  about a cold side effectiveness above 1.

## Installation

Requires [uv][]. From the base directory of this repository:

``` bash
uv sync
uv run python run_examples.py
```

This installs TESPy from the `feature/sorption-components` branch on GitHub
together with teqp and matplotlib.

## Open tasks

- [x] Validate absorber and desorber implementations against literature data
  (Patek and Klomfar check values, CoolSolve Library CSL-0043 and CSL-0249 in
  the TESPy tests and benchmark)
- [x] Build a combined absorber/desorber cycle (single-effect absorption system)
- [x] Add a solution heat exchanger between rich/poor streams
- [x] Rectifier integration for ammonia-water working pairs
- [ ] Extend the combined cycle to include a cooling machine (compression chiller driven by the absorber heat)
- [ ] Crystallization check for LiBr-water
- [ ] Double-effect cycles

## MIT License

Copyright (c) Francesco Witte, Felix Irrgang, Mathias Hofmann

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.


  [TESPy]: https://github.com/oemof/tespy
  [feature/sorption-components]: https://github.com/oemof/tespy/tree/feature/sorption-components
  [uv]: https://docs.astral.sh/uv/
