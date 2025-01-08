# Development guidelines

W.e've already had divergent codebases in the future due to fast-paced project needs and tight timelines.
To make this better, we're trying to standardize the way we develop code for GreenHEART in a way that's beneficial for developers, does not slow progress, and is sustainable for the future.
This document outlines the guidelines for developing code for GreenHEART

## Test development

Each new feature or bug fix should have a corresponding test.
Additionally, to help users create subsystems with the correct methods and attributes, we should have tests that users can run to check their subsystem models.

## Documentation development

The key to making GreenHEART more user-friendly is to have clear and concise documentation.
This includes docstrings for functions and classes, as well as high-level documentation for the tool itself.
We should also have a clear way to document the expected methods and attributes of classes so that users can develop their own models.

## Misc. development guidelines

- use numpydoc style for docstrings
- use numpy instead of lists for arrays
- use type hints for function arguments and return values