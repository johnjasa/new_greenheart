from new_greenheart.converters.hydrogen.electrolyzer_baseclass import ElectrolyzerBaseClass
import openmdao.api as om
import numpy as np
from greenheart.simulation.technologies.hydrogen.electrolysis.PEM_H2_LT_electrolyzer_Clusters import PEM_H2_Clusters
from greenheart.simulation.technologies.hydrogen.electrolysis.PEM_costs_Singlitico_model import PEMCostsSingliticoModel


class ElectrolyzerConfig:
    def __init__(self, config):
        # Dynamically set attributes based on the YAML keys
        for key, value in config.items():
            setattr(self, key, value)

class ElectrolyzerPerformanceModel(om.ExplicitComponent):
    """
    An OpenMDAO component that wraps the PEM electrolyzer model.
    Takes electricity input and outputs hydrogen and oxygen generation rates.
    """
    def initialize(self):
        self.options.declare('electrolyzer', types=PEM_H2_Clusters)

    def setup(self):
        # Define inputs for electricity and outputs for hydrogen and oxygen generation
        self.add_input('electricity', val=0.0, shape_by_conn=True, copy_shape='hydrogen', units='kW')
        self.add_output('hydrogen', val=0.0, shape_by_conn=True, copy_shape='electricity', units='kg/h')

        self.add_input('cluster_size', val=1.0, units='MW')
        self.add_output('total_hydrogen_produced', val=0.0, units='kg')

    def compute(self, inputs, outputs):
        # Run the PEM electrolyzer model using the input power signal
        self.options['electrolyzer'].max_stacks = inputs['cluster_size']
        h2_results, h2_results_aggregates = self.options['electrolyzer'].run(inputs['electricity'])
        
        # Assuming `h2_results` includes hydrogen and oxygen rates per timestep
        outputs['hydrogen'] = h2_results['hydrogen_hourly_production']
        outputs['total_hydrogen_produced'] = h2_results_aggregates['Total H2 Production [kg]']

class ElectrolyzerCostModel(om.ExplicitComponent):
    """
    An OpenMDAO component that computes the cost of a PEM electrolyzer.
    """
    def initialize(self):
        self.options.declare('cost_model', types=PEMCostsSingliticoModel)
        self.options.declare('config_details', types=dict)

    def setup(self):
        # Define inputs: electrolyzer capacity and reference cost
        config_details = self.options['config_details']
        self.add_input('P_elec', val=config_details['cluster_size_mw'], units='MW', desc='Nominal capacity of the electrolyzer')
        self.add_input('RC_elec', val=config_details['electrolyzer_cost'], units='MUSD/GW', desc='Reference cost of the electrolyzer')

        # Define outputs: CapEx and OpEx costs
        self.add_output('CapEx', val=0.0, units='MUSD', desc='Capital expenditure')
        self.add_output('OpEx', val=0.0, units='MUSD', desc='Operational expenditure')

    def compute(self, inputs, outputs):
        # Call the cost model to compute costs
        P_elec = inputs['P_elec'] * 1.e-3  # Convert MW to GW
        RC_elec = inputs['RC_elec']
        
        cost_model = self.options['cost_model']
        capex, opex = cost_model.run(P_elec, RC_elec)
        
        outputs['CapEx'] = capex
        outputs['OpEx'] = opex

class ElectrolyzerFinanceModel(om.ExplicitComponent):
    """
    Placeholder for the financial model of the PEM electrolyzer.
    """
    def setup(self):
        self.add_output('LCOH', val=0.0, units='USD/kg', desc='Levelized cost of hydrogen')

    def compute(self, inputs, outputs):
        outputs['LCOH'] = 4.11  # Placeholder value

class PEMElectrolyzer(ElectrolyzerBaseClass):
    """
    Wrapper class for the PEM electrolyzer in the new_greenheart framework, inheriting from ElectrolyzerBaseClass.
    """
    def __init__(self, plant_config, tech_config):
        """
        Initialize the PEMElectrolyzer.

        Args:
            config (ElectrolyzerConfig): Configuration for the PEM electrolyzer instance.
        """
        super().__init__(plant_config, tech_config)
        electrolyzer_config = ElectrolyzerConfig(tech_config['details'])
        self.electrolyzer = PEM_H2_Clusters(
            electrolyzer_config.cluster_size_mw,
            electrolyzer_config.plant_life,
            **electrolyzer_config.model_parameters
        )
        self.cost_model = PEMCostsSingliticoModel(elec_location=1)

    def get_performance_model(self):
        """
        Describes how the electrolyzer performs its function.

        Returns an OpenMDAO System.
        """
        return ElectrolyzerPerformanceModel(electrolyzer=self.electrolyzer)

    def get_cost_model(self):
        """
        Placeholder for electrolyzer cost model.
        """
        return ElectrolyzerCostModel(cost_model=self.cost_model, config_details=self.tech_config['details'])

    def get_control_strategy(self):
        """
        Placeholder for control strategy.
        """
        pass

    def get_financial_model(self):
        """
        Placeholder for financial model.
        """
        return ElectrolyzerFinanceModel()

    def post_process(self):
        """
        Post-process the results from the electrolyzer simulation.
        """
        pass