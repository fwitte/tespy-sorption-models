from test_absorber import Absorber
from test_desorber import Desorber


from tespy.components import Source, Sink, Pump, Valve, HeatExchanger
from tespy.networks import Network
from tespy.connections import Connection


from sorption_reference import *


nw = Network()

water = Source("water source")
rich = Sink("rich solution")
poor = Source("poor solution")

pu = Pump("pump")
va = Valve("valve")

absorber = Absorber("absorber")

c1 = Connection(water, "out1", absorber, "in2", label="1")
c2 = Connection(va, "out1", absorber, "in1", label="2")
c3 = Connection(absorber, "out1", pu, "in1", label="3")
c4 = Connection(pu, "out1", rich, "in1", label="4")
c7 = Connection(poor, "out1", va, "in1", label="7")

nw.add_conns(c1, c2, c3, c4, c7)

# pu.set_attr(eta_s=0.8)

c1.set_attr(fluid={"water": 1}, p=p_evap, m=1, x=1)
c2.set_attr(fluid={"water": x_water_poor, "INCOMP::LiBr": 1 - x_water_poor}, h=h_poor, mixing_rule="incomp-solution", solvent="LiBr")
c3.set_attr(h=h_sol_abs_out, p0=p_evap)
print(h_sol_abs_out)
c4.set_attr(p=p_cond, h=37410)
c7.set_attr(p=p_cond)
# nw.set_attr(iterinfo=False)
nw.solve("design")

# how does the reference temperature affect the energy balance
# p_ref = 1e5
# for T_ref in range(274, 400):
#     h_water_ref = CP.CoolProp.PropsSI("H", "P", p_ref, "T", T_ref, "water")
#     h_poor_ref = CP.CoolProp.PropsSI("H", "P", p_ref, "T", T_ref, f"INCOMP::LiBr[{x_poor}]")
#     h_rich_ref = CP.CoolProp.PropsSI("H", "P", p_ref, "T", T_ref, f"INCOMP::LiBr[{x_rich}]")
#     print((c1.h.val_SI - h_water_ref) * c1.m.val_SI + (c2.h.val_SI - h_poor_ref) * c2.m.val_SI - (c3.h.val_SI - h_rich_ref) * c3.m.val_SI)

# some checks
# nw.print_results()
# assert round(c1.m.val_SI * c1.fluid.val["water"] + c2.m.val_SI * c2.fluid.val["water"], 4) == round(c3.m.val_SI * c3.fluid.val["water"], 4)
# assert round(c2.m.val_SI * c2.fluid.val["LiBr"], 4) == round(c3.m.val_SI * c3.fluid.val["LiBr"], 4)

c4.set_attr(h=None)
pu.set_attr(eta_s=1)
# now there is two additional equations in case both fluids at outlet 1 are variable
# and one additional equation if none of the fluids is variale
# fluid composition as function of saturation temperature and pressure
c3.fluid.is_set = set()
c1.set_attr(p=None)
c3.set_attr(h=None, T=306.15, p=p_evap)
c3.h.val0 = c3.h.val_SI
# nw.solve("design")
# check results, should be identical to previous ones
# assert round(c1.m.val_SI * c1.fluid.val["water"] + c2.m.val_SI * c2.fluid.val["water"], 4) == round(c3.m.val_SI * c3.fluid.val["water"], 4)
# assert round(c2.m.val_SI * c2.fluid.val["LiBr"], 4) == round(c3.m.val_SI * c3.fluid.val["LiBr"], 4)

# fix the either the water or the libr mass fraction and the temperature or pressure
# gives us the other respective value, pressure in this case
# c3.set_attr(fluid={"INCOMP::LiBr": 0.50}, T=295, p=None)
# nw.solve("design")
# assert round(c1.m.val_SI * c1.fluid.val["water"] + c2.m.val_SI * c2.fluid.val["water"], 4) == round(c3.m.val_SI * c3.fluid.val["water"], 4)
# assert round(c2.m.val_SI * c2.fluid.val["LiBr"], 4) == round(c3.m.val_SI * c3.fluid.val["LiBr"], 4)

print(f"T3: {c3.T.val_SI}, p3: {c3.p.val_SI}, fluid3: {c3.fluid.val}")

# nw.print_results()


he = HeatExchanger("internal heat exchanger")

nw.del_conns(c4, c7)

