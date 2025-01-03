import numpy as np
import numpy_financial as npf

import openmdao.api as om

class AdjustedCapexComp(om.ExplicitComponent):
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
            self.add_output(f'capex_adjusted_{tech}', val=0.0, units='USD')

    def compute(self, inputs, outputs):
        for tech in self.options['tech_config']['technologies']:
            capex = inputs[f'capex_{tech}']
            cost_year = self.discount_years[tech]
            periods = self.cost_year - cost_year
            adjusted_capex = -npf.fv(self.inflation_rate, periods, 0.0, capex)
            outputs[f'capex_adjusted_{tech}'] = adjusted_capex