import json
from pyxdsm.XDSM import XDSM, FUNC
from collections import OrderedDict

# Function to create an XDSM diagram based on the given configuration
def create_xdsm_from_config(config, output_file='connections_xdsm.pdf'):
    # Create an XDSM object
    x = XDSM(use_sfmath=True)

    # Use an OrderedDict to keep the order of technologies
    technologies = OrderedDict()
    for conn in config["technology_interconnections"]:
        technologies[conn[0]] = None  # Source
        technologies[conn[1]] = None  # Destination

    # Add systems to the XDSM
    for tech in technologies.keys():
        x.add_system(tech, FUNC, tech)

    # Add connections
    for conn in config["technology_interconnections"]:
        if len(conn) == 3:
            source, destination, data = conn
            connection_label = data
        else:
            source, destination, data, label = conn

        connection_label = rf"\text{{{data} {'via'} {label}}}"

        x.connect(source, destination, connection_label)

    # Write the diagram to a file
    x.write(output_file)
    print(f"XDSM diagram written to {output_file}.tex")

# Example usage
if __name__ == "__main__":
    config_path = "config.json"  # Path to the input JSON config file
    output_path = "xdsm_diagram"  # Output XDSM file prefix (without extension)

    with open(config_path, 'r') as f:
        config = json.load(f)

    create_xdsm_from_config(config, output_path)
