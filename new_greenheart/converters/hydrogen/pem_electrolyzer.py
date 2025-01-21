import numpy as np
import openmdao.api as om
from greenheart.simulation.technologies.hydrogen.electrolysis.run_h2_PEM import run_h2_PEM
from greenheart.simulation.technologies.hydrogen.electrolysis.H2_cost_model import (
    basic_H2_cost_model,
)
from greenheart.simulation.technologies.hydrogen.electrolysis.PEM_costs_Singlitico_model import (
    PEMCostsSingliticoModel,
)
from greenheart.simulation.technologies.hydrogen.electrolysis.PEM_H2_LT_electrolyzer_Clusters import PEM_H2_Clusters
from greenheart.tools.eco.utilities import ceildiv

from new_greenheart.converters.hydrogen.electrolyzer_baseclass import ElectrolyzerPerformanceBaseClass, ElectrolyzerCostBaseClass, ElectrolyzerFinanceBaseClass


class ElectrolyzerConfig:
    def __init__(self, config):
        # Dynamically set attributes based on the YAML keys
        for key, value in config.items():
            setattr(self, key, value)

class ElectrolyzerPerformanceModel(ElectrolyzerPerformanceBaseClass):
    """
    An OpenMDAO component that wraps the PEM electrolyzer model.
    Takes electricity input and outputs hydrogen and oxygen generation rates.
    """
    def setup(self):
        super().setup()
        tech_config = self.options['tech_config']
        electrolyzer_config = ElectrolyzerConfig(tech_config['details'])
        self.electrolyzer = PEM_H2_Clusters(
            electrolyzer_config.cluster_size_mw,
            electrolyzer_config.plant_life,
            **electrolyzer_config.model_parameters
        )
        self.add_input('cluster_size', val=1.0, units='MW')

    def compute(self, inputs, outputs):
        # Run the PEM electrolyzer model using the input power signal
        self.electrolyzer.max_stacks = inputs['cluster_size']
        h2_results, h2_results_aggregates = self.electrolyzer.run(inputs['electricity'])
        
        # Assuming `h2_results` includes hydrogen and oxygen rates per timestep
        outputs['hydrogen'] = h2_results['hydrogen_hourly_production']
        outputs['total_hydrogen_produced'] = h2_results_aggregates['Total H2 Production [kg]']

class ElectrolyzerCostModel(ElectrolyzerCostBaseClass):
    """
    An OpenMDAO component that computes the cost of a PEM electrolyzer.
    """
    def setup(self):
        super().setup()
        self.cost_model = PEMCostsSingliticoModel(elec_location=1)
        # Define inputs: electrolyzer capacity and reference cost
        config_details = self.options['tech_config']['details']
        self.add_input('P_elec', val=config_details['cluster_size_mw'], units='MW', desc='Nominal capacity of the electrolyzer')
        self.add_input('RC_elec', val=config_details['electrolyzer_cost'], units='MUSD/GW', desc='Reference cost of the electrolyzer')

    def compute(self, inputs, outputs):
        # Call the cost model to compute costs
        P_elec = inputs['P_elec'] * 1.e-3  # Convert MW to GW
        RC_elec = inputs['RC_elec']
        
        cost_model = self.cost_model
        capex, opex = cost_model.run(P_elec, RC_elec)
        
        outputs['CapEx'] = capex * 1.e-6  # Convert to MUSD
        outputs['OpEx'] = opex * 1.e-6  # Convert to MUSD

class ElectrolyzerFinanceModel(ElectrolyzerFinanceBaseClass):
    """
    Placeholder for the financial model of the PEM electrolyzer.
    """
    def compute(self, inputs, outputs):
        outputs['LCOH'] = 4.11  # Placeholder value