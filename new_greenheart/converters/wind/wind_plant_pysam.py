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
    lat: float = field()
    lon: float = field()
    year: float = field()


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

        lat = self.plant_config.latitude
        lon = self.plant_config.longitude
        year = self.plant_config.year
        hub_height = self.config.hub_height
        wind_resource = WindResource(lat, lon, year, wind_turbine_hub_ht=hub_height)
        self.system_model.value("wind_resource_data", wind_resource.data)

    def compute(self, inputs, outputs):
        self.system_model.execute(0)
        outputs['electricity'] = self.system_model.Outputs.gen