c4 = Connection(pu, "out1", he, "in2", label="4")
c5 = Connection(he, "out2", rich, "in1", label="5")

c6 = Connection(poor, "out1", he, "in1", label="6")
c7 = Connection(he, "out1", va, "in1", label="7")

nw.add_conns(c4, c5, c6, c7)

c4.set_attr(p=p_cond, h0=37400)
c5.set_attr(h0=40000, p=p_cond)
c6.set_attr(h=h_poor, p=p_cond)
c7.set_attr(p=p_cond, h=100000)
c2.set_attr(h=None)

# nw.solve("design")

# he.set_attr(ttd_l=5)
# c7.set_attr(h=None)
# nw.solve("design")

# nw.print_results()

desorber = Desorber("desorber")

nw.del_conns(c5)

h5 = c5.h.val_SI

c5 = Connection(he, "out2", desorber, "in1", label="5")
c6a = Connection(desorber, "out1", rich, "in1", label="6a")
c10 = Connection(desorber, "out2", Sink("water sink"), "in1", label="10")

nw.add_conns(c5, c6a, c10)

c10.set_attr(fluid={"water": 1}, x=1, p=p_cond)
c6a.set_attr(h=h_poor, p0=p_cond)
c5.set_attr(h0=h5, p0=p_cond)

nw.solve("design")
nw.print_results()

from tespy.connections import Ref

c10.set_attr(p=None)
c6a.set_attr(fluid={"water": x_water_poor, "INCOMP::LiBr": 1 - x_water_poor})
c6.set_attr(p=None, h=None)
c6.set_attr(p=Ref(c6a, 1, 0), h=Ref(c6a, 1, 0))
c2.set_attr(fluid={"INCOMP::LiBr": None, "water": None})


def fluid_fraction(ude):
    fluid = ude.params["fluid"]
    return ude.conns[0].fluid.val[fluid] - ude.conns[1].fluid.val[fluid]

def fluid_fraction_deriv(ude):
    fluid = ude.params["fluid"]
    if fluid in ude.conns[0].fluid.is_var:
        ude.jacobian[ude.conns[0].fluid.J_col[fluid]] = 1

    if fluid in ude.conns[1].fluid.is_var:
        ude.jacobian[ude.conns[1].fluid.J_col[fluid]] = -1

from tespy.tools.helpers import UserDefinedEquation

water_ude = UserDefinedEquation(
    'water ude', fluid_fraction, fluid_fraction_deriv, [c6, c6a], params={'fluid': "water"}
)
libr_ude = UserDefinedEquation(
    'libr ude', fluid_fraction, fluid_fraction_deriv, [c6, c6a], params={'fluid': "LiBr"}
)

nw.add_ude(water_ude, libr_ude)

# nw.solve("design")
# nw.print_results()

c6a.set_attr(T=350, fluid={"water": None, "INCOMP::LiBr": None})
c3.set_attr(T=300)

# nw.solve("design")

# c6a.set_attr(p=p_cond * .9)
# nw.solve("design")
# nw.print_results()

c4.set_attr(p=None)
c7.set_attr(p=None, h=None)

he.set_attr(pr1=1, pr2=1, ttd_u=20)

# nw.solve("design")
# nw.print_results()

nw.del_conns(c10)

from tespy.components import SimpleHeatExchanger

cd = SimpleHeatExchanger("condenser")
expva = Valve("Expansion valve")
ev = SimpleHeatExchanger("evaporator")

c10 = Connection(desorber, "out2", cd, "in1", label="10")
c11 = Connection(cd, "out1", expva, "in1", label="11")
c12 = Connection(expva, "out1", ev, "in1", label="12")
c13 = Connection(ev, "out1", Sink("dummy"), "in1", label="13")

c10.set_attr(fluid={"water": 1}, x=1)
c11.set_attr(p=p_cond, x=0)
c12.set_attr(p=p_evap)
c13.set_attr(p=p_evap, x=1)

nw.add_conns(c10, c11, c12, c13)

# nw.solve("design")

cd.set_attr(pr=1)
ev.set_attr(pr=1)

c11.set_attr(p=None)
c12.set_attr(p=None)

# nw.print_results()

print()

print(desorber.Q.val + absorber.Q.val + cd.Q.val + ev.Q.val + pu.P.val)

nw.del_conns(c1, c13)

from tespy.components import CycleCloser

