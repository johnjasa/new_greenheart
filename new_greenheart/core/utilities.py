import json
from pyxdsm.XDSM import XDSM, FUNC
from collections import OrderedDict


def create_xdsm_from_config(config, output_file='connections_xdsm'):
    """
    Create an XDSM diagram from a given plant configuration and save it to a pdf file.

    Parameters
    ----------
    config : dict
        Configuration dictionary containing technology interconnections.
    output_file : str, optional
        The name of the output file where the XDSM diagram will be saved.
    """
    # Create an XDSM object
    x = XDSM(use_sfmath=True)

    # Use an OrderedDict to keep the order of technologies
    technologies = OrderedDict()
    if "technology_interconnections" not in config:
        return

    for conn in config["technology_interconnections"]:
        technologies[conn[0]] = None  # Source
        technologies[conn[1]] = None  # Destination

    # Add systems to the XDSM
    for tech in technologies.keys():
        tech_label = tech.replace('_', r'\_')
        x.add_system(tech, FUNC, rf"\text{{{tech_label}}}")

    # Add connections
    for conn in config["technology_interconnections"]:
        if len(conn) == 3:
            source, destination, data = conn
            connection_label = data
        else:
            source, destination, data, label = conn

        source_label = source.replace('_', r'\_')
        destination_label = destination.replace('_', r'\_')
        connection_label = rf"\text{{{data} {'via'} {label}}}"

        x.connect(source, destination, connection_label)

    # Write the diagram to a file
    x.write(output_file)
    print(f"XDSM diagram written to {output_file}.tex")
