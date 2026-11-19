# Sorption component models in TESPy

Example models of the absorption cycle components and working pairs of
[TESPy][] on the [feature/sorption-components][] branch: standalone absorbers,
desorbers and a rectifier, and closed single-effect absorption chillers with
LiBr-water and NH3-water.

> [!WARNING]
> The absorption cycle modeling in TESPy is experimental and not thoroughly
> tested yet, results and the API may change. Feedback is very welcome, please
> open an issue in the [TESPy repository][issues].

## Contents

| File | Description | References |
|------|-------------|------------|
| `libr_water_absorber.py` | `Absorber`: outlet enthalpy, mass flow, temperature and composition specifications, approach to equilibrium `td_eq` | [1], [2], [12] |
| `libr_water_absorber_cooled.py` | `CooledAbsorber` with cooling water: vapor mass flow, terminal temperature difference and heat flow specifications | [1], [2], [12] |
| `libr_water_desorber.py` | `Desorber`: the `vapor_state` options and outlet specifications | [1], [2], [12] |
| `libr_water_desorber_heated.py` | `HeatedDesorber` with heating water | [1], [2], [12] |
| `libr_water_chiller.py` | Closed single-effect LiBr-water chiller with solution heat exchanger, sweep of the generator temperature | [1], [2], [6], [8], [10], [12] |
| `libr_water_reference.py` | Reference states of a single-effect cycle from the LiBr-water pair, inputs of the LiBr-water component examples | [1], [2], [12] |
| `nh3_water_absorber.py` | `Absorber` with NH3-water, the refrigerant vapor is a solution connection | [3], [4], [5], [11] |
| `nh3_water_generator_rectifier.py` | `Desorber` and `Rectifier`: purification of the generator vapor, sweep of the refrigerant purity | [3], [4], [5], [11] |
| `nh3_water_chiller.py` | Closed NH3-water chiller with rectifier, solution and refrigerant heat exchanger, sweep of the evaporation temperature | [3], [4], [5], [7], [8], [9], [10], [11] |
| `custom_working_pair.py` | Custom working pair derived from LiBr-water with a limited equilibrium composition, registered as mixing rule and used in an absorber | [1], [2], [12] |
| `working_pair_properties.py` | Duehring chart of LiBr-water and bubble and dew lines of NH3-water, written to `working_pair_properties.svg` | [1]-[5], [11], [12] |
| `run_examples.py` | Runs all examples and reports the convergence of every solve | |

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

## References

Working pairs:

1. J. Pátek, J. Klomfar: A computationally effective formulation of the
   thermodynamic properties of LiBr-H2O solutions from 273 to 500 K over full
   composition range. International Journal of Refrigeration 29 (4), 2006,
   566-578. https://doi.org/10.1016/j.ijrefrig.2005.10.007 - LiBr-water pair
   `"libr-water"`.
2. W. Wagner, A. Pruß: The IAPWS formulation 1995 for the thermodynamic
   properties of ordinary water substance for general and scientific use.
   Journal of Physical and Chemical Reference Data 31 (2), 2002, 387-535.
   https://doi.org/10.1063/1.1461829 - water vapor and reference state of
   the LiBr-water pair (through CoolProp).
3. R. Tillner-Roth, D. G. Friend: A Helmholtz free energy formulation of the
   thermodynamic properties of the mixture {water + ammonia}. Journal of
   Physical and Chemical Reference Data 27 (1), 1998, 63-96.
   https://doi.org/10.1063/1.556015 - NH3-water pair `"nh3-water"`.
4. IAPWS G4-01: Guideline on the IAPWS Formulation 2001 for the Thermodynamic
   Properties of Ammonia-Water Mixtures. International Association for the
   Properties of Water and Steam, 2001. https://www.iapws.org - the
   formulation of [3] as adopted by IAPWS.
5. I. H. Bell, U. K. Deiters, A. M. M. Leal: Implementing an equation of state
   without derivatives: teqp. Industrial & Engineering Chemistry Research
   61 (17), 2022, 6010-6027. https://doi.org/10.1021/acs.iecr.2c00237 -
   Helmholtz energy kernel of the NH3-water pair.

