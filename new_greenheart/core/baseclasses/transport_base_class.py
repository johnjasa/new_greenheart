class TransportBaseClass(object):
    """
    Base class for all transport classes.
    """

    def __init__(self, plant_config={}, tech_config={}):
        self.tech_config = tech_config
        self.plant_config = plant_config

    def get_performance_model(self):
        """
        Describes how the transport performs its function.
        
        Returns an OpenMDAO System.
        """
        pass

    def get_cost_model(self):
        """
        Describes the costs associated with the transport.

        Returns an OpenMDAO System.
        """
        pass

    def get_financial_model(self):
        """
        Describes the financial model for the transport.

        Returns an OpenMDAO System.
        """
        pass

    def post_process(self):
        """
        Post process the results of the transport.
        """
        pass