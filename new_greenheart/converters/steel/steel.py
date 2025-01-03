from new_greenheart.core.baseclasses.converter_base_class import ConverterBaseClass
import openmdao.api as om
import numpy as np
from greenheart.simulation.technologies.steel.steel import run_steel_model, run_steel_cost_model, SteelCapacityModelConfig, SteelCostModelConfig, Feedstocks


class SteelPerformanceModel(om.ExplicitComponent):
    """
    An OpenMDAO component for modeling the performance of an steel plant.
    Computes annual steel production based on plant capacity and capacity factor.
    """
    def initialize(self):
        self.options.declare('plant_capacity', types=float)
        self.options.declare('capacity_factor', types=float)

    def setup(self):
        self.add_input('electricity', val=0.0, shape_by_conn=True, copy_shape='steel', units='kW')
        self.add_input('hydrogen', val=0.0, shape_by_conn=True, copy_shape='steel', units='kg/h')
        self.add_output('steel', val=0.0, shape_by_conn=True, copy_shape='electricity', units='t/year')

    def compute(self, inputs, outputs):
        plant_capacity = self.options['plant_capacity']
        capacity_factor = self.options['capacity_factor']
        steel_production_mtpy = run_steel_model(plant_capacity, capacity_factor)
        outputs['steel'] = steel_production_mtpy / len(inputs['electricity'])

class SteelCostModel(om.ExplicitComponent):
    """
    An OpenMDAO component for calculating the costs associated with steel production.
    Includes CapEx, OpEx, and byproduct credits.
    """
    def initialize(self):
        self.options.declare('config', types=SteelCostModelConfig)

    def setup(self):
        # Inputs for cost model configuration
        self.add_input('plant_capacity_mtpy', val=0.0, units='t/year', desc='Annual plant capacity')
        self.add_input('plant_capacity_factor', val=0.0, units=None, desc='Capacity factor')
        self.add_input('LCOH', val=0.0, units='USD/kg', desc='Levelized cost of hydrogen')
        self.add_output('CapEx', val=0.0, units='USD', desc='Total capital expenditures')
        self.add_output('OpEx', val=0.0, units='USD/year', desc='Total fixed operating costs')

    def compute(self, inputs, outputs):
        config = self.options['config']
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

        feedstocks = Feedstocks(**tech_config['details']['feedstocks'])

        self.cost_config = SteelCostModelConfig(
            operational_year=tech_config['details']['operational_year'],
            feedstocks=feedstocks,
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
