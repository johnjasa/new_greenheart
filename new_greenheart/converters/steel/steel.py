import openmdao.api as om
import numpy as np
from greenheart.simulation.technologies.steel.steel import run_steel_model, run_steel_cost_model, run_steel_finance_model, SteelCapacityModelConfig, SteelCostModelConfig, SteelFinanceModelConfig, Feedstocks
from new_greenheart.converters.steel.steel_baseclass import SteelPerformanceBaseClass, SteelCostBaseClass, SteelFinanceBaseClass


class SteelPerformanceModel(SteelPerformanceBaseClass):
    """
    An OpenMDAO component for modeling the performance of an steel plant.
    Computes annual steel production based on plant capacity and capacity factor.
    """
    def initialize(self):
        super().initialize()

    def setup(self):
        super().setup()

    def compute(self, inputs, outputs):
        details = self.options['tech_config']['details']
        plant_capacity = details['plant_capacity_mtpy']
        capacity_factor = details['capacity_factor']
        steel_production_mtpy = run_steel_model(plant_capacity, capacity_factor)
        outputs['steel'] = steel_production_mtpy / len(inputs['electricity'])

class SteelCostAndFinancialModel(SteelCostBaseClass):
    """
    An OpenMDAO component for calculating the costs associated with steel production.
    Includes CapEx, OpEx, and byproduct credits.
    """
    def initialize(self):
        super().initialize()

    def setup(self):
        super().setup()
        tech_config = self.options['tech_config']
        self.cost_config = SteelCostModelConfig(
            operational_year=tech_config['details']['operational_year'],
            feedstocks=Feedstocks(**tech_config['details']['feedstocks']),
            plant_capacity_mtpy=tech_config['details']['plant_capacity_mtpy'],
            lcoh=tech_config['details']['lcoh'],
        )

        self.add_input('steel_production_mtpy', val=0.0, units='t/year')

        self.add_output('LCOS', val=0.0, units='USD/t')

    def compute(self, inputs, outputs):
        tech_config = self.options['tech_config']
        plant_config = self.options['plant_config']
        config = self.cost_config
        config.lcoh = inputs['LCOH']
        cost_model_outputs = run_steel_cost_model(config)
        
        outputs['CapEx'] = cost_model_outputs.total_plant_cost
        outputs['OpEx'] = cost_model_outputs.total_fixed_operating_cost

        finance_config = SteelFinanceModelConfig(
            plant_life=plant_config['plant']['plant_life'],
            plant_capacity_mtpy=tech_config['details']['plant_capacity_mtpy'],
            plant_capacity_factor=tech_config['details']['capacity_factor'],
            steel_production_mtpy=inputs['steel_production_mtpy'],
            lcoh=inputs['LCOH'],
            grid_prices=tech_config['finances']['grid_prices'],
            feedstocks=Feedstocks(**tech_config['details']['feedstocks']),
            costs=cost_model_outputs,
            o2_heat_integration=tech_config['details']['o2_heat_integration'],
            financial_assumptions=tech_config['finances']['financial_assumptions'],
            install_years=int(plant_config['plant']['installation_time'] / 12),
            gen_inflation=plant_config['finance_parameters']['profast_general_inflation'],
            save_plots=False,
            show_plots=False,
            output_dir="./output/",
            design_scenario_id=0,
        )

        finance_model_outputs = run_steel_finance_model(finance_config)
        outputs['LCOS'] = finance_model_outputs.sol.get("price")