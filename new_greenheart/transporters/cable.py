import openmdao.api as om
from new_greenheart.core.baseclasses.transport_base_class import TransportBaseClass


class CableComponent(om.ExplicitComponent):
    """
    Pass-through cable with no losses.
    """
    def setup(self):
        self.add_input('electricity_input', val=0.0, shape_by_conn=True, copy_shape='electricity_output', units='kW')
        self.add_output('electricity_output', val=0.0, shape_by_conn=True, copy_shape='electricity_input', units='kW')

    def compute(self, inputs, outputs):
        outputs['electricity_output'] = inputs['electricity_input']

class Cable(TransportBaseClass):
    def get_performance_model(self):
        return CableComponent()