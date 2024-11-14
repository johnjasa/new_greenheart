import openmdao.api as om


class Pipe(om.ExplicitComponent):
    """
    Pass-through pipe with no losses.
    """
    def setup(self):
        self.add_input('resource_output', val=0.0, shape_by_conn=True, copy_shape='electricity_input', units='kg/s')
        self.add_output('resource_output', val=0.0, shape_by_conn=True, copy_shape='resource_input', units='kg/s')

    def compute(self, inputs, outputs):
        outputs['resource_output'] = inputs['resource_input']