from new_greenheart.core.greenheart_model import GreenHEARTModel


# Create a GreenHEART model
gh = GreenHEARTModel('07_wind_ammonia.yaml')

# Run the model
gh.run()

gh.post_process()