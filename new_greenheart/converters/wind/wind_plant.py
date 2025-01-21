from new_greenheart.core.baseclasses.converter_base_class import ConverterBaseClass
from hopp.simulation.technologies.wind.floris import Floris
from hopp.simulation.technologies.wind.wind_plant import WindPlant
from hopp.simulation.technologies.sites import SiteInfo, flatirons_site

from new_greenheart.converters.wind.wind_plant_baseclass import WindPerformanceBaseClass, WindCostBaseClass

n_timesteps = 8760

class WindConfig:
    def __init__(self, config_details):
        # Dynamically set attributes based on the YAML keys
        for key, value in config_details.items():
            setattr(self, key, value)


class WindPlantPerformanceComponent(WindPerformanceBaseClass):
    """
    An OpenMDAO component that wraps a WindPlant model.
    It takes wind parameters as input and outputs power generation data.
    """
    def setup(self):
        super().setup()
        self.site = SiteInfo(flatirons_site)
        wind_config = WindConfig(self.options['tech_config']['details'])
        self.wind_plant = WindPlant(self.site, wind_config)

    def compute(self, inputs, outputs):
        # Assumes the WindPlant instance has a method to simulate and return power output
        plant_life = self.options['plant_config']['plant']['plant_life']
        self.wind_plant.simulate_power(plant_life)
        outputs['electricity'] = self.wind_plant._system_model.value("gen")


class WindPlantCostComponent(WindCostBaseClass):
    """
    An OpenMDAO component that calculates the capital expenditure (CapEx) for a wind plant.

    Just a placeholder for now, but can be extended with more detailed cost models.
    """
    def initialize(self):
        super().initialize()
        self.options.declare('cost_per_kw', types=float, default=1500.0, desc='Cost per kW of installed capacity')

    def setup(self):
        super().setup()
        # Inputs: Number of turbines and turbine rating in kW
        self.add_input('num_turbines', val=0, desc='Number of wind turbines')
        self.add_input('turbine_rating_kw', val=0.0, units='kW', desc='Rating of each turbine in kW')

    def compute(self, inputs, outputs):
        num_turbines = inputs['num_turbines']
        turbine_rating_kw = inputs['turbine_rating_kw']
        cost_per_kw = self.options['cost_per_kw']

        # Calculate CapEx
        total_capacity_kw = num_turbines * turbine_rating_kw
        outputs['CapEx'] = total_capacity_kw * cost_per_kw
        outputs['OpEx'] = 0.1 * total_capacity_kw * cost_per_kw  #placeholder scalar value

