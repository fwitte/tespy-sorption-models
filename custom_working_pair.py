"""Custom working pair: LiBr-water with a limited equilibrium composition.

A working pair is a subclass of :code:`SolutionPair`, registered with
:code:`register_solution_pair` it is available as mixing rule of its name.
The pair below derives from TESPy's LiBr-water pair and limits the equilibrium
composition to 70 % LiBr, e.g. to keep away from crystallization. A custom
pair with the same key component as a built-in pair, LiBr here, must be named
with :code:`mixing_rule` on a solution connection of each circuit, it cannot
be inferred from the fluid names.

References
----------
- Patek and Klomfar (2006), https://doi.org/10.1016/j.ijrefrig.2005.10.007:
  LiBr-water pair.
- Wagner and Pruss (2002), https://doi.org/10.1063/1.1461829: IAPWS-95 water
  vapor and reference state.
"""
from CoolProp.CoolProp import PropsSI

from tespy.components import Absorber
from tespy.components import Sink
from tespy.components import Source
from tespy.connections import Connection
from tespy.connections import SolutionConnection
from tespy.networks import Network
from tespy.tools.fluid_properties.solutions import get_solution_pair
from tespy.tools.fluid_properties.solutions import register_solution_pair
from tespy.tools.fluid_properties.solutions.libr_water import LiBrWater


class LimitedLiBrWater(LiBrWater):
    """LiBr-water after Patek and Klomfar with the equilibrium composition
    limited to 70 % LiBr."""

    name = "libr-water-limited"
    w_max = 0.70


try:
    pair = get_solution_pair(LimitedLiBrWater.name)
except KeyError:
    pair = LimitedLiBrWater()
    register_solution_pair(pair)

p = PropsSI("P", "T", 318.15, "Q", 0, "water")
print(
    "equilibrium LiBr mass fraction at the 45 degC water saturation pressure "
    f"and 100 degC: {pair.w_bubble(p, 373.15):.3f}"
)
try:
    pair.w_bubble(p, 403.15)
except ValueError as e:
    print(f"at 130 degC: {e}")

# the custom pair in a model, named on the poor solution
nw = Network(iterinfo=False)
nw.units.set_defaults(temperature="degC", pressure="bar", heat="kW")

absorber = Absorber("absorber")
poor = SolutionConnection(
    Source("poor solution"), "out1", absorber, "in1", label="poor",
    mixing_rule=LimitedLiBrWater.name
)
vapor = Connection(Source("vapor"), "out1", absorber, "in2", label="vapor")
rich = SolutionConnection(
    absorber, "out1", Sink("rich solution"), "in1", label="rich"
)
nw.add_conns(poor, vapor, rich)

vapor.set_attr(fluid={"H2O": 1}, p=0.01, m=1, x=1)
poor.set_attr(xi=0.62, T=47)
rich.set_attr(T=32)
nw.solve("design")
print(
    f"status {nw.status}, pair {rich.mixing_rule}, "
    f"xi_rich={rich.xi.val:.4f}, m_poor={poor.m.val:.3f} kg/s, "
    f"Q={absorber.Q.val:.1f} kW"
)
