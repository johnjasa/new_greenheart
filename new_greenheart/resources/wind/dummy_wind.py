from new_greenheart.core.baseclasses.resource_base_class import ResourceBaseClass

class DummyWindResource(ResourceBaseClass):
    """
    Wind resource class.
    """
    def __init__(self):
        super().__init__()

    def get_performance_model(self):
        """
        Describes how the wind resource performs its function.
        
        This would be the equations that describe how the wind resource is used.

        Returns an OpenMDAO System.
        """
        pass

    def get_cost_model(self):
        """
        Describes the costs associated with the wind resource.

        Returns an OpenMDAO System.
        """
        pass

    def get_control_strategy(self):
        """
        Describes the control strategy for the wind resource.

        Returns an OpenMDAO System.
        """
        pass

    def get_financial_model(self):
        """
        Describes the financial model for the wind resource.

        Returns an OpenMDAO System.
        """
        pass