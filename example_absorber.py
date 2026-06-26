from tespy.components import Sink, Source
from tespy.components import Absorber
from tespy.connections import Connection
from tespy.connections.solutionconnection import SolutionConnection
from tespy.networks import Network
from sorption_reference import *

nw = Network()

poor_src = Source("poor solution source")
vap_src  = Source("vapour source")
rich_snk = Sink("rich solution sink")
absorber  = Absorber("absorber")

c_poor = SolutionConnection(poor_src, "out1", absorber, "in1", label="poor_in")
c_vap  = Connection(vap_src,          "out1", absorber, "in2", label="vapour_in")
c_rich = SolutionConnection(absorber, "out1", rich_snk, "in1", label="rich_out")

nw.add_conns(c_poor, c_vap, c_rich)

c_vap.set_attr(fluid={"H2O": 1}, p=0.01e5, m=1, x=1)
c_poor.set_attr(xi=1 - x_water_poor, T=320)
c_rich.set_attr(h=h_sol_abs_out)

nw.solve("design")
nw.print_results()

c_poor.set_attr(m=10)
c_rich.set_attr(h=None)

nw.solve("design")
nw.print_results()

c_rich.set_attr(T=305)
c_poor.set_attr(m=None)

nw.solve("design")
nw.print_results()

c_vap.set_attr(p=None)
c_rich.set_attr(fluid={"INCOMP::LiBr": 0.50})

nw.solve("design")
nw.print_results()
