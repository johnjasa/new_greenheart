from new_greenheart.core.baseclasses.converter_base_class import ConverterBaseClass
from hopp.simulation.technologies.wind.floris import Floris
from hopp.simulation.technologies.wind.wind_plant import WindPlant
from hopp.simulation.technologies.resource import WindResource
from hopp.simulation.technologies.sites import SiteInfo, flatirons_site

import openmdao.api as om

n_timesteps = 8760


class WindConfig:
    def __init__(self):
        self.num_turbines = 20
        self.turbine_rating_kw = 3000.0
        self.rotor_diameter = 120.0
        self.hub_height = 100.0
        self.layout_mode = "grid"
        self.model_name = "pysam"
        self.model_input_file = None
        self.layout_params = {
            "border_spacing": 0.5,          # spacing along border = (1 + border_spacing) * min spacing
            "border_offset": 0.5,           # turbine border spacing offset as ratio of border spacing (0, 1)
            "grid_angle": 2.0,              # turbine inner grid rotation (0, pi) [radians]
            "grid_aspect_power": 4.0,       # grid aspect ratio [cols / rows] = 2^grid_aspect_power
            "row_phase_offset": 0.2         # inner grid phase offset (0,1) (20% suggested)
        }
        self.rating_range_kw = (1000, 5000)
        self.floris_config = None
        self.operational_losses = 10.0
        self.timestep = (1, 60)
        self.fin_model = "default"
        self.name = "UtilityScaleWindPlant"



class WindPlantComponent(om.ExplicitComponent):
    """
    An OpenMDAO component that wraps a WindPlant model.
    It takes wind parameters as input and outputs power generation data.
    """
    def initialize(self):
        self.options.declare('wind_plant', types=WindPlant)

    def setup(self):
        # Outputs: Power generation in kW
        self.add_output('electricity', val=0.0, shape=n_timesteps, units='kW', desc='Power output from WindPlant')

    def compute(self, inputs, outputs):
        # Assumes the WindPlant instance has a method to simulate and return power output
        self.options['wind_plant'].simulate_power(30)
        outputs['electricity'] = self.options['wind_plant']._system_model.value("gen")

class WindPlantConverter(ConverterBaseClass):
    """
    Wrapper class for WindPlant in the new_greenheart framework, inheriting from ConverterBaseClass.
    """
    def __init__(self, energy_resources, site_info=SiteInfo(flatirons_site), config=WindConfig()):
        """
        Initialize the WindPlantConverter.

        Args:
            energy_resources (dict): Environmental parameters, e.g., wind speed, temperature.
            site_info (SiteInfo): Site information for the wind plant (location, elevation, etc.).
            config (WindConfig): Configuration for the WindPlant instance.
        """
        super().__init__(energy_resources)
        self.site = site_info
        self.config = config
        self.wind_plant = WindPlant(self.site, self.config)

    def define_outputs(self):
        """
        Define the outputs for the wind plant.

        Returns:
            dict: Output dictionary with electricity generation.
        """
        # The output value here is representative; typically, the value might be calculated dynamically.
        return {'electricity': {'value': 1000.0, 'units': 'kW'}}

    def get_performance_model(self):
        """
        Describes how the wind plant performs its function.

        Returns:
            OpenMDAO System: The performance model as an OpenMDAO component.
        """
        return WindPlantComponent(wind_plant=self.wind_plant)

    def get_cost_model(self):
        """
        Describes the costs associated with the wind plant.

        This can be extended with a financial cost model.

        Returns:
            Optional[OpenMDAO System]: Placeholder for financial model in OpenMDAO.
        """
        # Implement a financial cost model if available, or leave as placeholder
        pass

    def get_control_strategy(self):
        """
        Describes the control strategy for the wind plant.

        Returns:
            Optional[OpenMDAO System]: Placeholder for a control strategy.
        """
        # Control strategy can involve dispatch models or other control optimizations if defined
        pass

    def get_financial_model(self):
        """
        Describes the financial model for the wind plant.

        Returns:
            Optional[OpenMDAO System]: Financial model in OpenMDAO if available.
        """
        # If a financial model like SingleOwner is defined, integrate it here
        pass

    def post_process(self):
        """
        Post-process the results from the wind plant simulation.

        This function could include summary statistics, data exports, or other processing.
        """
        power_output = self.wind_plant.system_capacity_kw
        print(f"Wind plant post-process: total power output was {power_output} kW.")
