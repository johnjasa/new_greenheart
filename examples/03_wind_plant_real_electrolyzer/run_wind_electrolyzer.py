from new_greenheart.core.greenheart_model import GreenHEARTModel


# Create a GreenHEART model
gh = GreenHEARTModel('wind_plant_electrolyzer.yaml')

# Run the model
gh.run()

gh.post_process()