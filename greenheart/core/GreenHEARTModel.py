import numpy as np
import yaml
import openmdao.api as om


class GreenHEARTModel(object):

    def __init__(self, config_file):
        # read in config file; it's a yaml dict that looks like this:
        self.load_config(config_file)

        # validate inputs
        # Will we need schema for each wrapper individually? Presumably yes
        self.validate_inputs()

        # create plant-level model
        # this is an OpenMDAO group that contains all the technologies
        # it will need plant_config but not driver or tech config
        self.create_plant_model()

        # create technology models
        # these are OpenMDAO groups that contain all the components for each technology
        # they will need tech_config but not driver or plant config
        self.create_technology_models()

        # connect technologies
        # technologies are connected within the `technology_interconnections` section of the plant config
        self.connect_technologies()

        # create driver model
        # might be an analysis or optimization
        # can draw a fair amount from WEIS
        self.create_driver_model()

    def load_config(self, config_file):
        with open(config_file, 'r') as file:
            config = yaml.safe_load(file)

        self.name = config.get('name')
        self.system_summary = config.get('system_summary')

        # Load each config file as yaml and save as dict on this object
        with open(config.get('driver_config'), 'r') as file:
            self.driver_config = yaml.safe_load(file)

        with open(config.get('technology_config'), 'r') as file:
            self.technology_config = yaml.safe_load(file)

        with open(config.get('plant_config'), 'r') as file:
            self.plant_config = yaml.safe_load(file)

    def validate_inputs(self):
        # validate each config file
        self.validate_driver_config()
        self.validate_technology_config()
        self.validate_plant_config()
    
    def create_plant_model(self):
        """
        Create the plant-level model.

        This method creates an OpenMDAO group that contains all the technologies.
        It uses the plant configuration but not the driver or technology configuration.

        Information at this level might be used by any technology and info stored here is
        the same for each technology. This includes site information, project parameters,
        control strategy, and finance parameters.
        """

        # Create a site-level component
        site_config = self.plant_config.get('site', {})
        site_component = om.IndepVarComp()
        site_component.add_output('latitude', val=site_config.get('latitude', 0.0))
        site_component.add_output('longitude', val=site_config.get('longitude', 0.0))
        site_component.add_output('elevation_m', val=site_config.get('elevation_m', 0.0))
        site_component.add_output('time_zone', val=site_config.get('time_zone', 0))

        # Add boundaries if they exist
        boundaries = site_config.get('boundaries', [])
        for i, boundary in enumerate(boundaries):
            site_component.add_output(f'boundary_{i}_x', val=np.array(boundary.get('x', [])))
            site_component.add_output(f'boundary_{i}_y', val=np.array(boundary.get('y', [])))

        # Create a plant-level component
        project_parameters = self.plant_config.get('project_parameters', {})
        for key, value in project_parameters.items():
            plant_component.add_output(key, val=value)

        # Add control strategy parameters
        control_strategy = plant_config.get('control_strategy', {})
        for key, value in control_strategy.items():
            plant_component.add_output(key, val=value)

        # Add finance parameters
        finance_parameters = plant_config.get('finance_parameters', {})
        for key, value in finance_parameters.items():
            plant_component.add_output(key, val=value)

        plant_group = om.Group()
        plant_group.add_subsystem('plant_info', plant_component, promotes=['*'])

        # Create the plant model group and add components
        self.model = om.Group()
        self.model.add_subsystem('site', site_component, promotes=['*'])
        self.plant = self.model.add_subsystem('plant', plant_group, promotes=['*'])

    def create_technology_models(self):
        pass

    def connect_technologies(self):
        technology_interconnections = self.plant_config.get('technology_interconnections', [])

        # loop through each linkage and instantiate an OpenMDAO object (assume it exists) for
        # the connection type (e.g. cable, pipeline, etc)
        for connection in technology_interconnections:
            source_tech, dest_tech, transport_item, transport_type = connection

            # make the connection_name based on source, dest, item, type
            connection_name = f'{source_tech}_to_{dest_tech}_{transport_item}'

            # Add the connection component to the model
            self.plant.add_subsystem(connection_name, connection_component, promotes=['*'])

            # Connect the source technology to the connection component
            self.plant.connect(f'{source_tech}.{transport_item}_output', f'{connection_name}.{transport_item}_input')

            # Connect the connection component to the destination technology
            self.plant.connect(f'{connection_name}.{transport_item}_output', f'{dest_tech}.{transport_item}_input')

    def run(self):
        self.validate_inputs()
        # do model setup based on the driver config
        # might add a recorder, driver, set solver tolerances, etc

        # Add a recorder if specified in the driver config
        if 'recorder' in self.driver_config:
            recorder_config = self.driver_config['recorder']
            recorder = om.SqliteRecorder(recorder_config['file'])
            self.model.add_recorder(recorder)

        self.model.setup()

        self.model.run_model()


    def post_process(self):
        pass

