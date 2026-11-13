"""Single-effect LiBr-water absorption chiller.

Generator (desorber), condenser, evaporator, absorber, solution pump,
solution heat exchanger and two valves; the solution circuit is closed by a
cycle closer. After the design point, the generator outlet temperature is
varied.
"""
from tespy.components import Absorber
from tespy.components import CycleCloser
from tespy.components import Desorber
from tespy.components import HeatExchanger
from tespy.components import Pump
from tespy.components import SimpleHeatExchanger
from tespy.components import Valve
from tespy.connections import Connection
from tespy.connections import SolutionConnection
from tespy.networks import Network

nw = Network(iterinfo=False)
nw.units.set_defaults(temperature="degC", pressure="bar", heat="kW", power="kW")

generator = Desorber("generator")
condenser = SimpleHeatExchanger("condenser")
refrigerant_valve = Valve("refrigerant valve")
evaporator = SimpleHeatExchanger("evaporator")
absorber = Absorber("absorber")
closer = CycleCloser("solution cycle closer")
pump = Pump("solution pump")
shx = HeatExchanger("solution heat exchanger")
solution_valve = Valve("solution valve")

s0 = SolutionConnection(
    absorber, "out1", closer, "in1", label="s0", mixing_rule="libr-water"
)
s1 = SolutionConnection(closer, "out1", pump, "in1", label="s1")
s2 = SolutionConnection(pump, "out1", shx, "in2", label="s2")
s3 = SolutionConnection(shx, "out2", generator, "in1", label="s3")
s4 = SolutionConnection(generator, "out1", shx, "in1", label="s4")
s5 = SolutionConnection(shx, "out1", solution_valve, "in1", label="s5")
s6 = SolutionConnection(solution_valve, "out1", absorber, "in1", label="s6")
r1 = Connection(generator, "out2", condenser, "in1", label="r1")
r2 = Connection(condenser, "out1", refrigerant_valve, "in1", label="r2")
r3 = Connection(refrigerant_valve, "out1", evaporator, "in1", label="r3")
r4 = Connection(evaporator, "out1", absorber, "in2", label="r4")
nw.add_conns(s0, s1, s2, s3, s4, s5, s6, r1, r2, r3, r4)

condenser.set_attr(dp=0)
evaporator.set_attr(dp=0, Q=100)
pump.set_attr(eta_s=0.7)
shx.set_attr(dp1=0, dp2=0, ttd_l=10)

r1.set_attr(fluid={"H2O": 1})
r2.set_attr(x=0, T=45)
r4.set_attr(x=1, T=5)
s0.set_attr(T=40)
# the cycle closer does not close the variable composition
s1.set_attr(fluid_balance=True)
s4.set_attr(T=110)

nw.solve("design")
nw.print_results()
print(
    f"COP {evaporator.Q.val / generator.Q.val:.3f}, "
    f"circulation ratio {s0.m.val / r1.m.val:.2f}, "
    f"LiBr {s0.xi.val:.4f} (absorber) / {s4.xi.val:.4f} (generator)"
)

print("generator outlet temperature sweep")
for T in [90, 100, 110, 120, 130]:
    s4.set_attr(T=T)
    nw.solve("design")
    print(
        f"  T_gen {T} degC: status {nw.status}, "
        f"COP {evaporator.Q.val / generator.Q.val:.3f}, "
        f"circulation ratio {s0.m.val / r1.m.val:.2f}, "
        f"xi_gen {s4.xi.val:.4f}"
    )
