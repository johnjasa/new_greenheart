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
        self.options.declare('plant_config', types=dict)
        self.options.declare('tech_config', types=dict)

    def setup(self):
        self.add_input('electricity', val=0.0, shape_by_conn=True, copy_shape='hydrogen', units='kW')
        self.add_input('hydrogen', val=0.0, shape_by_conn=True, copy_shape='hydrogen', units='kg/h')
        self.add_output('ammonia', val=0.0, shape_by_conn=True, copy_shape='electricity', units='kg/h')

    def compute(self, inputs, outputs):
        plant_capacity=self.options['tech_config']['details']['plant_capacity_kgpy']
        capacity_factor=self.options['tech_config']['details']['capacity_factor']
        ammonia_production_kgpy = run_ammonia_model(plant_capacity, capacity_factor)
        outputs['ammonia'] = ammonia_production_kgpy / len(inputs['electricity'])

class AmmoniaCostModel(om.ExplicitComponent):
    """
    An OpenMDAO component for calculating the costs associated with ammonia production.
    Includes CapEx, OpEx, and byproduct credits.
    """
    def initialize(self):
        self.options.declare('plant_config', types=dict)
        self.options.declare('tech_config', types=dict)

    def setup(self):
        # Inputs for cost model configuration
        self.add_input('plant_capacity_kgpy', val=0.0, units='kg/year', desc='Annual plant capacity')
        self.add_input('plant_capacity_factor', val=0.0, units=None, desc='Capacity factor')
        self.add_output('CapEx', val=0.0, units='USD', desc='Total capital expenditures')
        self.add_output('OpEx', val=0.0, units='USD/year', desc='Total fixed operating costs')
        self.add_output('variable_cost_in_startup_year', val=0.0, units='USD', desc='Variable costs')
        self.add_output('credits_byproduct', val=0.0, units='USD', desc='Byproduct credits')

        tech_config = self.options['tech_config']

        self.cost_config = AmmoniaCostModelConfig(
            plant_capacity_factor=tech_config['details']['capacity_factor'],
            feedstocks=Feedstocks(**tech_config['details']['feedstocks']),
            plant_capacity_kgpy=tech_config['details']['plant_capacity_kgpy'],
        )

    def compute(self, inputs, outputs):
        cost_model_outputs = run_ammonia_cost_model(self.cost_config)
        
        outputs['CapEx'] = cost_model_outputs.capex_total
        outputs['OpEx'] = cost_model_outputs.total_fixed_operating_cost
        outputs['variable_cost_in_startup_year'] = cost_model_outputs.variable_cost_in_startup_year
        outputs['credits_byproduct'] = cost_model_outputs.credits_byproduct