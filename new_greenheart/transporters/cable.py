import openmdao.api as om


class CableComponent(om.ExplicitComponent):
    """
    Pass-through cable with no losses.
    """
    def setup(self):
        self.add_input('electricity_input', val=0.0, shape_by_conn=True, copy_shape='electricity_output', units='kW')
        self.add_output('electricity_output', val=0.0, shape_by_conn=True, copy_shape='electricity_input', units='kW')

    def compute(self, inputs, outputs):
        outputs['electricity_output'] = inputs['electricity_input']

class Cable():
    def get_performance_model(self):
        return CableComponent()