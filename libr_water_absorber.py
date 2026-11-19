"""Absorber with LiBr-water: specification variants of a standalone absorber.

Water vapor (in2) is absorbed in a refrigerant-poor solution (in1), the
refrigerant-rich solution (out1) leaves at its bubble point.

References
----------
- Patek and Klomfar (2006), https://doi.org/10.1016/j.ijrefrig.2005.10.007:
  LiBr-water pair.
- Wagner and Pruss (2002), https://doi.org/10.1063/1.1461829: IAPWS-95 water
  vapor and reference state, evaluated with CoolProp,
  https://github.com/CoolProp/CoolProp.
"""
from tespy.components import Absorber
from tespy.components import Sink
from tespy.components import Source
from tespy.connections import Connection
from tespy.connections import SolutionConnection
from tespy.networks import Network

from libr_water_reference import h_absorber_out
from libr_water_reference import w_poor

nw = Network(iterinfo=False)
nw.units.set_defaults(temperature="degC", pressure="bar", heat="kW")

absorber = Absorber("absorber")
poor = SolutionConnection(
    Source("poor solution"), "out1", absorber, "in1", label="poor",
    mixing_rule="libr-water"
)
vapor = Connection(Source("vapor"), "out1", absorber, "in2", label="vapor")
rich = SolutionConnection(
    absorber, "out1", Sink("rich solution"), "in1", label="rich"
)
nw.add_conns(poor, vapor, rich)


def report(case):
    print(
        f"{case}: status {nw.status}, p={vapor.p.val:.4f} bar, "
        f"xi_poor={poor.xi.val:.4f}, xi_rich={rich.xi.val:.4f}, "
        f"T_rich={rich.T.val:.2f} degC, m_poor={poor.m.val:.3f} kg/s, "
        f"Q={absorber.Q.val:.1f} kW"
    )


# 1 kg/s of saturated vapor at 10 mbar, outlet enthalpy given
vapor.set_attr(fluid={"H2O": 1}, p=0.01, m=1, x=1)
poor.set_attr(xi=w_poor, T=47)
rich.set_attr(h=h_absorber_out)
nw.solve("design")
report("outlet enthalpy")

# poor solution mass flow instead of the outlet enthalpy
poor.set_attr(m=10)
rich.set_attr(h=None)
nw.solve("design")
report("poor solution mass flow")

# outlet temperature instead of the poor solution mass flow
rich.set_attr(T=32)
poor.set_attr(m=None)
nw.solve("design")
report("outlet temperature")

# outlet composition: the absorber pressure follows from the equilibrium
vapor.set_attr(p=None)
rich.set_attr(xi=0.5)
nw.solve("design")
report("outlet composition")

# approach to the bubble point of 2 K
absorber.set_attr(td_eq=2)
nw.solve("design")
report("approach to equilibrium")
nw.print_results()
