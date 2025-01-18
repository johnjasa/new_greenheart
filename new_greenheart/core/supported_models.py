from new_greenheart.converters.wind.dummy_wind_turbine import DummyWindTurbine
from new_greenheart.converters.hydrogen.dummy_electrolyzer import DummyElectrolyzer
from new_greenheart.transporters.cable import Cable
from new_greenheart.transporters.pipe import Pipe
from new_greenheart.converters.wind.wind_plant import WindPlantConverter
from new_greenheart.converters.hydrogen.pem_electrolyzer import PEMElectrolyzer
from new_greenheart.converters.hydrogen.eco_tools_pem_electrolyzer import ElectrolyzerPerformanceModel, ElectrolyzerCostModel, ElectrolyzerFinanceModel
from new_greenheart.converters.hopp.hopp_wrapper import HOPPComponent
from new_greenheart.converters.ammonia.ammonia_converter import AmmoniaPlant
from new_greenheart.converters.steel.steel import SteelPerformanceModel, SteelCostModel
from new_greenheart.storage.hydrogen.tank import HydrogenTank


supported_models = {
    # Converters
    'dummy_wind_turbine': DummyWindTurbine,
    'dummy_electrolyzer': DummyElectrolyzer,
    'wind_plant': WindPlantConverter,
    'pem_electrolyzer': PEMElectrolyzer,
    'eco_pem_electrolyzer_performance': ElectrolyzerPerformanceModel,
    'eco_pem_electrolyzer_cost': ElectrolyzerCostModel,
    'eco_pem_electrolyzer_financial': ElectrolyzerFinanceModel,

    'hopp': HOPPComponent,
    'ammonia': AmmoniaPlant,
    'steel_performance': SteelPerformanceModel,
    'steel_cost': SteelCostModel,

    # Transport
    'cable': Cable,
    'pipe': Pipe,

    # Storage
    'hydrogen_tank': HydrogenTank,

}