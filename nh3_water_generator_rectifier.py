"""Generator and rectifier with NH3-water.

The strong solution is boiled in the generator, the vapor contains water and
is purified by partial condensation in the rectifier; the reflux is the liquid
in equilibrium with the entering vapor. Here the reflux leaves the system, in
a cycle it returns to the generator (see nh3_water_chiller.py). Requires the
optional dependency teqp.

References
----------
- Tillner-Roth and Friend (1998), https://doi.org/10.1063/1.556015, adopted as
  IAPWS G4-01: NH3-water pair.
- Bell, Deiters and Leal (2022), https://doi.org/10.1021/acs.iecr.2c00237:
  teqp Helmholtz energy kernel.
"""
from tespy.components import Desorber
from tespy.components import Rectifier
from tespy.components import Sink
from tespy.components import Source
from tespy.connections import SolutionConnection
from tespy.networks import Network

nw = Network(iterinfo=False)
nw.units.set_defaults(temperature="degC", pressure="bar", heat="kW")

generator = Desorber("generator", vapor_state="outlet-equilibrium")
rectifier = Rectifier("rectifier")
strong = SolutionConnection(
    Source("strong solution"), "out1", generator, "in1", label="strong",
    mixing_rule="nh3-water"
)
weak = SolutionConnection(
    generator, "out1", Sink("weak solution"), "in1", label="weak"
)
vapor = SolutionConnection(generator, "out2", rectifier, "in1", label="vapor")
refrigerant = SolutionConnection(
    rectifier, "out1", Sink("refrigerant"), "in1", label="refrigerant"
)
reflux = SolutionConnection(
    rectifier, "out2", Sink("reflux"), "in1", label="reflux"
)
nw.add_conns(strong, weak, vapor, refrigerant, reflux)

strong.set_attr(xi=0.4172, p=15.545, m=0.05, T=85)
weak.set_attr(T=120)
refrigerant.set_attr(xi=0.9995)
# the rectifier does not impose its pressure on the reflux
reflux.set_attr(p=15.545)
nw.solve("design")
nw.print_results()
print(
    f"vapor {vapor.xi.val:.4f} NH3 at {vapor.T.val:.2f} degC, "
    f"refrigerant {refrigerant.m.val * 1e3:.3f} g/s at {refrigerant.T.val:.2f} "
    f"degC, reflux {reflux.m.val * 1e3:.3f} g/s with {reflux.xi.val:.4f} NH3, "
    f"Q_gen {generator.Q.val:.2f} kW, Q_rect {rectifier.Q.val:.2f} kW"
)

# purer refrigerant
for purity in [0.995, 0.999, 0.9999]:
    refrigerant.set_attr(xi=purity)
    nw.solve("design")
    print(
        f"  purity {purity}: status {nw.status}, "
        f"refrigerant {refrigerant.m.val * 1e3:.3f} g/s, "
        f"Q_rect {rectifier.Q.val:.3f} kW"
    )
