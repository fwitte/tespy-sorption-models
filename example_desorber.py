from tespy.components import Sink, Source
from tespy.components import Desorber
from tespy.connections import Connection
from tespy.connections.solutionconnection import SolutionConnection
from tespy.networks import Network
from sorption_reference import *

nw = Network()

rich_src = Source("rich solution source")
poor_snk = Sink("poor solution sink")
vap_snk  = Sink("vapour sink")
desorber  = Desorber("desorber")

c_rich = SolutionConnection(rich_src, "out1", desorber, "in1",  label="rich_in")
c_poor = SolutionConnection(desorber, "out1", poor_snk, "in1",  label="poor_out")
c_vap  = Connection(desorber,         "out2", vap_snk,  "in1",  label="vapour_out")

nw.add_conns(c_rich, c_poor, c_vap)

c_rich.set_attr(xi=1 - x_water_rich, p=p_cond, m=10, h=h_pump_out)
c_poor.set_attr(h=h_poor)
c_vap.set_attr(fluid={"H2O": 1}, x=1)

nw.max_iter = 40
nw.solve("design")
nw.print_results()

c_vap.set_attr(x=None, T=320)

nw.solve("design")
nw.print_results()

c_poor.set_attr(m=9, h=None)

nw.solve("design")
nw.print_results()

c_poor.set_attr(m=None, T=350)

nw.solve("design")
nw.print_results()

c_poor.set_attr(fluid={"INCOMP::LiBr": 0.7})
c_rich.set_attr(p=None)

nw.solve("design")
nw.print_results()
