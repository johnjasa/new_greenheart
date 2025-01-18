import numpy as np
import openmdao.api as om
from greenheart.simulation.technologies.hydrogen.electrolysis.run_h2_PEM import run_h2_PEM
from greenheart.simulation.technologies.hydrogen.electrolysis.H2_cost_model import (
    basic_H2_cost_model,
)
from greenheart.simulation.technologies.hydrogen.electrolysis.PEM_costs_Singlitico_model import (
    PEMCostsSingliticoModel,
)
from greenheart.tools.eco.utilities import ceildiv

from new_greenheart.converters.hydrogen.electrolyzer_baseclass import ElectrolyzerPerformanceBaseClass, ElectrolyzerCostBaseClass, ElectrolyzerFinanceBaseClass


class ElectrolyzerPerformanceModel(ElectrolyzerPerformanceBaseClass):
    """
    An OpenMDAO component that wraps the PEM electrolyzer model.
    Takes electricity input and outputs hydrogen and oxygen generation rates.
    """
    def initialize(self):
        super().initialize()

    def setup(self):
        super().setup()

    def compute(self, inputs, outputs):
        config = self.options['tech_config']['details']
        plant_life = self.options['plant_config']['plant']['plant_life']
        electrolyzer_size_mw = config["rating"]
        electrolyzer_capex_kw = config["electrolyzer_capex"]

        # # IF GRID CONNECTED
        # if plant_config["plant"]["grid_connection"]:
        #     # NOTE: if grid-connected, it assumes that hydrogen demand is input and there is not
        #     # multi-cluster control strategies. This capability exists at the cluster level, not at the
        #     # system level.
        #     if config["sizing"]["hydrogen_dmd"] is not None:
        #         grid_connection_scenario = "grid-only"
        #         hydrogen_production_capacity_required_kgphr = config[
        #             "sizing"
        #         ]["hydrogen_dmd"]
        #         energy_to_electrolyzer_kw = []
        #     else:
        #         grid_connection_scenario = "off-grid"
        #         hydrogen_production_capacity_required_kgphr = []
        #         energy_to_electrolyzer_kw = np.ones(8760) * electrolyzer_size_mw * 1e3
        # # IF NOT GRID CONNECTED
        # else:
        hydrogen_production_capacity_required_kgphr = []
        grid_connection_scenario = "off-grid"
        energy_to_electrolyzer_kw = inputs['electricity']

        n_pem_clusters = int(
            ceildiv(electrolyzer_size_mw, config["cluster_rating_MW"])
        )

        ## run using greensteel model
        pem_param_dict = {
            "eol_eff_percent_loss": config["eol_eff_percent_loss"],
            "uptime_hours_until_eol": config["uptime_hours_until_eol"],
            "include_degradation_penalty": config[
                "include_degradation_penalty"
            ],
            "turndown_ratio": config["turndown_ratio"],
        }

        H2_Results, h2_ts, h2_tot, power_to_electrolyzer_kw = run_h2_PEM(
            electrical_generation_timeseries=energy_to_electrolyzer_kw,
            electrolyzer_size=electrolyzer_size_mw,
            useful_life=plant_life,
            n_pem_clusters=n_pem_clusters,
            pem_control_type=config["pem_control_type"],
            electrolyzer_direct_cost_kw=electrolyzer_capex_kw,
            user_defined_pem_param_dictionary=pem_param_dict,
            grid_connection_scenario=grid_connection_scenario,  # if not offgrid, assumes steady h2 demand in kgphr for full year  # noqa: E501
            hydrogen_production_capacity_required_kgphr=hydrogen_production_capacity_required_kgphr,
            debug_mode=False,
            verbose=False,
        )

        # Assuming `h2_results` includes hydrogen and oxygen rates per timestep
        outputs['hydrogen'] = H2_Results["Hydrogen Hourly Production [kg/hr]"]
        outputs['total_hydrogen_produced'] = H2_Results["Sim: Total H2 Produced [kg]"]

class ElectrolyzerCostModel(ElectrolyzerCostBaseClass):
    """
    An OpenMDAO component that computes the cost of a PEM electrolyzer.
    """
    def initialize(self):
        self.options.declare('tech_config', types=dict)
        self.options.declare('plant_config', types=dict)

    def setup(self):
        self.add_input('total_hydrogen_produced', val=0.0, units='kg/year')
        self.add_input('electricity', val=0.0, shape_by_conn=True, units='kW')
        # Define outputs: CapEx and OpEx costs
        self.add_output('CapEx', val=0.0, units='USD', desc='Capital expenditure')
        self.add_output('OpEx', val=0.0, units='USD/year', desc='Operational expenditure')

    def compute(self, inputs, outputs):
        # unpack inputs
        config = self.options['tech_config']['details']
        plant_config = self.options['plant_config']
        
        total_hydrogen_produced = float(inputs["total_hydrogen_produced"])
        electrolyzer_size_mw = config["rating"]
        useful_life = plant_config["plant"]["plant_life"]
        atb_year = plant_config["plant"]["atb_year"]

        electrolyzer_cost_model = config[
            "cost_model"
        ]  # can be "basic" or "singlitico2021"

        # run hydrogen production cost model - from hopp examples
        if config["location"] == "onshore":
            offshore = 0
        else:
            offshore = 1

        if electrolyzer_cost_model == "basic":
            (
                cf_h2_annuals,
                electrolyzer_total_capital_cost,
                electrolyzer_OM_cost,
                electrolyzer_capex_kw,
                time_between_replacement,
                h2_tax_credit,
                h2_itc,
            ) = basic_H2_cost_model(
                config["electrolyzer_capex"],
                config["time_between_replacement"],
                electrolyzer_size_mw,
                useful_life,
                atb_year,
                inputs["electricity"],
                total_hydrogen_produced,
                0.0,
                0.0,
                include_refurb_in_opex=False,
                offshore=offshore,
            )
        elif electrolyzer_cost_model == "singlitico2021":
            P_elec = electrolyzer_size_mw * 1e-3  # [GW]
            RC_elec = config["electrolyzer_capex"]  # [USD/kW]

            pem_offshore = PEMCostsSingliticoModel(elec_location=offshore)

            (
                electrolyzer_capital_cost_musd,
                electrolyzer_om_cost_musd,
            ) = pem_offshore.run(P_elec, RC_elec)

            electrolyzer_total_capital_cost = (
                electrolyzer_capital_cost_musd * 1e6
            )  # convert from M USD to USD
            electrolyzer_OM_cost = electrolyzer_om_cost_musd * 1e6  # convert from M USD to USD

        else:
            msg = (
                f"Electrolyzer cost model must be one of['basic', 'singlitico2021'] but "
                f"'{electrolyzer_cost_model}' was given"
            )
            raise ValueError(msg)

        outputs['CapEx'] = electrolyzer_total_capital_cost
        outputs['OpEx'] = electrolyzer_OM_cost

class ElectrolyzerFinanceModel(ElectrolyzerFinanceBaseClass):
    """
    Placeholder for the financial model of the PEM electrolyzer.
    """
    def setup(self):
        self.add_output('LCOH', val=0.0, units='USD/kg', desc='Levelized cost of hydrogen')

    def compute(self, inputs, outputs):
        outputs['LCOH'] = 4.11  # Placeholder value
