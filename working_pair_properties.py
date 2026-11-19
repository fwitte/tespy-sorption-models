"""Property diagrams of the working pairs.

- LiBr-water: Duehring chart, the vapor pressure of the solution over its
  temperature for lines of constant LiBr mass fraction.
- NH3-water: bubble and dew point temperatures over the NH3 mass fraction at
  the evaporator and condenser pressure of the NH3-water chiller (requires
  the optional dependency teqp).

The figures are written to working_pair_properties.svg.

References
----------
- Patek and Klomfar (2006), https://doi.org/10.1016/j.ijrefrig.2005.10.007:
  LiBr-water pair.
- Wagner and Pruss (2002), https://doi.org/10.1063/1.1461829: IAPWS-95 water
  vapor and reference state, evaluated with CoolProp,
  https://github.com/CoolProp/CoolProp.
- Tillner-Roth and Friend (1998), https://doi.org/10.1063/1.556015, adopted as
  IAPWS G4-01: NH3-water pair.
- Bell, Deiters and Leal (2022), https://doi.org/10.1021/acs.iecr.2c00237:
  teqp Helmholtz energy kernel, https://github.com/usnistgov/teqp.
"""
import matplotlib.pyplot as plt
import numpy as np

from tespy.tools.fluid_properties.solutions import get_solution_pair

fig, (ax_libr, ax_nh3) = plt.subplots(1, 2, figsize=(12, 5))

libr_water = get_solution_pair("libr-water")
T = np.linspace(280, 450, 80)
for w in [0, 0.4, 0.5, 0.55, 0.6, 0.65, 0.7]:
    p = [libr_water.p_bubble(Ti, w) for Ti in T]
    ax_libr.semilogy(T - 273.15, np.array(p) / 1e3, label=f"{w:.0%} LiBr")
ax_libr.set_xlabel("solution temperature in degC")
ax_libr.set_ylabel("vapor pressure in kPa")
ax_libr.set_title("LiBr-water (Patek and Klomfar 2006)")
ax_libr.grid(which="both", alpha=0.3)
ax_libr.legend()

nh3_water = get_solution_pair("nh3-water")
w = np.linspace(0.01, 0.995, 60)
for p, label in [(2.906e5, "2.9 bar"), (15.545e5, "15.5 bar")]:
    T_bubble = [nh3_water.T_bubble(p, wi) for wi in w]
    T_dew = [nh3_water.T_dew(p, wi) for wi in w]
    line, = ax_nh3.plot(w, np.array(T_bubble) - 273.15, label=f"bubble {label}")
    ax_nh3.plot(
        w, np.array(T_dew) - 273.15, "--", color=line.get_color(),
        label=f"dew {label}"
    )
ax_nh3.set_xlabel("NH3 mass fraction")
ax_nh3.set_ylabel("temperature in degC")
ax_nh3.set_title("NH3-water (IAPWS G4-01)")
ax_nh3.grid(alpha=0.3)
ax_nh3.legend()

fig.tight_layout()
fig.savefig("working_pair_properties.svg")
print("written working_pair_properties.svg")
