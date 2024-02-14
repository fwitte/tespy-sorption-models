# Sorption component models in TESPy

This is a prototype for the implementation of sorption processes in [TESPy][].
Two models are included in the repository and validated with data from different
literature sources:

1. Refrigeration machine
2. Heat transformer

## Usage

Clone the repository and build a new `python3.11` environment. From the base
directory of the repository run

``` bash
pip install -r ./requirements.txt
```

to install the version specific requirements.

## Refrigeration machine

### Model

<figure>
<img src="./flowsheet.svg" class="align-center" />
</figure>

### Validation

The [validation][] folder contains the original data from literature. The
deviation between literature and TESPy values can be obtained by changing to
validation directory and running validation.py.

## Heat transformer

### Model

### Validation

## Citation

The state of this repository is archived via zenodo. If you are using the
TESPy model within your own research, you can refer to this model via the
zenodo doi: [10.5281/zenodo.6592257][].

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
  [validation]: ./validation/
