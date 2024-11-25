from new_greenheart.core.baseclasses.converter_base_class import ConverterBaseClass
import openmdao.api as om
import numpy as np
from new_greenheart.converters.hopp.hopp_mgmt import setup_hopp, run_hopp
from hopp.utilities import load_yaml
from greenheart.tools.eco.utilities import convert_relative_to_absolute_path


n_timesteps = 8760

class HOPPComponent(om.ExplicitComponent):
    """
    A simple OpenMDAO component that represents a HOPP model.
    """
    def initialize(self):
        self.options.declare('hopp_config', types=dict)
        self.options.declare('project_lifetime', types=int)

    def setup(self):
        # Outputs
        self.add_output('electricity', val=np.zeros(n_timesteps), units='kW', desc='Power output')

        self.hybrid_interface = setup_hopp(self.options['hopp_config'])

    def compute(self, inputs, outputs):
        hopp_results = run_hopp(setup_hopp(self.options['hopp_config']), self.options['project_lifetime'])
        
        outputs['electricity'] = hopp_results["combined_hybrid_power_production_hopp"]

class HOPPModel(ConverterBaseClass):
    """
    Simple HOPP wrapper class.
    """
    def __init__(self, plant_config, tech_config):
        super().__init__(plant_config, tech_config)

    def get_performance_model(self):
        """
        Describes how the HOPP model performs its function.
        
        Returns an OpenMDAO System.
        """
        return HOPPComponent(hopp_config=self.tech_config['performance_model']['config'], project_lifetime=self.plant_config['plant']['plant_life'])

    def get_cost_model(self):
        """
        Describes the costs associated with the HOPP model.

        Returns an OpenMDAO System.
        """
        return None