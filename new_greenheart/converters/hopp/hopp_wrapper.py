import hashlib
import dill
import os
import numpy as np
import openmdao.api as om
from new_greenheart.core.baseclasses.converter_base_class import ConverterBaseClass
from new_greenheart.converters.hopp.hopp_mgmt import setup_hopp, run_hopp


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
        config_hash = hashlib.md5(str(self.options['hopp_config']).encode('utf-8') + str(self.options['project_lifetime']).encode('utf-8')).hexdigest()

        # make a cache dir
        if not os.path.exists("cache"):
            os.makedirs("cache")
        cache_file = f"cache/{config_hash}.pkl"

        if os.path.exists(cache_file):
            with open(cache_file, 'rb') as f:
                subset_of_hopp_results = dill.load(f)
        else:
            hopp_results = run_hopp(setup_hopp(self.options['hopp_config']), self.options['project_lifetime'])
            subset_of_hopp_results = {key: hopp_results[key] for key in ['combined_hybrid_power_production_hopp']}
            with open(cache_file, 'wb') as f:
                dill.dump(subset_of_hopp_results, f)

        outputs['electricity'] = subset_of_hopp_results["combined_hybrid_power_production_hopp"]

class HOPPCostModel(om.ExplicitComponent):
    """
    A simple OpenMDAO component that represents the costs associated with a HOPP model.
    """
    def initialize(self):
        self.options.declare('config', types=dict)

    def setup(self):
        # Outputs
        self.add_output('CapEx', val=0.0, units='USD', desc='Total capital expenditures')
        self.add_output('OpEx', val=0.0, units='USD/year', desc='Total fixed operating costs')

    def compute(self, inputs, outputs):
        # Placeholder for cost model
        outputs['CapEx'] = 0.0
        outputs['OpEx'] = 0.0

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
        return HOPPCostModel(config={})