cc = CycleCloser("closer refrigeration cycle")
c13 = Connection(ev, "out1", cc, "in1", label="13")
c14 = Connection(cc, "out1", absorber, "in2", label="14")

nw.add_conns(c13, c14)

c14.set_attr(fluid={"water": 1}, m=1, x=1)
# c10.set_attr(fluid={"water": None})

# nw.solve("design")

c14.set_attr(T=280)
c3.set_attr(p=None)
c6a.set_attr(h=None)
c10.set_attr(T=320)
c14.set_attr(m=None)
cd.set_attr(Q=-4e6)

# nw.solve("design")

cd.set_attr(Q=None)
absorber.set_attr(Q=-5e6)

# nw.solve("design")

# absorber.set_attr(Q=None)
# desorber.set_attr(Q=5e6)

# nw.solve("design")

# nw.set_attr(iterinfo=False)

# nw.print_results()

nw.specifications

h = c6.h.val_SI
p = c6.p.val_SI

nw.del_conns(c6, c6a)

cc_solution = CycleCloser("closer solution cycle")

c6a = Connection(desorber, "out1", cc_solution, "in1", label="6a")
c6 = Connection(cc_solution, "out1", he, "in1", label="6")

c6.fluid.back_end = {"LiBr": "INCOMP", "water": "HEOS"}
c6a.fluid.back_end = {"LiBr": "INCOMP", "water": "HEOS"}
c6.set_attr(h=h, p0=p)
c6a.set_attr(h0=h, p0=p)

nw.add_conns(c6a, c6)

# this part is not necassary, ude connections are passed by label somehow...
# nw.del_ude(water_ude, libr_ude)

# water_ude = UserDefinedEquation(
#     'water ude', fluid_fraction, fluid_fraction_deriv, [c6, c6a], params={'fluid': "water"}
# )
# libr_ude = UserDefinedEquation(
#     'libr ude', fluid_fraction, fluid_fraction_deriv, [c6, c6a], params={'fluid': "LiBr"}
# )

# nw.add_ude(water_ude, libr_ude)

nw.solve("design")
# nw.set_attr(iterinfo=False)

c6.set_attr(h=None)
# pu.set_attr(eta_s=None, eta_vol=1)

c14.set_attr(T=273.15 + 6)
c3.set_attr(T=273.15 + 34.9)
c10.set_attr(T=44.5 + 273.15)
c6.set_attr(T=90 + 273.15)
he.set_attr(ttd_u=None)
c7.set_attr(T=273.15 + 65)

absorber.set_attr(Q=None)
ev.set_attr(Q=1e4)

nw.solve("design")

print([c.m.val_SI for c in [c2, c5, c10]])
print(1 / c3.vol.val_SI)
print(c3.v.val_SI * (c4.p.val_SI - c3.p.val_SI))
print(c3.m.val_SI * (c4.h.val_SI - c3.h.val_SI))
print(c4.p.val_SI - c3.p.val_SI)

pu.set_attr(eta_s=None, eta_vol=1)

nw.solve("design")

print([c.m.val_SI for c in [c2, c5, c10]])

print(1 / c3.vol.val_SI)
print(c3.v.val_SI * (c4.p.val_SI - c3.p.val_SI))
print(c3.m.val_SI * (c4.h.val_SI - c3.h.val_SI))
print(c4.p.val_SI - c3.p.val_SI)

print(c6.fluid.val)
print(c3.fluid.val)

nw.print_results()


c3.set_attr(T=None)
c3.set_attr(fluid={"water": 0.48, "INCOMP::LiBr": 1 - 0.48})

nw.solve("design")

print(c3.T.val)



# for T in range(340, 400):
#     c6.set_attr(T=T)
#     c10.set_attr(T=T - 30)

#     nw.solve("design")

#     print(ev.Q.val)

# nw.add_conns()

exit()
nw.del_conns(c6, c6a)

from tespy.components import Splitter

sp = Splitter("splitter")

c6a = Connection(desorber, "out2", sp, "in1", label="6a")
c6b = Connection(sp, "out1", he, "in1", label="6b")
c6c = Connection(sp, "out2", rich, "in1", label="6c")

nw.add_conns(c6a, c6b, c6c)

c6a.set_attr(h0=h_poor)
c6b.set_attr(h0=h_poor)
c6c.set_attr(h0=h_poor)
c10.set_attr(p=p_cond)

nw.solve("design")
