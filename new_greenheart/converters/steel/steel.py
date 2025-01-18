from new_greenheart.core.baseclasses.converter_base_class import ConverterBaseClass
import openmdao.api as om
import numpy as np
from greenheart.simulation.technologies.steel.steel import run_steel_model, run_steel_cost_model, SteelCapacityModelConfig, SteelCostModelConfig, Feedstocks
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

class SteelCostModel(SteelCostBaseClass):
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

    def compute(self, inputs, outputs):
        config = self.cost_config
        config.lcoh = inputs['LCOH']
        cost_model_outputs = run_steel_cost_model(config)
        
        outputs['CapEx'] = cost_model_outputs.total_plant_cost
        outputs['OpEx'] = cost_model_outputs.total_fixed_operating_cost

class SteelPlant(ConverterBaseClass):
    """
    Wrapper class for the steel plant in the new_greenheart framework.
    Inherits from ConverterBaseClass and integrates performance and cost models.
    """
    def __init__(self, plant_config, tech_config):
        super().__init__(plant_config, tech_config)

        self.cost_config = SteelCostModelConfig(
            operational_year=tech_config['details']['operational_year'],
            feedstocks=Feedstocks(**tech_config['details']['feedstocks']),
            plant_capacity_mtpy=tech_config['details']['plant_capacity_mtpy'],
            lcoh=tech_config['details']['lcoh'],
        )

    def get_performance_model(self):
        """
        Returns the performance model for steel production.
        """
        return SteelPerformanceModel(plant_capacity=self.tech_config['details']['plant_capacity_mtpy'], capacity_factor=self.tech_config['details']['capacity_factor'])

    def get_cost_model(self):
        """
        Returns the cost model for the steel plant.
        """
        return SteelCostModel(config=self.cost_config)

    def get_control_strategy(self):
        """
        Placeholder for control strategy.
        """
        pass

    def get_financial_model(self):
        """
        Placeholder for financial model.
        """
        pass

    def post_process(self):
        """
        Post-process the results from the steel plant simulation.
        """
        pass
