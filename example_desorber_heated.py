from tespy.components import Sink, Source
from tespy.components import HeatedDesorber
from tespy.connections import Connection
from tespy.connections.solutionconnection import SolutionConnection
from tespy.networks import Network
from sorption_reference import *

nw = Network()

rich_src = Source("rich solution source")
poor_snk = Sink("poor solution sink")
vap_snk  = Sink("vapour sink")
heat_src = Source("heating water source")
heat_snk = Sink("heating water sink")
desorber = HeatedDesorber("desorber")

c_rich = SolutionConnection(rich_src, "out1", desorber, "in1", label="rich_in", mixing_rule="libr-water")
c_heat_in = Connection(heat_src, "out1", desorber, "in2", label="heating_in")
c_poor = SolutionConnection(desorber, "out1", poor_snk, "in1", label="poor_out")
c_heat_out = Connection(desorber, "out2", heat_snk, "in1", label="heating_out")
c_vap  = Connection(desorber, "out3", vap_snk, "in1", label="vapour_out")

nw.add_conns(c_rich, c_heat_in, c_poor, c_heat_out, c_vap)

desorber.set_attr(dp2=0)
c_rich.set_attr(xi=1 - x_water_rich, p=p_cond, m=10, h=h_pump_out)
c_poor.set_attr(T=350)
c_vap.set_attr(fluid={"H2O": 1})
c_heat_in.set_attr(fluid={"H2O": 1}, p=5e5, T=370)
c_heat_out.set_attr(T=360)

nw.solve("design")
nw.print_results()

# replace the poor solution temperature specification with the upper terminal
# temperature difference between heating water inlet and poor solution outlet
c_poor.set_attr(T=None)
desorber.set_attr(ttd_u=20)

nw.solve("design")
nw.print_results()

# replace the terminal temperature difference with a heat flow specification
Q_design = desorber.Q.val_SI
desorber.set_attr(ttd_u=None, Q=Q_design)

nw.solve("design")
nw.print_results()
