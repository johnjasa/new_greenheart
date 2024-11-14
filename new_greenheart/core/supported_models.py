from new_greenheart.converters.wind.dummy_wind_turbine import DummyWindTurbine
from new_greenheart.converters.hydrogen.dummy_electrolyzer import DummyElectrolyzer
from new_greenheart.transporters.cable import Cable
from new_greenheart.transporters.pipe import Pipe
from new_greenheart.converters.wind.wind_plant import WindPlantConverter


supported_models = {
    'dummy_wind_turbine': DummyWindTurbine,
    'dummy_electrolyzer': DummyElectrolyzer,
    'wind_plant': WindPlantConverter,

    'cable': Cable,
    'pipe': Pipe,

}