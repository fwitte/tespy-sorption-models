from tespy.components.component import Component
from tespy.tools.fluid_properties.mixtures import xsat_pT_incomp_solution


class Sorption(Component):

    def preprocess(self, num_vars):
        self.h2o = "water"
        super().preprocess(num_vars)

    def get_mandatory_constraints(self):
        constraints = {
            'mass_flow_constraints': {
                'func': self.mass_flow_func, 'deriv': self.mass_flow_deriv,
                'constant_deriv': True,# 'latex': self.mass_flow_func_doc,
                'num_eq': 1
            },
            'fluid_constraints': {
                'func': self.fluid_func, 'deriv': self.fluid_deriv,
                'constant_deriv': False,# 'latex': self.fluid_func_doc,
                'num_eq': 1
            },
            'pressure_constraints': {
                'func': self.pressure_equality_func,
                'deriv': self.pressure_equality_deriv,
                'constant_deriv': True,
                'latex': self.pressure_equality_func_doc,
                'num_eq': 2
            },
            "saturation_constraints_libr": {
                "func": self.saturated_solution_libr_func,
                "deriv": self.saturated_solution_libr_deriv,
                "constant_deriv": False,
                "num_eq": 1
            },
        }
        print(self.outl[0].solvent)
        print(self.outl[0].fluid.is_var)
        if self.outl[0].solvent in self.outl[0].fluid.is_var:
            constraints["saturation_constraints_water"] = {
                "func": self.saturated_solution_water_func,
                "deriv": self.saturated_solution_water_deriv,
                "constant_deriv": False,
                "num_eq": 1
            }
        print(sum(constraint["num_eq"] for constraint in constraints.values()))
        return constraints

    def mass_flow_func(self):
        return sum([c.m.val_SI for c in self.inl] + [-c.m.val_SI for c in self.outl])

    def mass_flow_deriv(self, k):
        for c in self.inl:
            if c.m.is_var:
                self.jacobian[k, c.m.J_col] = 1

        for c in self.outl:
            if c.m.is_var:
                self.jacobian[k, c.m.J_col] = -1

    def fluid_func(self):
        return (
            self.inl[0].m.val_SI * self.inl[0].fluid.val["LiBr"]
            - self.outl[0].m.val_SI * self.outl[0].fluid.val["LiBr"]
        )

    def fluid_deriv(self, increment_filter, k):
        outl = self.outl[0]
        inl = self.inl[0]

        if inl.m.is_var:
            self.jacobian[k, inl.m.J_col] = inl.fluid.val[inl.solvent]
        if inl.solvent in inl.fluid.is_var:
            self.jacobian[k, inl.fluid.J_col[inl.solvent]] = inl.m.val_SI
        if outl.m.is_var:
            self.jacobian[k, outl.m.J_col] = -outl.fluid.val[outl.solvent]
        if outl.solvent in outl.fluid.is_var:
            self.jacobian[k, outl.fluid.J_col[outl.solvent]] = -outl.m.val_SI

    def saturated_solution_water_func(self):
        outl = self.outl[0]
        return 1 - outl.fluid.val[outl.solvent] - outl.fluid.val[self.h2o]

    def saturated_solution_water_deriv(self, increment_filter, k):
        outl = self.outl[0]
        if self.h2o in outl.fluid.is_var:
            self.jacobian[k, outl.fluid.J_col[self.h2o]] = -1
        if outl.solvent in outl.fluid.is_var:
            self.jacobian[k, outl.fluid.J_col[outl.solvent]] = -1

    def saturated_solution_libr_func(self):
        outl = self.outl[0]
        x_previous = outl.fluid.val[outl.solvent]
        T = outl.calc_T()
        x_libr = xsat_pT_incomp_solution(outl.p.val_SI, T, outl.fluid_data, solvent=outl.solvent, x0=x_previous)
        outl.fluid_data[outl.solvent]["wrapper"].AS.set_mass_fractions([x_previous])
        return x_libr - outl.fluid.val[outl.solvent]

    def saturated_solution_libr_deriv(self, increment_filter, k):
        outl = self.outl[0]
        if outl.p.is_var:
            deriv = self.numeric_deriv(self.saturated_solution_libr_func, "p", outl)
            self.jacobian[k, outl.p.J_col] = deriv
        if outl.h.is_var:
            deriv = self.numeric_deriv(self.saturated_solution_libr_func, "h", outl)
            self.jacobian[k, outl.h.J_col] = deriv
        if outl.solvent in outl.fluid.is_var:
            self.jacobian[k, outl.fluid.J_col[outl.solvent]] = self.numeric_deriv(self.saturated_solution_libr_func, outl.solvent, outl)

    def heat_func(self):
        return self.calc_Q() - self.Q.val

    def heat_deriv(self, increment_filter, k):
        for c in self.inl:
            if self.is_variable(c.m):
                self.jacobian[k, c.m.J_col] = -c.h.val_SI
            if self.is_variable(c.h):
                self.jacobian[k, c.h.J_col] = -c.m.val_SI

        for c in self.outl:
            if self.is_variable(c.m):
                self.jacobian[k, c.m.J_col] = c.h.val_SI
            if self.is_variable(c.h):
                self.jacobian[k, c.h.J_col] = c.m.val_SI

    def calc_Q(self):
        return (
            sum([c.h.val_SI * c.m.val_SI for c in self.outl])
            - sum([c.h.val_SI * c.m.val_SI for c in self.inl])
        )

    def calc_parameters(self):
        self.Q.val = self.calc_Q()

    def propagate_to_target(self, branch):
        return
