import openmdao.api as om
from new_greenheart.core.baseclasses.transport_base_class import TransportBaseClass


class PipeComponent(om.ExplicitComponent):
    """
    Pass-through pipe with no losses.
    """
    def setup(self):
        self.add_input('hydrogen_input', val=0.0, shape_by_conn=True, copy_shape='hydrogen_output', units='kg/s')
        self.add_output('hydrogen_output', val=0.0, shape_by_conn=True, copy_shape='hydrogen_input', units='kg/s')

    def compute(self, inputs, outputs):
        outputs['hydrogen_output'] = inputs['hydrogen_input']

class Pipe(TransportBaseClass):
    def get_performance_model(self):
        return PipeComponent()