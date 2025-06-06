import numpy as np
import openmdao.api as om
from attrs import define, field
from greenheart.simulation.technologies.hydrogen.electrolysis.run_h2_PEM import run_h2_PEM
from greenheart.simulation.technologies.hydrogen.electrolysis.H2_cost_model import (
    basic_H2_cost_model,
)
from greenheart.simulation.technologies.hydrogen.electrolysis.PEM_costs_Singlitico_model import (
    PEMCostsSingliticoModel,
)
from greenheart.simulation.technologies.hydrogen.electrolysis.PEM_H2_LT_electrolyzer_Clusters import PEM_H2_Clusters
from greenheart.tools.eco.utilities import ceildiv

from new_greenheart.converters.hydrogen.electrolyzer_baseclass import (
    ElectrolyzerPerformanceBaseClass,
    ElectrolyzerCostBaseClass,
    ElectrolyzerFinanceBaseClass
)
from new_greenheart.core.utilities import (
    BaseConfig,
    merge_shared_cost_inputs,
    merge_shared_performance_inputs
)


@define
class ElectrolyzerPerformanceModelConfig(BaseConfig):
    cluster_size_mw: float = field()
    plant_life: int = field()
    eol_eff_percent_loss: float = field()
    uptime_hours_until_eol: int = field()
    include_degradation_penalty: bool = field()
    turndown_ratio: float = field()


class ElectrolyzerPerformanceModel(ElectrolyzerPerformanceBaseClass):
    """
    An OpenMDAO component that wraps the PEM electrolyzer model.
    Takes electricity input and outputs hydrogen and oxygen generation rates.
    """
    def setup(self):
        super().setup()
        self.config = ElectrolyzerPerformanceModelConfig.from_dict(
            merge_shared_performance_inputs(self.options["tech_config"]["model_inputs"])
        )
        self.electrolyzer = PEM_H2_Clusters(
            self.config.cluster_size_mw,
            self.config.plant_life,
            self.config.eol_eff_percent_loss,
            self.config.uptime_hours_until_eol,
            self.config.include_degradation_penalty,
            self.config.turndown_ratio,
        )
        self.add_input('cluster_size', val=1.0, units='MW')

    def compute(self, inputs, outputs):
        # Run the PEM electrolyzer model using the input power signal
        self.electrolyzer.max_stacks = inputs['cluster_size']
        h2_results, h2_results_aggregates = self.electrolyzer.run(inputs['electricity'])
        
        # Assuming `h2_results` includes hydrogen and oxygen rates per timestep
        outputs['hydrogen'] = h2_results['hydrogen_hourly_production']
        outputs['total_hydrogen_produced'] = h2_results_aggregates['Total H2 Production [kg]']


@define
class ElectrolyzeCostModelConfig(BaseConfig):
    cluster_size_mw: float = field()
    electrolyzer_cost: float = field()


class ElectrolyzerCostModel(ElectrolyzerCostBaseClass):
    """
    An OpenMDAO component that computes the cost of a PEM electrolyzer.
    """
    def setup(self):
        super().setup()
        self.cost_model = PEMCostsSingliticoModel(elec_location=1)
        # Define inputs: electrolyzer capacity and reference cost
        self.config = ElectrolyzeCostModelConfig.from_dict(
            merge_shared_cost_inputs(self.options['tech_config']['model_inputs'])
        )
        self.add_input('P_elec', val=self.config.cluster_size_mw, units='MW', desc='Nominal capacity of the electrolyzer')
        self.add_input('RC_elec', val=self.config.electrolyzer_cost, units='MUSD/GW', desc='Reference cost of the electrolyzer')

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
