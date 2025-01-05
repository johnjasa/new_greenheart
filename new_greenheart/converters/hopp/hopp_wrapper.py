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
    
    This component uses caching to store and retrieve results of the HOPP model
    based on the configuration and project lifetime. The caching mechanism helps
    to avoid redundant computations and speeds up the execution by reusing previously
    computed results when the same configuration is encountered.
    """
    def initialize(self):
        self.options.declare('hopp_config', types=dict)
        self.options.declare('project_lifetime', types=int)

    def setup(self):
        # Outputs
        self.add_output('electricity', val=np.zeros(n_timesteps), units='kW', desc='Power output')
        self.add_output('CapEx', val=0.0, units='USD', desc='Total capital expenditures')
        self.add_output('OpEx', val=0.0, units='USD/year', desc='Total fixed operating costs')

        self.hybrid_interface = setup_hopp(self.options['hopp_config'])

    def compute(self, inputs, outputs):
        # Create a unique hash for the current configuration to use as a cache key
        config_hash = hashlib.md5(str(self.options['hopp_config']).encode('utf-8') + str(self.options['project_lifetime']).encode('utf-8')).hexdigest()

        # Define the keys of interest from the HOPP results that we want to cache
        keys_of_interest = [
            'combined_hybrid_power_production_hopp',
            'capex',
            'opex',
        ]

        # Create a cache directory if it doesn't exist
        if not os.path.exists("cache"):
            os.makedirs("cache")
        cache_file = f"cache/{config_hash}.pkl"

        # Check if the results for the current configuration are already cached
        if os.path.exists(cache_file):
            # Load the cached results
            with open(cache_file, 'rb') as f:
                subset_of_hopp_results = dill.load(f)
        else:
            # Run the HOPP model and get the results
            hopp_results = run_hopp(setup_hopp(self.options['hopp_config']), self.options['project_lifetime'])
            # Extract the subset of results we are interested in
            subset_of_hopp_results = {key: hopp_results[key] for key in keys_of_interest}
            # Cache the results for future use
            with open(cache_file, 'wb') as f:
                dill.dump(subset_of_hopp_results, f)

        # Set the outputs from the cached or newly computed results
        outputs['electricity'] = subset_of_hopp_results["combined_hybrid_power_production_hopp"]
        outputs['CapEx'] = subset_of_hopp_results["capex"]
        outputs['OpEx'] = subset_of_hopp_results["opex"]

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
        Return None; the cost model for HOPP is built in to the performance model.
        """
        return None