import numpy as np
import numpy_financial as npf

import openmdao.api as om

class AdjustedCapexOpexComp(om.ExplicitComponent):
    def initialize(self):
        self.options.declare('tech_config', types=dict)
        self.options.declare('plant_config', types=dict)

    def setup(self):
        tech_config = self.options['tech_config']
        plant_config = self.options['plant_config']
        self.discount_years = plant_config['finance_parameters']['discount_years']
        self.inflation_rate = plant_config['finance_parameters']['costing_general_inflation']
        self.cost_year = plant_config['plant']['cost_year']

        for tech in tech_config['technologies']:
            self.add_input(f'capex_{tech}', val=0.0, units='USD')
            self.add_input(f'opex_{tech}', val=0.0, units='USD/year')
            self.add_output(f'capex_adjusted_{tech}', val=0.0, units='USD')
            self.add_output(f'opex_adjusted_{tech}', val=0.0, units='USD/year')
        
        self.add_output('total_capex_adjusted', val=0.0, units='USD')
        self.add_output('total_opex_adjusted', val=0.0, units='USD/year')

    def compute(self, inputs, outputs):
        total_capex_adjusted = 0.0
        total_opex_adjusted = 0.0
        for tech in self.options['tech_config']['technologies']:
            capex = inputs[f'capex_{tech}']
            opex = inputs[f'opex_{tech}']
            cost_year = self.discount_years[tech]
            periods = self.cost_year - cost_year
            adjusted_capex = -npf.fv(self.inflation_rate, periods, 0.0, capex)
            adjusted_opex = -npf.fv(self.inflation_rate, periods, 0.0, opex)
            outputs[f'capex_adjusted_{tech}'] = adjusted_capex
            outputs[f'opex_adjusted_{tech}'] = adjusted_opex
            total_capex_adjusted += adjusted_capex
            total_opex_adjusted += adjusted_opex
        
        outputs['total_capex_adjusted'] = total_capex_adjusted
        outputs['total_opex_adjusted'] = total_opex_adjusted