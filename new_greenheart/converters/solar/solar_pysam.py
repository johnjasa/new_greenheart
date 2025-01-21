import PySAM.Pvwattsv8 as Pvwatts
from hopp.simulation.technologies.resource import SolarResource

from new_greenheart.converters.solar.solar_baseclass import SolarPerformanceBaseClass, SolarCostBaseClass


class PYSAMSolarPlantPerformanceComponent(SolarPerformanceBaseClass):
    """
    An OpenMDAO component that wraps a SolarPlant model.
    It takes wind parameters as input and outputs power generation data.
    """
    def setup(self):
        super().setup()
        self.config_name = "PVWattsSingleOwner"
        self.system_model = Pvwatts.default(self.config_name)

        lat = self.options['plant_config']['site']['latitude']
        lon = self.options['plant_config']['site']['longitude']
        year = self.options['plant_config']['site']['year']
        solar_resource = SolarResource(lat, lon, year)
        self.system_model.value("solar_resource_data", solar_resource.data)

    def compute(self, inputs, outputs):
        self.system_model.execute(0)
        outputs['electricity'] = self.system_model.Outputs.gen

