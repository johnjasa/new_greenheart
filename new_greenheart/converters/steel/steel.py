import numpy as np
import openmdao.api as om
from attrs import define, field

from greenheart.simulation.technologies.steel.steel import (
    run_steel_model,
    run_steel_cost_model,
    run_steel_finance_model,
    SteelCapacityModelConfig,
    SteelCostModelConfig,
    SteelFinanceModelConfig,
    Feedstocks
)

from new_greenheart.converters.steel.steel_baseclass import (
    SteelPerformanceBaseClass,
    SteelCostBaseClass,
    SteelFinanceBaseClass
)
from new_greenheart.core.utilities import BaseConfig
from new_greenheart.core.validators import gt_zero, contains, range_val


@define
class SteelPerformanceModelConfig(BaseConfig):
    plant_capacity_mtpy: float = field()
    capacity_factor: float = field()


class SteelPerformanceModel(SteelPerformanceBaseClass):
    """
    An OpenMDAO component for modeling the performance of an steel plant.
    Computes annual steel production based on plant capacity and capacity factor.
    """
    def initialize(self):
        super().initialize()

    def setup(self):
        super().setup()
        self.config = SteelPerformanceModelConfig.from_dict(self.options['tech_config']['details'])

    def compute(self, inputs, outputs):
        steel_production_mtpy = run_steel_model(
            self.config.plant_capacity_mtpy,
            self.config.capacity_factor,
        )
        outputs['steel'] = steel_production_mtpy / len(inputs['electricity'])


@define
class SteelCostAndFinancialModelConfig(BaseConfig):
    operational_year: int = field()
    plant_capacity_mtpy: float = field()
    capacity_factor: float = field()
    o2_heat_integration: bool = field()
    lcoh: float = field()
    feedstocks: dict = field() #TODO: build validator for this large dictionary
    finances: dict = field() #TODO: build validator for this large dictionary


@define
class SteelCostAndFinancialPlantConfig(BaseConfig):
    plant_life: int = field()
    installation_time: int = field()
    gen_inflation: float = field()


class SteelCostAndFinancialModel(SteelCostBaseClass):
    """
    An OpenMDAO component for calculating the costs associated with steel production.
    Includes CapEx, OpEx, and byproduct credits.
    """
    def initialize(self):
        super().initialize()

    def setup(self):
        super().setup()
        self.config = SteelCostAndFinancialModelConfig.from_dict(
            self.options['tech_config']['details']
        )
        # TODO Bring the steel cost model config and feedstock classes into new greenheart
        self.cost_config = SteelCostModelConfig(
            operational_year=self.config.operational_year,
            feedstocks=Feedstocks(**self.config.feedstocks),
            plant_capacity_mtpy=self.config.plant_capacity_mtpy,
            lcoh=self.config.lcoh,
        )
        # TODO Review whether to split plant and finance_parameters configs or combine somehow
        self.plant_config = SteelCostAndFinancialPlantConfig(
            plant_life=self.options["plant_config"]["plant"]["plant_life"],
            installation_time=self.options["plant_config"]["plant"]["installation_time"],
            gen_inflation=self.options["plant_config"]["finance_parameters"]["profast_general_inflation"]
        )

        self.add_input('steel_production_mtpy', val=0.0, units='t/year')

        self.add_output('LCOS', val=0.0, units='USD/t')

    def compute(self, inputs, outputs):
        config = self.cost_config
        config.lcoh = inputs['LCOH']
        cost_model_outputs = run_steel_cost_model(config)
        
        outputs['CapEx'] = cost_model_outputs.total_plant_cost
        outputs['OpEx'] = cost_model_outputs.total_fixed_operating_cost

        # TODO Bring this config dict into new_greenheart from old greenheart
        finance_config = SteelFinanceModelConfig(
            plant_life=self.plant_config.plant_life,
            plant_capacity_mtpy=self.config.plant_capacity_mtpy,
            plant_capacity_factor=self.config.capacity_factor,
            steel_production_mtpy=inputs['steel_production_mtpy'],
            lcoh=config.lcoh,
            grid_prices=self.config.finances['grid_prices'],
            feedstocks=Feedstocks(**self.config.feedstocks),
            costs=cost_model_outputs,
            o2_heat_integration=self.config.o2_heat_integration,
            financial_assumptions=self.config.finances['financial_assumptions'],
            install_years=int(self.plant_config.installation_time / 12),
            gen_inflation=self.plant_config.gen_inflation,
            save_plots=False,
            show_plots=False,
            output_dir="./output/",
            design_scenario_id=0,
        )

        finance_model_outputs = run_steel_finance_model(finance_config)
        outputs['LCOS'] = finance_model_outputs.sol.get("price")