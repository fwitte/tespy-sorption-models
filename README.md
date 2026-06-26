# Sorption component models in TESPy

This repository is a development sandbox for the sorption components
(`Absorber`, `Desorber`) being implemented in [TESPy][] on the
[feature/sorption-components][] branch. It contains standalone example
scripts and reference utilities used during development and validation.

## Contents

| File | Description |
|------|-------------|
| `example_absorber.py` | Standalone absorber network - exercises several specification combinations (vapour inlet, poor/rich solution, LiBr mixture) |
| `example_desorber.py` | Standalone desorber network - mirrors the absorber examples for the desorber component |
| `sorption_reference.py` | CoolProp-based reference functions for LiBr saturation pressure/concentration, used as fixed-point inputs in the example scripts |

## Installation

Requires [uv][]. From the base directory of this repository:

``` bash
uv sync
```

This installs TESPy directly from the `feature/sorption-components` branch on
GitHub together with all other dependencies.

## Open tasks

- [ ] Validate absorber and desorber implementations against literature data
- [ ] Build a combined absorber/desorber cycle (single-effect absorption system)
- [ ] Extend the combined cycle to include a cooling machine (compression chiller driven by the absorber heat)
- [ ] Add a solution heat exchanger between rich/poor streams
- [ ] Investigate rectifier/condenser integration for ammonia-water working pairs

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
