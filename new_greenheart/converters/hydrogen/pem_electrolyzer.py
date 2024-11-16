from new_greenheart.core.baseclasses.converter_base_class import ConverterBaseClass
import openmdao.api as om
import numpy as np
from greenheart.simulation.technologies.hydrogen.electrolysis.PEM_H2_LT_electrolyzer_Clusters import PEM_H2_Clusters


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

    def compute(self, inputs, outputs):
        # Run the PEM electrolyzer model using the input power signal
        h2_results, _ = self.options['electrolyzer'].run(inputs['electricity'])
        
        # Assuming `h2_results` includes hydrogen and oxygen rates per timestep
        outputs['hydrogen'] = h2_results['hydrogen_hourly_production']

class PEMElectrolyzer(ConverterBaseClass):
    """
    Wrapper class for the PEM electrolyzer in the new_greenheart framework, inheriting from ConverterBaseClass.
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
        pass

    def get_control_strategy(self):
        """
        Placeholder for control strategy.
        """
        pass

    def get_financial_model(self):
        """
        Placeholder for financial model.
        """
        pass

    def post_process(self):
        """
        Post-process the results from the electrolyzer simulation.
        """
        pass