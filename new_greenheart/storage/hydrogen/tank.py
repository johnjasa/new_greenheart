from new_greenheart.core.baseclasses.storage_base_class import StorageBaseClass
import numpy as np
import openmdao.api as om


class HydrogenTankPerformanceModel(om.ExplicitComponent):
    def initialize(self):
        self.options.declare('config_details', types=dict)

    def setup(self):
        self.add_input('hydrogen', val=0., shape_by_conn=True, copy_shape='hydrogen_out', units='kg/h', desc='Hydrogen input over a year')
        self.add_input('initial_hydrogen', val=0., units='kg', desc='Initial amount of hydrogen in the tank')
        self.add_input('total_capacity', val=float(self.options['config_details']['total_capacity']), units='kg', desc='Total storage capacity')
        self.add_input('hydrogen_out', val=0., shape_by_conn=True, copy_shape='hydrogen', units='kg/h', desc='Hydrogen output over a year')
        self.add_output('stored_hydrogen', val=0.0, shape_by_conn=True, copy_shape='hydrogen', units='kg', desc='Amount of hydrogen stored')

    def compute(self, inputs, outputs):
        initial_hydrogen = inputs['initial_hydrogen']
        hydrogen_in = inputs['hydrogen']
        hydrogen_out = inputs['hydrogen_out']

        outputs['stored_hydrogen'] = initial_hydrogen + hydrogen_in - hydrogen_out

class HydrogenTankCostModel(om.ExplicitComponent):
    def initialize(self):
        self.options.declare('config_details', types=dict)

    def setup(self):
        self.add_input('total_capacity', val=float(self.options['config_details']['total_capacity']), units='kg', desc='Total storage capacity')
        self.add_output('CapEx', val=0.0, units='MUSD', desc='Capital expenditure')
        self.add_output('OpEx', val=0.0, units='MUSD', desc='Operational expenditure')

    def compute(self, inputs, outputs):
        outputs['CapEx'] = inputs['total_capacity'] * 0.1
        outputs['OpEx'] = inputs['total_capacity'] * 0.01


class HydrogenTank(StorageBaseClass):
    """
    Wrapper class for the hydrogen tank in the new_greenheart framework, inheriting from StorageBaseClass.
    """
    def __init__(self, plant_config, tech_config):
        """
        Initialize the HydrogenTank.
        """
        super().__init__(plant_config, tech_config)

    def get_performance_model(self):
        """
        Describes how the hydrogen tank performs its function.

        Returns an OpenMDAO System.
        """
        return HydrogenTankPerformanceModel(config_details=self.tech_config['details'])

    def get_cost_model(self):
        """
        Describes the costs associated with the hydrogen tank.
        """
        return HydrogenTankCostModel(config_details=self.tech_config['details'])