from new_greenheart.core.baseclasses.converter_base_class import ConverterBaseClass


class ElectrolyzerBaseClass(ConverterBaseClass):
    def __init__(self, plant_config, tech_config):
        super().__init__(plant_config, tech_config)