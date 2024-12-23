from new_greenheart.core.baseclasses.converter_base_class import ConverterBaseClass
import openmdao.api as om
import numpy as np
from greenheart.simulation.technologies.ammonia.ammonia import run_ammonia_model, run_ammonia_cost_model, AmmoniaCapacityModelConfig, AmmoniaCostModelConfig, Feedstocks


class AmmoniaPerformanceModel(om.ExplicitComponent):
    """
    An OpenMDAO component for modeling the performance of an ammonia plant.
    Computes annual ammonia production based on plant capacity and capacity factor.
    """
    def initialize(self):
        self.options.declare('plant_capacity', types=float)
        self.options.declare('capacity_factor', types=float)

    def setup(self):
        self.add_input('electricity', val=0.0, shape_by_conn=True, copy_shape='hydrogen', units='kW')
        self.add_input('hydrogen', val=0.0, shape_by_conn=True, copy_shape='hydrogen', units='kg/h')
        self.add_output('ammonia', val=0.0, shape_by_conn=True, copy_shape='electricity', units='kg/h')

    def compute(self, inputs, outputs):
        plant_capacity = self.options['plant_capacity']
        capacity_factor = self.options['capacity_factor']
        ammonia_production_kgpy = run_ammonia_model(plant_capacity, capacity_factor)
        outputs['ammonia'] = ammonia_production_kgpy / len(inputs['electricity'])

class AmmoniaCostModel(om.ExplicitComponent):
    """
    An OpenMDAO component for calculating the costs associated with ammonia production.
    Includes CapEx, OpEx, and byproduct credits.
    """
    def initialize(self):
        self.options.declare('config', types=AmmoniaCostModelConfig)

    def setup(self):
        # Inputs for cost model configuration
        self.add_input('plant_capacity_kgpy', val=0.0, units='kg/year', desc='Annual plant capacity')
        self.add_input('plant_capacity_factor', val=0.0, units=None, desc='Capacity factor')
        self.add_output('capex_total', val=0.0, units='USD', desc='Total capital expenditures')
        self.add_output('total_fixed_operating_cost', val=0.0, units='USD', desc='Total fixed operating costs')
        self.add_output('variable_cost_in_startup_year', val=0.0, units='USD', desc='Variable costs')
        self.add_output('credits_byproduct', val=0.0, units='USD', desc='Byproduct credits')

    def compute(self, inputs, outputs):
        config = self.options['config']
        cost_model_outputs = run_ammonia_cost_model(config)
        
        outputs['capex_total'] = cost_model_outputs.capex_total
        outputs['total_fixed_operating_cost'] = cost_model_outputs.total_fixed_operating_cost
        outputs['variable_cost_in_startup_year'] = cost_model_outputs.variable_cost_in_startup_year
        outputs['credits_byproduct'] = cost_model_outputs.credits_byproduct

class AmmoniaPlant(ConverterBaseClass):
    """
    Wrapper class for the ammonia plant in the new_greenheart framework.
    Inherits from ConverterBaseClass and integrates performance and cost models.
    """
    def __init__(self, plant_config, tech_config):
        super().__init__(plant_config, tech_config)

        feedstocks = Feedstocks(**tech_config['details']['feedstocks'])

        self.cost_config = AmmoniaCostModelConfig(
            plant_capacity_factor=tech_config['details']['capacity_factor'],
            feedstocks=feedstocks,
            plant_capacity_kgpy=tech_config['details']['plant_capacity_kgpy'],
        )

    def get_performance_model(self):
        """
        Returns the performance model for ammonia production.
        """
        return AmmoniaPerformanceModel(plant_capacity=self.tech_config['details']['plant_capacity_kgpy'], capacity_factor=self.tech_config['details']['capacity_factor'])

    def get_cost_model(self):
        """
        Returns the cost model for the ammonia plant.
        """
        return AmmoniaCostModel(config=self.cost_config)

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
        Post-process the results from the ammonia plant simulation.
        """
        pass
