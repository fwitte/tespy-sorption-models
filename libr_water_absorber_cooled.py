"""CooledAbsorber with LiBr-water: absorber with integrated cooling water.

The heat of absorption goes to the cooling water (in2 to out2), the vapor
enters at in3.
"""
from tespy.components import CooledAbsorber
from tespy.components import Sink
from tespy.components import Source
from tespy.connections import Connection
from tespy.connections import SolutionConnection
from tespy.networks import Network

from libr_water_reference import p_evaporation
from libr_water_reference import w_poor

nw = Network(iterinfo=False)
nw.units.set_defaults(temperature="degC", pressure="bar", heat="kW")

absorber = CooledAbsorber("absorber")
poor = SolutionConnection(
    Source("poor solution"), "out1", absorber, "in1", label="poor",
    mixing_rule="libr-water"
)
cooling_in = Connection(
    Source("cooling water in"), "out1", absorber, "in2", label="cooling_in"
)
vapor = Connection(Source("vapor"), "out1", absorber, "in3", label="vapor")
rich = SolutionConnection(
    absorber, "out1", Sink("rich solution"), "in1", label="rich"
)
cooling_out = Connection(
    absorber, "out2", Sink("cooling water out"), "in1", label="cooling_out"
)
nw.add_conns(poor, cooling_in, vapor, rich, cooling_out)


def report(case):
    print(
        f"{case}: status {nw.status}, m_vapor={vapor.m.val:.3f} kg/s, "
        f"T_rich={rich.T.val:.2f} degC, xi_rich={rich.xi.val:.4f}, "
        f"m_cooling={cooling_in.m.val:.2f} kg/s, ttd_l={absorber.ttd_l.val:.2f} K, "
        f"Q={absorber.Q.val:.1f} kW"
    )


absorber.set_attr(dp2=0)
poor.set_attr(xi=w_poor, T=47, m=10)
vapor.set_attr(fluid={"H2O": 1}, p=p_evaporation / 1e5, m=1, x=1)
cooling_in.set_attr(fluid={"H2O": 1}, p=2, T=20)
cooling_out.set_attr(T=25)
nw.solve("design")
report("vapor mass flow")

# lower terminal temperature difference instead of the vapor mass flow
vapor.set_attr(m=None)
absorber.set_attr(ttd_l=13)
nw.solve("design")
report("lower terminal temperature difference")

# heat flow instead of the terminal temperature difference
absorber.set_attr(ttd_l=None, Q=absorber.Q.val)
nw.solve("design")
report("heat flow")
nw.print_results()
