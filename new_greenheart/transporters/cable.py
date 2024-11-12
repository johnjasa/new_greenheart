import openmdao.api as om

class Cable(om.ExplicitComponent):
    def setup(self):
        self.add_input('electricity_input', val=0.0, units='kW')
        self.add_output('electricity_output', val=0.0, units='kW')

    def compute(self, inputs, outputs):
        outputs['electricity_output'] = inputs['electricity_input']