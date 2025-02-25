import PySAM.Pvwattsv8 as Pvwatts
from attrs import define, field

from hopp.simulation.technologies.resource import SolarResource

from new_greenheart.converters.solar.solar_baseclass import (
    SolarPerformanceBaseClass,
    SolarCostBaseClass
)
from new_greenheart.core.utilities import BaseConfig


@define
class PYSAMSolarPlantPerformanceComponentConfig(BaseConfig):
    lat: float = field()
    lon: float = field()
    year: float = field()


class PYSAMSolarPlantPerformanceComponent(SolarPerformanceBaseClass):
    """
    An OpenMDAO component that wraps a SolarPlant model.
    It takes wind parameters as input and outputs power generation data.
    """
    def setup(self):
        super().setup()
        self.config = PYSAMSolarPlantPerformanceComponentConfig(
            self.options["plant_config"]["site"]
        )
        self.config_name = "PVWattsSingleOwner"
        self.system_model = Pvwatts.default(self.config_name)

        solar_resource = SolarResource(self.config.lat, self.config.lon, self.config.year)
        self.system_model.value("solar_resource_data", solar_resource.data)

    def compute(self, inputs, outputs):
        self.system_model.execute(0)
        outputs['electricity'] = self.system_model.Outputs.gen

