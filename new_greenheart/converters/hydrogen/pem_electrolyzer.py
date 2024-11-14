from new_greenheart.core.baseclasses.converter_base_class import ConverterBaseClass
import openmdao.api as om
import numpy as np
from greenheart.simulation.technologies.hydrogen.electrolysis.PEM_H2_LT_electrolyzer_Clusters import PEM_H2_Clusters


class ElectrolyzerConfig:
    def __init__(self):
        self.cluster_size_mw = 1.0  # MW
        self.plant_life = 30  # years
        self.model_parameters = {
            "eol_eff_percent_loss": 10,  # percent
            "uptime_hours_until_eol": 77600,  # hours until end-of-life
            "include_degradation_penalty": True,
            "turndown_ratio": 0.1,
        }

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
        self.add_output('hydrogen', val=0.0, shape_by_conn=True, copy_shape='electricity', units='kg/s')

    def compute(self, inputs, outputs):
        # Run the PEM electrolyzer model using the input power signal
        power_signal = np.full((8760,), inputs['electricity'])  # Example constant power
        h2_results, _ = self.options['electrolyzer'].run(power_signal)
        
        # Assuming `h2_results` includes hydrogen and oxygen rates per timestep
        outputs['hydrogen'] = h2_results['hydrogen_hourly_production'] / 3600  # Convert from kg/h to kg/s

class PEMElectrolyzer(ConverterBaseClass):
    """
    Wrapper class for the PEM electrolyzer in the new_greenheart framework, inheriting from ConverterBaseClass.
    """
    def __init__(self, config=ElectrolyzerConfig()):
        """
        Initialize the PEMElectrolyzer.

        Args:
            config (ElectrolyzerConfig): Configuration for the PEM electrolyzer instance.
        """
        super().__init__(energy_resources={'electricity': 0.0})
        self.config = config
        self.electrolyzer = PEM_H2_Clusters(
            self.config.cluster_size_mw,
            self.config.plant_life,
            **self.config.model_parameters
        )

    def define_inputs(self):
        """
        Define the inputs for the electrolyzer.
        """
        return {'electricity': {'value': 0.0, 'units': 'kW'}}

    def define_outputs(self):
        """
        Define the outputs for the electrolyzer.
        """
        return {'hydrogen': {'value': 0.0, 'units': 'kg/s'},
                'oxygen': {'value': 0.0, 'units': 'kg/s'}}

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