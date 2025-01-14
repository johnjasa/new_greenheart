from new_greenheart.converters.wind.dummy_wind_turbine import DummyWindTurbine
from new_greenheart.converters.hydrogen.dummy_electrolyzer import DummyElectrolyzer
from new_greenheart.transporters.cable import Cable
from new_greenheart.transporters.pipe import Pipe
from new_greenheart.converters.wind.wind_plant import WindPlantConverter
from new_greenheart.converters.hydrogen.pem_electrolyzer import PEMElectrolyzer
from new_greenheart.converters.hydrogen.eco_tools_pem_electrolyzer import ECOPEMElectrolyzer
from new_greenheart.converters.hopp.hopp_wrapper import HOPPModel
from new_greenheart.converters.ammonia.ammonia_converter import AmmoniaPlant
from new_greenheart.converters.steel.steel import SteelPlant
from new_greenheart.storage.hydrogen.tank import HydrogenTank


supported_models = {
    # Converters
    'dummy_wind_turbine': DummyWindTurbine,
    'dummy_electrolyzer': DummyElectrolyzer,
    'wind_plant': WindPlantConverter,
    'pem_electrolyzer': PEMElectrolyzer,
    'eco_pem_electrolyzer': ECOPEMElectrolyzer,
    'hopp': HOPPModel,
    'ammonia': AmmoniaPlant,
    'steel': SteelPlant,

    # Transport
    'cable': Cable,
    'pipe': Pipe,

    # Storage
    'hydrogen_tank': HydrogenTank,

}