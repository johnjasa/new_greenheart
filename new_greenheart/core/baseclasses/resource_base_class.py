# To be built out

class ResourceBaseClass:
    """
    Base class for all resource classes.
    """

    def __init__(self):
        pass

    def define_outputs(self):
        """
        Define the outputs for the resource.
        """
        pass

    def get_performance_model(self):
        """
        Describes how the resource performs its function.
        
        This would be the equations that describe how the resource is used.

        Returns an OpenMDAO System.
        """

    def get_cost_model(self):
        """
        Describes the costs associated with the resource.

        Returns an OpenMDAO System.
        """

    def get_control_strategy(self):
        """
        Describes the control strategy for the resource.

        Returns an OpenMDAO System.
        """

    def get_financial_model(self):
        """
        Describes the financial model for the resource.

        Returns an OpenMDAO System.
        """