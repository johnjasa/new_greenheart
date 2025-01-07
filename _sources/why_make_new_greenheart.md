# Why make new GreenHEART?

GreenHEART has already proven itself useful as a tool that can analyze and design complex hybrid systems producing electricity, hydrogen, steel, and more.
However, these developments came in waves across multiple disparate projects, leading to a sometimes disjoint codebase.
In an effort to streamline and modularize GreenHEART to make it more effective and capable for necessary future studies, we are devoting time to redesigning it from the ground up.
This page discusses some of the high-level decisions and mindsets that we've used throughout this process.

## What does it mean to "modularize" GreenHEART?

Most of the current implementation of GreenHEART assumes that you are modeling a certain hybrid system architecture using a limited number of specific models.
As more projects call for using GreenHEART, we must make it easier to develop and add capability to the tool in a sustainable and clear way.
By making the internal framework of GreenHEART more agnostic to the technologies considered in the hybrid system design, we can allow for more user-defined modularized subsystems to be considered effectively.

Getting into the details, this means creating generalized components that GreenHEART can expect to behave in a certain way.

We introduce the ideas of "converters", which convert one resource into another.
Simple examples of converters include electrolyzers, wind turbines, solar PV panels, and more.
These converters can pass resources to other converters or "storage" components via "transporter" components.

Transporters include hydrogen pipelines, electricity cables, or anything that transports a resource.
In a broad sense, these might include delivery trucks or shipping vessels, though those are more for future consideration.

Storage components include batteries, hydrogen tanks; anything where you store a resource.

By combining instances of these different generalized components, we can study distinct hybrid systems in GreenHEART.
Internally, the GreenHEART framework just needs to know if a something is a converter, transporter, storage, or some other type of component.
Additionally, this allows users to develop their own components using the expected interface, and add in custom subsystems to their hybrid plant. 

## Why use OpenMDAO as the internal framework for GreenHEART?

Through a series of internal discussions, the GreenHEART dev team landed on using [NASA's OpenMDAO framework](https://github.com/OpenMDAO/OpenMDAO/) for this new version of the tool.

Using OpenMDAO for this gives quite a few benefits:
- a proven framework for complex data-passing within multidisciplinary systems
- automatically-generated visualization tools to help understand models and debug them
- internal units handling and conversion
- built-in nonlinear solvers to resolve model coupling
- built-in optimization and parameter sweep drivers
- multiple existing NREL tools use OpenMDAO, including [WISDEM](https://github.com/WISDEM/WISDEM/) and [WEIS](https://github.com/WISDEM/WEIS), so we can draw from institutional knowledge
- set up with gradient-based optimization in mind, which is not currently a focus for GreenHEART but this positions the tool well for potential future additions
- parallelization done using MPI, which is also not currently a focus but useful for the future

However, there are a few downsides to using OpenMDAO:
- an additional layer of code that developers must consider
- longer error stack traces that might seem daunting in the terminal
- potentially increased computational costs depending on problem type and size
- it isn't great at optimizing mixed-integer problems

The benefits outweighed the downsides, hence the team's choice to use OpenMDAO going forward.
Additionally, we can code GreenHEART in a way to minimize some of the potential issues, given that we're aware of them before refactoring GreenHEART.

## Where does HOPP come into play?

[HOPP](https://github.com/NREL/HOPP) is a well-structured and useful tool that analyzes hybrid plants producing electricity.
GreenHEART historically calls HOPP to obtain the plant's outputted electricity, which is then used downstream to feed into electrolyzers, steel, and other components.
The current setup of new GreenHEART largely works in the same way.

The end-goal of new GreenHEART is to remove this call to HOPP as a monolith and instead break out the individual technologies so they are all exposed equally to GreenHEART.
This would entail reworking the dispatch implementation so it is controlled by GreenHEART and not by HOPP, which is a non-trivial task.