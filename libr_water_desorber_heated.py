"""HeatedDesorber with LiBr-water: desorber with integrated heating water.

The heat of desorption comes from the heating water (in2 to out2), the vapor
leaves at out3.
"""
from tespy.components import HeatedDesorber
from tespy.components import Sink
from tespy.components import Source
from tespy.connections import Connection
from tespy.connections import SolutionConnection
from tespy.networks import Network

from libr_water_reference import h_pump_out
from libr_water_reference import p_condensation
from libr_water_reference import w_rich

nw = Network(iterinfo=False)
nw.units.set_defaults(temperature="degC", pressure="bar", heat="kW")

desorber = HeatedDesorber("desorber")
rich = SolutionConnection(
    Source("rich solution"), "out1", desorber, "in1", label="rich",
    mixing_rule="libr-water"
)
heating_in = Connection(
    Source("heating water in"), "out1", desorber, "in2", label="heating_in"
)
poor = SolutionConnection(
    desorber, "out1", Sink("poor solution"), "in1", label="poor"
)
heating_out = Connection(
    desorber, "out2", Sink("heating water out"), "in1", label="heating_out"
)
vapor = Connection(desorber, "out3", Sink("vapor"), "in1", label="vapor")
nw.add_conns(rich, heating_in, poor, heating_out, vapor)


def report(case):
    print(
        f"{case}: status {nw.status}, T_poor={poor.T.val:.2f} degC, "
        f"xi_poor={poor.xi.val:.4f}, m_heating={heating_in.m.val:.2f} kg/s, "
        f"ttd_u={desorber.ttd_u.val:.2f} K, Q={desorber.Q.val:.1f} kW"
    )


desorber.set_attr(dp2=0)
rich.set_attr(xi=w_rich, p=p_condensation / 1e5, m=10, h=h_pump_out)
poor.set_attr(T=77)
vapor.set_attr(fluid={"H2O": 1})
heating_in.set_attr(fluid={"H2O": 1}, p=5, T=97)
heating_out.set_attr(T=87)
nw.solve("design")
report("poor solution temperature")

# upper terminal temperature difference instead of the poor solution
# temperature
poor.set_attr(T=None)
desorber.set_attr(ttd_u=20)
nw.solve("design")
report("upper terminal temperature difference")

# heat flow instead of the terminal temperature difference
desorber.set_attr(ttd_u=None, Q=desorber.Q.val)
nw.solve("design")
report("heat flow")
nw.print_results()
