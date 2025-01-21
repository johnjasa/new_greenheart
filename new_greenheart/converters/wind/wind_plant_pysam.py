import PySAM.Windpower as Windpower
from hopp.simulation.technologies.resource import WindResource

from new_greenheart.converters.wind.wind_plant_baseclass import WindPerformanceBaseClass, WindCostBaseClass


class PYSAMWindPlantPerformanceComponent(WindPerformanceBaseClass):
    """
    An OpenMDAO component that wraps a WindPlant model.
    It takes wind parameters as input and outputs power generation data.
    """
    def setup(self):
        super().setup()
        self.config_name = "WindPowerSingleOwner"
        self.system_model = Windpower.default(self.config_name)

        lat = self.options['plant_config']['site']['latitude']
        lon = self.options['plant_config']['site']['longitude']
        year = self.options['plant_config']['site']['year']
        hub_height = self.options['tech_config']['details']['hub_height']
        wind_resource = WindResource(lat, lon, year, wind_turbine_hub_ht=hub_height)
        self.system_model.value("wind_resource_data", wind_resource.data)

    def compute(self, inputs, outputs):
        self.system_model.execute(0)
        outputs['electricity'] = self.system_model.Outputs.gen

