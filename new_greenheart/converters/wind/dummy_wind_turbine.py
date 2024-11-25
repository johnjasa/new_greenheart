from new_greenheart.core.baseclasses.converter_base_class import ConverterBaseClass

import openmdao.api as om


class WindTurbineComponent(om.ExplicitComponent):
    """
    A simple OpenMDAO component that represents a wind turbine.
    It takes in wind speed and outputs power.
    """
    def initialize(self):
        self.options.declare('wind_speed', types=float)

    def setup(self):
        # Outputs
        self.add_output('electricity', val=0.0, units='kW', desc='Power output')

    def compute(self, inputs, outputs):
        wind_speed = self.options['wind_speed']
        
        # Simple power curve: P = 0.5 * Cp * rho * A * V^3
        Cp = 0.4  # Power coefficient
        rho = 1.225  # Air density in kg/m^3
        A = 10.0  # Swept area in m^2
        outputs['electricity'] = 0.5 * Cp * rho * A * wind_speed ** 3


class WindTurbineCosts(om.ExplicitComponent):
    """
    A simple OpenMDAO component that represents the costs of a wind turbine.
    """
    def setup(self):
        # Outputs
        self.add_output('capital_cost', val=0.0, units='USD', desc='Capital cost of the wind turbine')

    def compute(self, inputs, outputs):
        outputs['capital_cost'] = 1000000.0


class DummyWindTurbine(ConverterBaseClass):
    """
    Dummy wind turbine class.
    """
    def __init__(self, plant_config, tech_config):
        super().__init__(plant_config, tech_config)

    def get_performance_model(self):
        """
        Describes how the wind turbine performs its function.
        
        Returns an OpenMDAO System.
        """
        return WindTurbineComponent(wind_speed=self.tech_config['resource']['wind_speed'])

    def get_cost_model(self):
        """
        Describes the costs associated with the wind turbine.

        Returns an OpenMDAO System.
        """
        pass

    def get_control_strategy(self):
        """
        Describes the control strategy for the wind turbine.
        """
        pass

    def get_financial_model(self):
        """
        Describes the financial model for the wind turbine.

        Returns an OpenMDAO System.
        """
        pass

    def post_process(self):
        """
        Post process the results of the wind turbine.
        """
        print("Wind turbine did great!")