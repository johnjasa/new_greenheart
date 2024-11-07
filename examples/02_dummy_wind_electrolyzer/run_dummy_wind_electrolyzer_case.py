from new_greenheart.core.GreenHEARTModel import GreenHEARTModel

# Create a GreenHEART model
gh = GreenHEARTModel('dummy_wind_electrolyzer_case.yaml')

# Run the model
gh.run()

gh.post_process()