Reference models:

6. CoolSolve Library [CSL-0043][csl-0043]: LiBr-water absorption chiller
   cycle with a solution heat exchanger, from the ULiège course Machines et
   systèmes thermiques (J. Lebrun, V. Lemort, S. Bertagnolio).
   `libr_water_chiller.py` uses its evaporator (5 degC), absorber (40 degC)
   and condenser (45 degC) temperatures; the generator temperature, the
   solution heat exchanger and the pump differ. Model
   [`libr_water_absorption_chiller.eescode`](https://github.com/IntSusEnergySystems/CoolSolve_Library/blob/main/models/refrigeration_heat_pumps/absorption/libr_water_absorption_chiller/libr_water_absorption_chiller.eescode),
   solution of the original EES file
   [`libr_water_absorption_chiller.sol`](https://github.com/IntSusEnergySystems/CoolSolve_Library/blob/main/models/refrigeration_heat_pumps/absorption/libr_water_absorption_chiller/libr_water_absorption_chiller.sol).
7. CoolSolve Library [CSL-0249][csl-0249]: single-effect ammonia-water
   absorption chiller with rectifier, the design point of
   `nh3_water_chiller.py` (identical inputs, same formulation and reference
   state). Model
   [`nh3h2o_absorption_chiller.eescode`](https://github.com/IntSusEnergySystems/CoolSolve_Library/blob/main/models/refrigeration_heat_pumps/absorption/nh3h2o_absorption_chiller/nh3h2o_absorption_chiller.eescode),
   CoolSolve solution
   [`nh3h2o_absorption_chiller.sol`](https://github.com/IntSusEnergySystems/CoolSolve_Library/blob/main/models/refrigeration_heat_pumps/absorption/nh3h2o_absorption_chiller/nh3h2o_absorption_chiller.sol).
   The TESPy test
   [`tests/test_models/test_absorption_chillers.py`](https://github.com/oemof/tespy/blob/feature/sorption-components/tests/test_models/test_absorption_chillers.py)
   checks the TESPy model against it.
8. K. E. Herold, R. Radermacher, S. A. Klein: Absorption Chillers and Heat
   Pumps. CRC Press, 1996 (2nd edition 2016) - standard single-effect cycles.

Software and model repositories:

9. [CoolSolve][] (MIT): open-source EES-compatible equation solver on
   CoolProp. Its implementation of IAPWS G4-01
   ([`src/nh3h2o.cpp`](https://github.com/CoolProp/CoolSolve/blob/main/src/nh3h2o.cpp),
   phase equilibrium and flashes in
   [`src/nh3h2o_flash.cpp`](https://github.com/CoolProp/CoolSolve/blob/main/src/nh3h2o_flash.cpp))
   computed the CSL-0249 solution [7], against which the NH3-water pair of
   TESPy is validated.
10. [CoolSolve Library][] (MIT): curated library of EES models for CoolSolve,
    source of the reference models [6] and [7] with their stored solutions.
11. [teqp][] (NIST): C++ library with Python interface for equations of state
    with automatic differentiation, kernel [5] of the NH3-water pair.
12. [CoolProp][] (MIT): water and steam properties after IAPWS-95 [2].

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
  [CoolSolve]: https://github.com/CoolProp/CoolSolve
  [CoolSolve Library]: https://github.com/IntSusEnergySystems/CoolSolve_Library
  [teqp]: https://github.com/usnistgov/teqp
  [CoolProp]: https://github.com/CoolProp/CoolProp
  [csl-0043]: https://github.com/IntSusEnergySystems/CoolSolve_Library/tree/main/models/refrigeration_heat_pumps/absorption/libr_water_absorption_chiller
  [csl-0249]: https://github.com/IntSusEnergySystems/CoolSolve_Library/tree/main/models/refrigeration_heat_pumps/absorption/nh3h2o_absorption_chiller
  [issues]: https://github.com/oemof/tespy/issues
