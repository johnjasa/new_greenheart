from new_greenheart.converters.hydrogen.electrolyzer_baseclass import ElectrolyzerBaseClass

import openmdao.api as om


class ElectrolyzerPerformanceModel(om.ExplicitComponent):
    def setup(self):
        self.add_input('electricity', val=0.0, shape_by_conn=True, copy_shape='hydrogen', units='kW')
        self.add_input('water', val=0.0, shape_by_conn=True, copy_shape='hydrogen', units='kg/s')
        self.add_output('hydrogen', val=0.0, shape_by_conn=True, copy_shape='electricity', units='kg/s')
        self.add_output('oxygen', val=0.0, shape_by_conn=True, copy_shape='electricity', units='kg/s')

    def compute(self, inputs, outputs):
        electricity = inputs['electricity']
        water = inputs['water']
        
        # Simple model: assume 1 kW electricity produces 0.1 kg/s hydrogen and 0.8 kg/s oxygen
        outputs['hydrogen'] = 0.1 * electricity
        outputs['oxygen'] = 0.8 * electricity

class DummyElectrolyzer(ElectrolyzerBaseClass):
    def __init__(self, plant_config, tech_config):
        super().__init__(plant_config, tech_config)

    def get_performance_model(self):
        """
        Describes how the converter performs its function.
        
        This would be the equations that describe how the converter transforms
        one resource into another.

        Returns an OpenMDAO System.
        """
        return ElectrolyzerPerformanceModel()