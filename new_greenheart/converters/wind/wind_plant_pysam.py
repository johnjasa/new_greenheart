import PySAM.Windpower as Windpower
from attrs import define, field

from hopp.simulation.technologies.resource import WindResource

from new_greenheart.converters.wind.wind_plant_baseclass import (
    WindPerformanceBaseClass,
    WindCostBaseClass
)
from new_greenheart.core.utilities import BaseConfig


@define
class PYSAMWindPlantPerformanceComponentConfig(BaseConfig):
    hub_height: float = field()


@define
class PYSAMWindPlantPerformanceComponentSiteConfig(BaseConfig):
    """Configuration class for the location of the wind plant PYSAMWindPlantPerformanceComponentSite.

    Args:
        latitude (float): Latitude of wind plant location.
        longitude (float): Longitude of wind plant location.
        year (float): Year for resource.
        wind_resource_filepath (str): Path to wind resource file. Defaults to "".
    """
    latitude: float = field()
    longitude: float = field()
    year: float = field()
    wind_resource_filepath: str = field(default="")


class PYSAMWindPlantPerformanceComponent(WindPerformanceBaseClass):
    """
    An OpenMDAO component that wraps a WindPlant model.
    It takes wind parameters as input and outputs power generation data.
    """
    def setup(self):
        super().setup()
        self.config = PYSAMWindPlantPerformanceComponentConfig.from_dict(
            self.options['tech_config']['details']
        )
        self.site_config = PYSAMWindPlantPerformanceComponentSiteConfig.from_dict(
            self.options['plant_config']['site']
        )
        self.config_name = "WindPowerSingleOwner"
        self.system_model = Windpower.default(self.config_name)

        lat = self.site_config.latitude
        lon = self.site_config.longitude
        year = self.site_config.year
        resource_filepath = self.site_config.wind_resource_filepath
        hub_height = self.config.hub_height
        wind_resource = WindResource(lat, lon, year, wind_turbine_hub_ht=hub_height, filepath=resource_filepath)
        self.system_model.value("wind_resource_data", wind_resource.data)

    def compute(self, inputs, outputs):
        self.system_model.execute(0)
        outputs['electricity'] = self.system_model.Outputs.gen

