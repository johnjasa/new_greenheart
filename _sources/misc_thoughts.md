# Miscellaneous Thoughts

This is a non-exhaustive collection of items that have come up in discussions about ODIES.
It's meant to be a place to jot down ideas and thoughts that don't fit neatly into the other documents.
Most of these will become issues in the repo once they're fleshed out a bit more.

- **Resource and LCA handling**
	- Clearly define and differentiate between natural resources and feedstocks in the model.
		- If it's being used to produce power it should be a natural resource
		- If it's being used to produce something else, it's a feedstock
    - Implement a structure to handle feedstocks at the site level, considering potential duplications for LCA purposes.
- **Grid Connectivity**
	- Add a clear indicator at the configuration level to specify whether a site is grid-connected, hybrid, or off-grid.
	- Move forward with LCA as a postprocessing step to reduce computational costs while ensuring interpolation for Cambium data on a per-year basis.
	- Investigate scenarios where optimizing for LCA directly might be necessary.
    - Incorporate Dakota's suggestion to ensure LCA postprocessing handles grid-connected assumptions for technologies like steel and ammonia; might be needed later.
- **Technology and Resource Flow Diagram**
    - Develop an example high-level flow diagram to illustrate relationships between technologies, feedstocks, and resources, once we have the definitions more fleshed out.
- **Class structure within ODIES**
	- We should have nested inheritance for technologies that will share methods; e.g. `ConverterBaseClass` -> `ElectrolyzerBaseClass` -> `BERTElectrolyzerWrapper`
- **Default config handling**
	- We should have no default values; everything should be user-provided says Chris
- **Future technology adds**
	- Marine carbon capture, it's currently implemented like ammonia and steel
- **Steel handling**
	- Currently the hydrogen and electricity inputs are considered feedstocks
	- We need some way for LCOH to be passed from the electrolyzer
	- [Here's the EAF to DRI split out model](https://github.com/kbrunik/HOPP/tree/steel-model/ODIES/simulation/technologies/steel)
- **Electrolyzers**
	- BERT should be the one-stop-shop for most electrolyzer models
	- We want to have a standalone BERT config that can be passed wholesale through ODIES
- **Financials**
	- Very unclear how we'll getting the timing of the financial calculations correct; there are some places in the current ODIES we we have a partial financial stackup, e.g. computing LCOH of a plant before passing it to a steel processing module

### Action items:
- [x] make converters have an intermediary class (Electrolyzer example)
- [x] make a figure showing how this inheritance works
- [x] make docs online for ODIES
- [x] make the ammonia model take in a flat hydrogen array and convert it to be time-based
- [x] change the ammonia model so it's based on the amount of hydrogen produced (summed)
- [x] I suggest me drawing up a block diagram for these, show inputs/outputs
- [x] financials are unclear; give this more thought about how they're connected
- [x] make figures for each of the examples showing the technologies and connections; could use XDSM for this, automate the process somewhat
- [ ] add a logger note or warning that the ammonia's assumed to be produced in a flat way
- [ ] make an example of a class that has a method that returns cluster size, hub height, do this with an attr not the actual method now that I'm typing this
- [ ] figure out how to make get_inputs and get_outputs in a good way
- [ ] make the OM model use the get_inputs and get_outputs methods
- [ ] figure out how to best handle the saved off data and reruns; OM pickle, something else, a flag on the compute method that just loads in the results?
- [ ] start a yaml library
- [ ] investigate Kaitlin's intern steel model
- [ ] add a notion of a splitter; wind producing electricity to be split out for use in example 7
- [ ] differentiate between "inputs" and "outputs" in OpenMDAO parlance and what it means for the model; inputs or outputs to the tank, for example, might not be a literal input or output in the code sense
- [ ] write a guide for how to make a technology wrapper in the current ODIES setup
- [ ] figure out how to have inputs and outputs defined in a clear way, including required inputs and outputs for a given technology type
- [ ] how to handle when a technology has an input and an output of the same energy type; like a tank storing hydrogen that has some coming in and some going out; can't have the same OM variable name so should we just append _in or _out?