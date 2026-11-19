"""Absorber with NH3-water.

The refrigerant (0.9995 NH3) leaving the evaporator is absorbed in the weak
solution; with NH3-water the vapor is a SolutionConnection of the same
working pair. Requires the optional dependency teqp.

References
----------
- Tillner-Roth and Friend (1998), https://doi.org/10.1063/1.556015, adopted as
  IAPWS G4-01: NH3-water pair.
- Bell, Deiters and Leal (2022), https://doi.org/10.1021/acs.iecr.2c00237:
  teqp Helmholtz energy kernel, https://github.com/usnistgov/teqp.
"""
from tespy.components import Absorber
from tespy.components import Sink
from tespy.components import Source
from tespy.connections import SolutionConnection
from tespy.networks import Network

nw = Network(iterinfo=False)
nw.units.set_defaults(temperature="degC", pressure="bar", heat="kW")

absorber = Absorber("absorber")
weak = SolutionConnection(
    Source("weak solution"), "out1", absorber, "in1", label="weak",
    mixing_rule="nh3-water"
)
vapor = SolutionConnection(
    Source("refrigerant"), "out1", absorber, "in2", label="vapor"
)
strong = SolutionConnection(
    absorber, "out1", Sink("strong solution"), "in1", label="strong"
)
nw.add_conns(weak, vapor, strong)


def report(case):
    print(
        f"{case}: status {nw.status}, p={vapor.p.val:.3f} bar, "
        f"x_vapor={vapor.x.val:.3f}, xi_strong={strong.xi.val:.4f}, "
        f"m_weak={weak.m.val:.4f} kg/s, Q={absorber.Q.val:.2f} kW"
    )


# refrigerant from the evaporator with 1 % liquid left, weak solution after
# its valve (two-phase), strong solution leaving at 35 degC
vapor.set_attr(xi=0.9995, m=0.01, x=0.99, T=-8.8)
weak.set_attr(xi=0.3067, T=57)
strong.set_attr(T=35)
nw.solve("design")
report("design")

# strong solution composition instead of its temperature
strong.set_attr(T=None, xi=0.4)
nw.solve("design")
report("strong solution composition")
nw.print_results()
