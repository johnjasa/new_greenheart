from new_greenheart.core.baseclasses.converter_base_class import ConverterBaseClass

import openmdao.api as om


class WindTurbineComponent(om.ExplicitComponent):
    """
    A simple OpenMDAO component that represents a wind turbine.
    It takes in wind speed and outputs power.
    """
    def initialize(self):
        self.options.declare('energy_resources', types=dict)

    def setup(self):
        # Outputs
        self.add_output('electricity', val=0.0, units='kW', desc='Power output')

    def compute(self, inputs, outputs):
        wind_speed = self.options['energy_resources']['wind_speed']
        
        # Simple power curve: P = 0.5 * Cp * rho * A * V^3
        Cp = 0.4  # Power coefficient
        rho = 1.225  # Air density in kg/m^3
        A = 10.0  # Swept area in m^2
        outputs['electricity'] = 0.5 * Cp * rho * A * wind_speed ** 3


class DummyWindTurbine(ConverterBaseClass):
    """
    Dummy wind turbine class.
    """
    def __init__(self, energy_resources):
        super().__init__(energy_resources)

    def get_performance_model(self):
        """
        Describes how the wind turbine performs its function.
        
        This would be the equations that describe how the wind turbine is used.

        Returns an OpenMDAO System.
        """
        return WindTurbineComponent(energy_resources=self.energy_resources)

    def get_cost_model(self):
        """
        Describes the costs associated with the wind turbine.

        Returns an OpenMDAO System.
        """
        pass

    def get_control_strategy(self):
        """
        Describes the control strategy for the wind turbine.

        Returns an OpenMDAO System.
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