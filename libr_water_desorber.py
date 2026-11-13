"""Desorber with LiBr-water: specification variants of a standalone desorber.

The refrigerant-rich solution (in1) is separated into the refrigerant-poor
solution (out1) at its bubble point and water vapor (out2).
"""
from tespy.components import Desorber
from tespy.components import Sink
from tespy.components import Source
from tespy.connections import Connection
from tespy.connections import SolutionConnection
from tespy.networks import Network

from libr_water_reference import h_desorber_out
from libr_water_reference import h_pump_out
from libr_water_reference import p_condensation
from libr_water_reference import w_rich

nw = Network(iterinfo=False)
nw.units.set_defaults(temperature="degC", pressure="bar", heat="kW")

desorber = Desorber("desorber")
rich = SolutionConnection(
    Source("rich solution"), "out1", desorber, "in1", label="rich",
    mixing_rule="libr-water"
)
poor = SolutionConnection(
    desorber, "out1", Sink("poor solution"), "in1", label="poor"
)
vapor = Connection(desorber, "out2", Sink("vapor"), "in1", label="vapor")
nw.add_conns(rich, poor, vapor)


def report(case):
    print(
        f"{case}: status {nw.status}, p={vapor.p.val:.4f} bar, "
        f"xi_poor={poor.xi.val:.4f}, T_poor={poor.T.val:.2f} degC, "
        f"T_vapor={vapor.T.val:.2f} degC, m_vapor={vapor.m.val:.3f} kg/s, "
        f"Q={desorber.Q.val:.1f} kW"
    )


# the vapor leaves in equilibrium with the entering solution
# (vapor_state="inlet-equilibrium", the default)
rich.set_attr(xi=w_rich, p=p_condensation / 1e5, m=10, h=h_pump_out)
poor.set_attr(h=h_desorber_out)
vapor.set_attr(fluid={"H2O": 1})
nw.solve("design")
report("enthalpies, vapor in equilibrium with the inlet")

# the vapor leaves in equilibrium with the leaving solution
desorber.set_attr(vapor_state="outlet-equilibrium")
nw.solve("design")
report("vapor in equilibrium with the outlet")

# poor solution mass flow instead of its enthalpy
poor.set_attr(m=9, h=None)
nw.solve("design")
report("poor solution mass flow")

# poor solution temperature instead of its mass flow
poor.set_attr(m=None, T=77)
nw.solve("design")
report("poor solution temperature")

# poor solution composition: the desorber pressure follows from the
# equilibrium
poor.set_attr(xi=0.7)
rich.set_attr(p=None)
nw.solve("design")
report("poor solution composition")

# the vapor state is specified on the vapor connection instead
desorber.set_attr(vapor_state="free")
vapor.set_attr(T=80)
nw.solve("design")
report("free vapor state")
nw.print_results()
