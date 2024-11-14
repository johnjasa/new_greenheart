from new_greenheart.converters.wind.dummy_wind_turbine import DummyWindTurbine
from new_greenheart.converters.hydrogen.dummy_electrolyzer import DummyElectrolyzer
from new_greenheart.transporters.cable import Cable
from new_greenheart.transporters.pipe import Pipe
from new_greenheart.converters.wind.wind_plant import WindPlantConverter
from new_greenheart.converters.hydrogen.pem_electrolyzer import PEMElectrolyzer


supported_models = {
    'dummy_wind_turbine': DummyWindTurbine,
    'dummy_electrolyzer': DummyElectrolyzer,
    'wind_plant': WindPlantConverter,
    'pem_electrolyzer': PEMElectrolyzer,

    'cable': Cable,
    'pipe': Pipe,

}