from test_absorber import Absorber
from test_desorber import Desorber


from tespy.components import Source, Sink, Pump, Valve, HeatExchanger, CycleCloser, SimpleHeatExchanger
from tespy.networks import Network
from tespy.connections import Connection, Ref


nw = Network(T_unit="C", p_unit="bar")

absorber = Absorber("absorber")
desorber = Desorber("desorber")

sol_pump = Pump("solution pump")
sol_valve = Valve("solution valve")
sol_heatex = HeatExchanger("solution heat exchanger")

sol_heatex_sink = Sink("solution heat exchanger sink")
sol_heatex_source = Source("solution heat exchanger source")
sol_cc = CycleCloser("solution cycle closer")

ev_source = Source("water from ev")
cd_sink = Sink("water to cd")


c1 = Connection(absorber, "out1", sol_heatex, "in1", label="1")
c2 = Connection(sol_heatex, "out1", sol_valve, "in1", label="2")
c3 = Connection(sol_valve, "out1", desorber, "in1", label="3")
c4 = Connection(desorber, "out1", sol_cc, "in1", label="4")
c40 = Connection(sol_cc, "out1", sol_pump, "in1", label="40")
c5 = Connection(sol_pump, "out1", sol_heatex, "in2", label="5")
c6 = Connection(sol_heatex, "out2", absorber, "in1", label="6")

c10 = Connection(desorber, "out2", cd_sink, "in1", label="10")
c14 = Connection(ev_source, "out1", absorber, "in2", label="14")

nw.add_conns(c1, c2, c3, c4, c40, c5, c6, c10, c14)

# some starting values are required here...
c1.set_attr(p0=0.5, m=10, h0=244000)
c2.set_attr(h=Ref(c1, 1, 20000), h0=200000)  # the sign in the Ref should be negative, it is a bug from previous version and already fixed in main
c3.set_attr(p0=0.01)
c4.set_attr(h0=20000, p0=0.01)
c5.set_attr(h=35000)
c6.set_attr(fluid={"INCOMP::LiBr": 0.55, "water": 0.45}, solvent="LiBr", mixing_rule="incomp-solution", h0=40000)

c10.set_attr(fluid={"water": 1}, x=1, m=1, T=10)
c14.set_attr(fluid={"water": 1}, x=1, T=90, m=1)

sol_heatex.set_attr(pr1=1, pr2=1)

nw.solve("design")

nw.del_conns(c10, c14)

refr_cc = CycleCloser("refrigeration cycle closer")
cd = SimpleHeatExchanger("condenser")
refr_pump = Pump("refrigeration pump")
ev = SimpleHeatExchanger("evaporator")

c10 = Connection(desorber, "out2", refr_cc, "in1", label="10")
c11 = Connection(refr_cc, "out1", cd, "in1", label="11")
c12 = Connection(cd, "out1", refr_pump, "in1", label="12")
c13 = Connection(refr_pump, "out1", ev, "in1", label="13")
c14 = Connection(ev, "out1", absorber, "in2", label="14")

c10.set_attr(fluid={"water": 1}, x=1, m=1, T=10)
c11.set_attr(fluid={"water": 1}, m=1)
c12.set_attr(x=0)
c14.set_attr(x=1, T=90)

cd.set_attr(pr=1)
ev.set_attr(pr=1)
refr_pump.set_attr(eta_s=0.75)

nw.add_conns(c10, c11, c12, c13, c14)

# nw.solve("design")

c5.set_attr(h=None)
sol_pump.set_attr(eta_s=0.75)

c2.set_attr(h_ref=None)
sol_heatex.set_attr(ttd_u=10)

nw.solve("design")

c1.set_attr(m=None)
desorber.set_attr(Q=1e6)

c10.set_attr(m=None)
ev.set_attr(Q=2.5e6)

c11.set_attr(m=None)
c11.set_attr(m=Ref(c10, 1, 0))

nw.solve("design")


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
    'water ude', fluid_fraction, fluid_fraction_deriv, [c4, c40], params={'fluid': "water"}
)
# libr_ude = UserDefinedEquation(
#     'libr ude', fluid_fraction, fluid_fraction_deriv, [c4, c40], params={'fluid': "LiBr"}
# )

nw.add_ude(water_ude) #, libr_ude)

c4.set_attr(fluid={"INCOMP::LiBr": None, "water": None})
c6.set_attr(fluid={"INCOMP::LiBr": None, "water": None})
# c1.set_attr(T=120)
c4.set_attr(T=20)

nw.solve("design")

print([c.fluid.val for c in (c6, c3, c4)])

nw.print_results()

exit()

# 1st law consistency check
print(sum([refr_pump.P.val, sol_pump.P.val, cd.Q.val, ev.Q.val, absorber.Q.val, desorber.Q.val]))
nw.set_attr(iterinfo=False)

results = {}
import pandas as pd

results["T_evap"] = pd.DataFrame()

for T in range(65, 90):
    c14.set_attr(T=T)
    nw.solve("design")
    results["T_evap"].loc[T, "power input"] = sum([refr_pump.P.val, sol_pump.P.val])
    results["T_evap"].loc[T, "heat input"] = sum([ev.Q.val, desorber.Q.val])
    results["T_evap"].loc[T, "heat production"] = sum([absorber.Q.val])

import matplotlib.pyplot as plt


fig, ax = plt.subplots(1)

ax.plot(results["T_evap"].index, results["T_evap"]["heat production"])
ax.plot(results["T_evap"].index, results["T_evap"]["heat input"])

plt.show()
