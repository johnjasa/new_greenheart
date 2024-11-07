# To be built out

class ConverterBaseClass(object):
    """
    Base class for all converter classes.
    """

    def __init__(self):
        pass

    def define_inputs(self):
        """
        Define the inputs for the converter.
        This would the resources that come into the converter.
        """
        pass

    def define_outputs(self):
        """
        Define the outputs for the converter.
        This would be the resources that leave the converter
        """
        pass

    def get_performance_model(self):
        """
        Describes how the converter performs its function.
        
        This would be the equations that describe how the converter transforms
        one resource into another.

        Returns an OpenMDAO System.
        """

    def get_cost_model(self):
        """
        Describes the costs associated with the converter.

        Returns an OpenMDAO System.
        """

    def get_control_strategy(self):
        """
        Describes the control strategy for the converter.

        Returns an OpenMDAO System.
        """

    def get_financial_model(self):
        """
        Describes the financial model for the converter.

        Returns an OpenMDAO System.
        """

    def post_process(self):
        """
        Post process the results of the converter.
        """
        pass