class StorageBaseClass(object):
    """
    Base class for all storage classes.
    """

    def __init__(self, plant_config={}, tech_config={}):
        self.tech_config = tech_config
        self.plant_config = plant_config

    def get_performance_model(self):
        """
        Describes how the storage performs its function.
        
        Returns an OpenMDAO System.
        """
        return None

    def get_cost_model(self):
        """
        Describes the costs associated with the storage.

        Returns an OpenMDAO System.
        """
        return None

    def get_control_strategy(self):
        """
        Describes the control strategy for the storage.

        Returns an OpenMDAO System.
        """
        pass

    def get_financial_model(self):
        """
        Describes the financial model for the storage.

        Returns an OpenMDAO System.
        """
        return None

    def post_process(self):
        """
        Post process the results of the storage.
        """
        pass