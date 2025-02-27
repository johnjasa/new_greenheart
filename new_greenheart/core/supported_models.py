from new_greenheart.converters.wind.dummy_wind_turbine import DummyPlantPerformance, DummyPlantCost
from new_greenheart.converters.hydrogen.dummy_electrolyzer import DummyElectrolyzerPerformanceModel, DummyElectrolyzerCostModel
from new_greenheart.transporters.cable import Cable
from new_greenheart.transporters.pipe import Pipe
from new_greenheart.converters.wind.wind_plant import WindPlantPerformanceComponent, WindPlantCostComponent
from new_greenheart.converters.hydrogen.pem_electrolyzer import ElectrolyzerPerformanceModel, ElectrolyzerCostModel, ElectrolyzerFinanceModel
from new_greenheart.converters.hydrogen.eco_tools_pem_electrolyzer import ECOElectrolyzerPerformanceModel, ECOElectrolyzerCostModel
from new_greenheart.converters.hopp.hopp_wrapper import HOPPComponent
from new_greenheart.converters.desalination.desalination import ReverseOsmosisPerformanceModel, ReverseOsmosisCostModel
from new_greenheart.converters.ammonia.ammonia_baseclass import AmmoniaPerformanceModel, AmmoniaCostModel
from new_greenheart.converters.steel.steel import SteelPerformanceModel, SteelCostAndFinancialModel
from new_greenheart.storage.hydrogen.tank_baseclass import HydrogenTankPerformanceModel, HydrogenTankCostModel
from new_greenheart.storage.hydrogen.eco_storage import H2Storage
from new_greenheart.converters.wind.wind_plant_pysam import PYSAMWindPlantPerformanceComponent
from new_greenheart.converters.solar.solar_pysam import PYSAMSolarPlantPerformanceComponent


supported_models = {
    # Converters
    'dummy_wind_turbine_performance': DummyPlantPerformance,
    'dummy_wind_turbine_cost': DummyPlantCost,    

    'dummy_electrolyzer_performance': DummyElectrolyzerPerformanceModel,
    'dummy_electrolyzer_cost': DummyElectrolyzerCostModel,

    'wind_plant_performance': WindPlantPerformanceComponent,
    'wind_plant_cost': WindPlantCostComponent,

    'pysam_wind_plant_performance' : PYSAMWindPlantPerformanceComponent,

    'pysam_solar_plant_performance' : PYSAMSolarPlantPerformanceComponent,

    'pem_electrolyzer_performance': ElectrolyzerPerformanceModel,
    'pem_electrolyzer_cost': ElectrolyzerCostModel,
    'pem_electrolyzer_financial': ElectrolyzerFinanceModel,

    'eco_pem_electrolyzer_performance': ECOElectrolyzerPerformanceModel,
    'eco_pem_electrolyzer_cost': ECOElectrolyzerCostModel,

    'h2_storage': H2Storage,

    'hopp': HOPPComponent,

    'reverse_osmosis_desalination_performance': ReverseOsmosisPerformanceModel,
    'reverse_osmosis_desalination_cost': ReverseOsmosisCostModel,

    'ammonia_performance': AmmoniaPerformanceModel,
    'ammonia_cost': AmmoniaCostModel,

    'steel_performance': SteelPerformanceModel,
    'steel_cost': SteelCostAndFinancialModel,

    # Transport
    'cable': Cable,
    'pipe': Pipe,

    # Storage
    'hydrogen_tank_performance': HydrogenTankPerformanceModel,
    'hydrogen_tank_cost': HydrogenTankCostModel,

}