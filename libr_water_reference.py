"""Reference states of a single-effect LiBr-water cycle.

The states are computed with the LiBr-water working pair of TESPy (Patek and
Klomfar 2006) and serve as inputs of the LiBr-water component examples. All
values in SI units, the mass fractions w are LiBr mass fractions.

References
----------
- Patek and Klomfar (2006), https://doi.org/10.1016/j.ijrefrig.2005.10.007:
  LiBr-water pair.
- Wagner and Pruss (2002), https://doi.org/10.1063/1.1461829: IAPWS-95 water
  vapor and reference state.
"""
from CoolProp.CoolProp import PropsSI

from tespy.tools.fluid_properties.solutions import get_solution_pair

libr_water = get_solution_pair("libr-water")

T_evaporation = 275.15
p_evaporation = PropsSI("P", "Q", 0, "T", T_evaporation, "water")
T_condensation = 309.15
p_condensation = PropsSI("P", "Q", 0, "T", T_condensation, "water")

# solution leaving the desorber (heat source) and the absorber (heat sink)
T_desorber_out = 350
T_absorber_out = 306.15

# the refrigerant-rich solution leaves the absorber, the refrigerant-poor
# solution the desorber, both at their bubble point
w_rich = libr_water.w_bubble(p_evaporation, T_absorber_out)
w_poor = libr_water.w_bubble(p_condensation, T_desorber_out)

h_absorber_out = libr_water.h_pT(p_evaporation, T_absorber_out, w_rich)

# the liquid is incompressible: the isentropic pump outlet has the inlet
# temperature
eta_s_pump = 0.9
h_pump_out_s = libr_water.h_pT(p_condensation, T_absorber_out, w_rich)
h_pump_out = h_absorber_out + (h_pump_out_s - h_absorber_out) / eta_s_pump

h_desorber_out = libr_water.h_pT(p_condensation, T_desorber_out, w_poor)
