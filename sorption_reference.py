"""Reference states of a single-effect LiBr-water cycle.

The states are computed with the LiBr-water working pair of TESPy (Patek and
Klomfar 2006) and serve as fixed inputs of the example scripts.
"""
import CoolProp as CP

from tespy.tools.fluid_properties.solutions import get_solution_pair

libr_water = get_solution_pair("libr-water")

# water cycle
T_evap = 275.15
p_evap = CP.CoolProp.PropsSI("P", "Q", 0, "T", T_evap, "water")

T_cond = 309.15
p_cond = CP.CoolProp.PropsSI("P", "Q", 0, "T", T_cond, "water")

# heat source temperature
T_sol_des_out = 350

# heat sink temperature
T_sol_abs_out = 306.15

# LiBr mass fraction of the refrigerant-rich solution leaving the absorber and
# of the refrigerant-poor solution leaving the desorber
x_rich = libr_water.w_bubble(p_evap, T_sol_abs_out)
x_poor = libr_water.w_bubble(p_cond, T_sol_des_out)

x_water_rich = 1 - x_rich
x_water_poor = 1 - x_poor

T_water_abs_in = T_evap
h_water_abs_in = CP.CoolProp.PropsSI("H", "Q", 1, "T", T_water_abs_in, "water")

h_sol_abs_out = libr_water.h_pT(p_evap, T_sol_abs_out, x_rich)
s_sol_abs_out = libr_water.s_pT(p_evap, T_sol_abs_out, x_rich)

# the liquid is incompressible, the isentropic pump outlet has the inlet
# temperature
eta_s_pump = 0.9
h_pump_out_s = libr_water.h_pT(p_cond, T_sol_abs_out, x_rich)
h_pump_out = h_sol_abs_out + (h_pump_out_s - h_sol_abs_out) / eta_s_pump

h_poor = libr_water.h_pT(p_cond, T_sol_des_out, x_poor)

# vapor leaving the desorber in equilibrium with the refrigerant-rich solution
T_water_des_out = libr_water.T_bubble(p_cond, x_rich)
h_water_des_out = CP.CoolProp.PropsSI("H", "P", p_cond, "T", T_water_des_out, "water")

m_water = 1
m_rich = m_water * x_poor / (x_poor - x_rich)
m_poor = m_rich - m_water

delta_H_abs = -m_water * h_water_abs_in - m_poor * h_poor + m_rich * h_sol_abs_out
delta_H_des = m_water * h_water_des_out + m_poor * h_poor - m_rich * h_pump_out
