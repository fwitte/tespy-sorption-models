"""Single-effect NH3-water absorption chiller with rectifier.

The cycle of the CoolSolve Library model CSL-0249: 10 kW cooling capacity,
evaporator inlet at -10 degC, condenser outlet at 40 degC, absorber outlet at
35 degC, generator outlet at 120 degC, refrigerant of 0.9995 NH3,
effectivenesses of the solution and the refrigerant heat exchanger of 0.7
(temperature based, user defined equations), pump efficiency of 0.6. The
reflux of the rectifier enters the generator through a merge. After the
design point, the evaporation temperature is varied. Requires the optional
dependency teqp.

The refrigerant heat exchanger of the original is infeasible: its
effectiveness refers to the liquid side, which has the larger heat capacity
rate, the cold vapor leaves at 54.8 degC above the 40 degC of the entering
liquid. TESPy reproduces the state and reports a cold side effectiveness above
1 (network status 1).

References
----------
- Tillner-Roth and Friend (1998), https://doi.org/10.1063/1.556015, adopted as
  IAPWS G4-01: NH3-water pair.
- Bell, Deiters and Leal (2022), https://doi.org/10.1021/acs.iecr.2c00237:
  teqp Helmholtz energy kernel, https://github.com/usnistgov/teqp.
- CoolSolve Library CSL-0249, https://github.com/IntSusEnergySystems/CoolSolve_Library/tree/main/models/refrigeration_heat_pumps/absorption/nh3h2o_absorption_chiller:
  design point of this example, with the CoolSolve solution
  nh3h2o_absorption_chiller.sol. CoolSolve, https://github.com/CoolProp/CoolSolve,
  implements IAPWS G4-01 in src/nh3h2o.cpp and src/nh3h2o_flash.cpp.
- Herold, Radermacher and Klein: Absorption Chillers and Heat Pumps, CRC
  Press, 1996: single-effect cycle.
"""
from tespy.components import Absorber
from tespy.components import CycleCloser
from tespy.components import Desorber
from tespy.components import HeatExchanger
from tespy.components import Merge
from tespy.components import Pump
from tespy.components import Rectifier
from tespy.components import SimpleHeatExchanger
from tespy.components import Valve
from tespy.connections import SolutionConnection
from tespy.networks import Network
from tespy.tools import UserDefinedEquation
from tespy.tools.fluid_properties.solutions import get_solution_pair

pair = get_solution_pair("nh3-water")
X_REF = 0.9995

nw = Network(iterinfo=False)
nw.units.set_defaults(temperature="degC", pressure="bar", heat="kW", power="kW")

absorber = Absorber("absorber")
closer = CycleCloser("solution cycle closer")
pump = Pump("solution pump")
shx = HeatExchanger("solution heat exchanger")
merge = Merge("reflux merge")
generator = Desorber("generator", vapor_state="outlet-equilibrium")
rectifier = Rectifier("rectifier")
solution_valve = Valve("solution valve")
condenser = SimpleHeatExchanger("condenser")
rhx = HeatExchanger("refrigerant heat exchanger")
refrigerant_valve = Valve("refrigerant valve")
evaporator = SimpleHeatExchanger("evaporator")

c = {}
for label, source, outlet, target, inlet in [
    ("1", closer, "out1", pump, "in1"),
    ("2", pump, "out1", shx, "in2"),
    ("3", shx, "out2", merge, "in1"),
    ("3m", merge, "out1", generator, "in1"),
    ("4", generator, "out1", shx, "in1"),
    ("5", shx, "out1", solution_valve, "in1"),
    ("6", solution_valve, "out1", absorber, "in1"),
    ("7", generator, "out2", rectifier, "in1"),
    ("8", rectifier, "out1", condenser, "in1"),
    ("9", rectifier, "out2", merge, "in2"),
    ("10", condenser, "out1", rhx, "in1"),
    ("11", rhx, "out1", refrigerant_valve, "in1"),
    ("12", refrigerant_valve, "out1", evaporator, "in1"),
    ("13", evaporator, "out1", rhx, "in2"),
    ("14", rhx, "out2", absorber, "in2"),
]:
    c[label] = SolutionConnection(source, outlet, target, inlet, label=label)
c["0"] = SolutionConnection(
    absorber, "out1", closer, "in1", label="0", mixing_rule="nh3-water"
)
nw.add_conns(*c.values())

condenser.set_attr(dp=0)
evaporator.set_attr(dp=0, Q=10)
shx.set_attr(dp1=0, dp2=0)
rhx.set_attr(dp1=0, dp2=0)
pump.set_attr(eta_s=0.6)

# the evaporator pressure is the bubble pressure of the refrigerant at the
# evaporation temperature
c["0"].set_attr(T=35, p=pair.p_bubble(263.15, X_REF) / 1e5)
c["1"].set_attr(fluid_balance=True)
c["4"].set_attr(T=120)
c["8"].set_attr(xi=X_REF)
c["10"].set_attr(x=0, T=40)
c["13"].set_attr(x=0.99)


def effectiveness(ude):
    hot_in, cold_in, hot_out = ude.conns
    T_hot_in = hot_in.calc_T()
    return hot_out.calc_T() - (T_hot_in - 0.7 * (T_hot_in - cold_in.calc_T()))


def effectiveness_dependents(ude):
    return {
        "scalars": [[v for conn in ude.conns for v in (conn.p, conn.h)]],
        "vectors": [{
            conn.fluid: {"NH3"} & conn.fluid.is_var for conn in ude.conns
        }],
    }


nw.add_ude(
    UserDefinedEquation(
        "solution heat exchanger effectiveness", effectiveness,
        dependents=effectiveness_dependents, conns=[c["4"], c["2"], c["5"]]
    ),
    UserDefinedEquation(
        "refrigerant heat exchanger effectiveness", effectiveness,
        dependents=effectiveness_dependents, conns=[c["10"], c["13"], c["11"]]
    ),
)
nw.solve("design")
nw.print_results()
print(
    f"status {nw.status}, COP {evaporator.Q.val / generator.Q.val:.4f} "
    f"(CoolSolve 0.4541), circulation ratio "
    f"{c['1'].m.val / c['8'].m.val:.3f} (CoolSolve 6.270)"
)

print("evaporation temperature sweep")
for T_ev in [-15, -10, -5, 0, 5]:
    c["0"].set_attr(p=pair.p_bubble(T_ev + 273.15, X_REF) / 1e5)
    nw.solve("design")
    print(
        f"  T_ev {T_ev} degC: status {nw.status}, "
        f"COP {evaporator.Q.val / generator.Q.val:.4f}, "
        f"circulation ratio {c['1'].m.val / c['8'].m.val:.3f}"
    )
