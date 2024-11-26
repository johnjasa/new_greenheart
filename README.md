# New GreenHEART planning

## Examples currently included

### 01_dummy_wind

This is the simplest example possible; a single technology is producing a single type of resource.
In this case, a mock wind turbine is ingesting wind speed data and outputting electricity.
This example is a stepping stone to develop more of the framework.

### 02_dummy_wind_electrolyzer

Now the mock wind turbine is coupled to a mock electrolyzer.
The electricity is coupled between the technologies through the framework's connection handling.

### 03_wind_plant_electrolyzer

We're now running an actual wind plant and grabbing meaningful electricity outputs and those electricity values are being passed to a mock electrolyzer.
This example helped work out how to pass in config data to a technology.

### 04_wind_plant_real_electrolyzer

Now the electrolyzer is the actual PEM model that exists in GreenHEART.
This provided another example of how to wrap a technology.

### 05_wind_h2_opt

This is the same system as the prior example, but we add plant optimization capability.
It's a simple optimization problem, but this shows how we can add a driver to the problem.

### 06_hopp_h2

This example introduces HOPP as a single block in the new GreenHEART paradigm.
This isn't where we want to be in the end of this GreenHEART reformulation, but it is an important stepping stone as it allows us to focus on the rest of the framework and non-HOPP technologies while treating HOPP as a monolith.
