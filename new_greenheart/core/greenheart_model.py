import numpy as np
import yaml
import openmdao.api as om

from new_greenheart.core.supported_models import supported_models
from new_greenheart.resources.wind.dummy_wind import DummyWindResource
from new_greenheart.converters.wind.dummy_wind_turbine import DummyWindTurbine
from new_greenheart.core.pose_optimization import PoseOptimization
from new_greenheart.core.inputs.validation import load_yaml, load_plant_yaml, load_tech_yaml, load_driver_yaml


class GreenHEARTModel(object):

    def __init__(self, config_file):
        # read in config file; it's a yaml dict that looks like this:
        self.load_config(config_file)

        # create site-level model
        # this is an OpenMDAO group that contains all the site information
        self.create_site_model()

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
        self.driver_config = load_driver_yaml(config.get('driver_config'))
        self.technology_config = load_tech_yaml(config.get('technology_config'))
        self.plant_config = load_plant_yaml(config.get('plant_config'))

    def create_site_model(self):
        # Create a site-level component
        site_config = self.plant_config.get('site', {})
        site_component = om.IndepVarComp()
        site_component.add_output('latitude', val=site_config.get('latitude', 0.0))
        site_component.add_output('longitude', val=site_config.get('longitude', 0.0))
        site_component.add_output('elevation_m', val=site_config.get('elevation_m', 0.0))
        site_component.add_output('time_zone', val=site_config.get('time_zone', 0))

        # Add boundaries if they exist
        site_config = self.plant_config.get('site', {})
        boundaries = site_config.get('boundaries', [])
        for i, boundary in enumerate(boundaries):
            site_component.add_output(f'boundary_{i}_x', val=np.array(boundary.get('x', [])))
            site_component.add_output(f'boundary_{i}_y', val=np.array(boundary.get('y', [])))

        self.prob = om.Problem()
        self.model = self.prob.model
        self.model.add_subsystem('site', site_component, promotes=['*'])
    
    def create_plant_model(self):
        """
        Create the plant-level model.

        This method creates an OpenMDAO group that contains all the technologies.
        It uses the plant configuration but not the driver or technology configuration.

        Information at this level might be used by any technology and info stored here is
        the same for each technology. This includes site information, project parameters,
        control strategy, and finance parameters.
        """
        # Create a plant-level component
        plant_component = om.IndepVarComp()
        plant_component.add_output('plant_component_example_value', val=1.)
        project_parameters = self.plant_config.get('project_parameters', {})
        for key, value in project_parameters.items():
            plant_component.add_output(key, val=value)

        # Add control strategy parameters
        control_strategy = self.plant_config.get('control_strategy', {})
        for key, value in control_strategy.items():
            plant_component.add_output(key, val=value)

        # Add finance parameters
        finance_parameters = self.plant_config.get('finance_parameters', {})
        for key, value in finance_parameters.items():
            plant_component.add_output(key, val=value)

        plant_group = om.Group()
        plant_group.add_subsystem('plant_info', plant_component, promotes=['*'])

        # Create the plant model group and add components
        self.plant = self.model.add_subsystem('plant', plant_group, promotes=['*'])

    def create_technology_models(self):
        # loop through each technology and instantiate an OpenMDAO object (assume it exists)
        # for each technology

        self.technology_objects = []
        self.tech_names = []
        self.cost_models = []
        self.financial_models = []

        # Create a technology group for each technology
        for tech_name, tech_config in self.technology_config['technologies'].items():
            tech_group = self.plant.add_subsystem(tech_name, om.Group())

            tech_class = supported_models[tech_config['performance_model']['model']]

            tech_object = tech_class(self.plant_config, tech_config)

            self.technology_objects.append(tech_object)
            self.tech_names.append(tech_name)
            tech_group.add_subsystem(tech_name, tech_object.get_performance_model(), promotes=['*'])

            # Add cost model
            cost_model = tech_object.get_cost_model()
            self.cost_models.append(cost_model)
            if cost_model is not None:
                tech_group.add_subsystem(f'{tech_name}_cost', cost_model, promotes=['*'])

            # Add financial model
            financial_model = tech_object.get_financial_model()
            self.financial_models.append(financial_model)
            if financial_model is not None:
                tech_group.add_subsystem(f'{tech_name}_financial', financial_model, promotes=['*'])

    def connect_technologies(self):
        technology_interconnections = self.plant_config.get('technology_interconnections', [])

        self.transport_objects = []

        # loop through each linkage and instantiate an OpenMDAO object (assume it exists) for
        # the connection type (e.g. cable, pipeline, etc)
        for connection in technology_interconnections:
            if len(connection) == 4:
                source_tech, dest_tech, transport_item, transport_type = connection

                # make the connection_name based on source, dest, item, type
                connection_name = f'{source_tech}_to_{dest_tech}_{transport_type}'

                # Create the transport object
                transport_object = supported_models[transport_type]()
                self.transport_objects.append(transport_object)
                connection_component = transport_object.get_performance_model()

                # Add the connection component to the model
                self.plant.add_subsystem(connection_name, connection_component)

                # Connect the source technology to the connection component
                self.plant.connect(f'{source_tech}.{transport_item}', f'{connection_name}.{transport_item}_input')

                # Connect the connection component to the destination technology
                self.plant.connect(f'{connection_name}.{transport_item}_output', f'{dest_tech}.{transport_item}')

            elif len(connection) == 3:
                # connect directly from source to dest
                source_tech, dest_tech, connected_parameter = connection

                self.plant.connect(f'{source_tech}.{connected_parameter}', f'{dest_tech}.{connected_parameter}')

            else:
                err_msg = f'Invalid connection: {connection}'
                raise ValueError(err_msg)


        # TODO: connect outputs of the technology models to the cost and financial models of the same name if the cost and financial models are not None

        self.plant.options['auto_order'] = True

    def create_driver_model(self):
        """
        Add the driver to the OpenMDAO model.
        """
        if 'driver' in self.driver_config:
            myopt = PoseOptimization(self.driver_config)
            myopt.set_driver(self.prob)
            myopt.set_objective(self.prob)
            myopt.set_design_variables(self.prob)
            myopt.set_constraints(self.prob)

    def run(self):
        # do model setup based on the driver config
        # might add a recorder, driver, set solver tolerances, etc

        # Add a recorder if specified in the driver config
        if 'recorder' in self.driver_config:
            recorder_config = self.driver_config['recorder']
            recorder = om.SqliteRecorder(recorder_config['file'])
            self.model.add_recorder(recorder)

        self.prob.setup()

        self.prob.run_driver()

    def post_process(self):
        self.prob.model.list_inputs(units=True)
        self.prob.model.list_outputs(units=True)

        # loop through technologies and post process outputs
        for idx_tech, (tech_name, tech_config) in enumerate(self.technology_config['technologies'].items()):
            self.technology_objects[idx_tech].post_process()

