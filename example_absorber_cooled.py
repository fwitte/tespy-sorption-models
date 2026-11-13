from tespy.components import Sink, Source
from tespy.components import CooledAbsorber
from tespy.connections import Connection
from tespy.connections.solutionconnection import SolutionConnection
from tespy.networks import Network
from sorption_reference import *

nw = Network()

poor_src = Source("poor solution source")
vap_src  = Source("vapour source")
rich_snk = Sink("rich solution sink")
cool_src = Source("cooling water source")
cool_snk = Sink("cooling water sink")
absorber = CooledAbsorber("absorber")

c_poor = SolutionConnection(poor_src, "out1", absorber, "in1", label="poor_in", mixing_rule="libr-water")
c_cool_in = Connection(cool_src, "out1", absorber, "in2", label="cooling_in")
c_vap  = Connection(vap_src, "out1", absorber, "in3", label="vapour_in")
c_rich = SolutionConnection(absorber, "out1", rich_snk, "in1", label="rich_out")
c_cool_out = Connection(absorber, "out2", cool_snk, "in1", label="cooling_out")

nw.add_conns(c_poor, c_cool_in, c_vap, c_rich, c_cool_out)

absorber.set_attr(dp2=0)
c_poor.set_attr(xi=1 - x_water_poor, T=320, m=10)
c_vap.set_attr(fluid={"H2O": 1}, p=p_evap, m=1, x=1)
c_cool_in.set_attr(fluid={"H2O": 1}, p=2e5, T=293.15)
c_cool_out.set_attr(T=298.15)

nw.solve("design")
nw.print_results()

# replace the vapour mass flow specification with the lower terminal
# temperature difference between rich solution outlet and cooling water inlet
c_vap.set_attr(m=None)
absorber.set_attr(ttd_l=13)

nw.solve("design")
nw.print_results()

# replace the terminal temperature difference with a heat flow specification
Q_design = absorber.Q.val_SI
absorber.set_attr(ttd_l=None, Q=Q_design)

nw.solve("design")
nw.print_results()
