from new_greenheart.core.baseclasses.converter_base_class import ConverterBaseClass
from hopp.simulation.technologies.wind.floris import Floris
from hopp.simulation.technologies.wind.wind_plant import WindPlant
from hopp.simulation.technologies.sites import SiteInfo, flatirons_site

import openmdao.api as om

n_timesteps = 8760

class WindConfig:
    def __init__(self, config_details):
        # Dynamically set attributes based on the YAML keys
        for key, value in config_details.items():
            setattr(self, key, value)


class WindPlantComponent(om.ExplicitComponent):
    """
    An OpenMDAO component that wraps a WindPlant model.
    It takes wind parameters as input and outputs power generation data.
    """
    def initialize(self):
        self.options.declare('wind_plant', types=WindPlant)
        self.options.declare('plant_life')

    def setup(self):
        # Outputs: Power generation in kW
        self.add_output('electricity', val=0.0, shape=n_timesteps, units='kW', desc='Power output from WindPlant')

    def compute(self, inputs, outputs):
        # Assumes the WindPlant instance has a method to simulate and return power output
        plant_life = self.options['plant_life']
        self.options['wind_plant'].simulate_power(plant_life)
        outputs['electricity'] = self.options['wind_plant']._system_model.value("gen")


class WindPlantCostComponent(om.ExplicitComponent):
    """
    An OpenMDAO component that calculates the capital expenditure (CapEx) for a wind plant.

    Just a placeholder for now, but can be extended with more detailed cost models.
    """
    def initialize(self):
        self.options.declare('cost_per_kw', types=float, default=1500.0, desc='Cost per kW of installed capacity')

    def setup(self):
        # Inputs: Number of turbines and turbine rating in kW
        self.add_input('num_turbines', val=0, desc='Number of wind turbines')
        self.add_input('turbine_rating_kw', val=0.0, units='kW', desc='Rating of each turbine in kW')

        # Output: Capital expenditure in USD
        self.add_output('CapEx', val=0.0, units='USD', desc='Capital expenditure for the wind plant')
        self.add_output('OpEx', val=0.0, units='USD/year', desc='Operational expenditure for the wind plant')

    def compute(self, inputs, outputs):
        num_turbines = inputs['num_turbines']
        turbine_rating_kw = inputs['turbine_rating_kw']
        cost_per_kw = self.options['cost_per_kw']

        # Calculate CapEx
        total_capacity_kw = num_turbines * turbine_rating_kw
        outputs['CapEx'] = total_capacity_kw * cost_per_kw
        outputs['OpEx'] = 0.1 * total_capacity_kw * cost_per_kw  #placeholder scalar value

class WindPlantConverter(ConverterBaseClass):
    """
    Wrapper class for WindPlant in the new_greenheart framework, inheriting from ConverterBaseClass.
    """
    def __init__(self, plant_config, tech_config, site_info=SiteInfo(flatirons_site)):
        """
        Initialize the WindPlantConverter.

        Args:
            tech_config (dict): Environmental parameters, e.g., wind speed, temperature.
            site_info (SiteInfo): Site information for the wind plant (location, elevation, etc.).
            config (WindConfig): Configuration for the WindPlant instance.
        """
        super().__init__(plant_config, tech_config)
        self.site = site_info
        wind_config = WindConfig(tech_config['details'])
        self.wind_plant = WindPlant(self.site, wind_config)

    def get_performance_model(self):
        """
        Describes how the wind plant performs its function.

        Returns:
            OpenMDAO System: The performance model as an OpenMDAO component.
        """
        return WindPlantComponent(wind_plant=self.wind_plant, plant_life=self.plant_config['plant']['plant_life'])

    def get_cost_model(self):
        """
        Describes the costs associated with the wind plant.

        This can be extended with a cost model.

        Returns:
            Optional[OpenMDAO System]: Placeholder for cost model in OpenMDAO.
        """
        return WindPlantCostComponent(cost_per_kw=1500.0)

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
        pass