from new_greenheart.transporters.power_combiner import CombinerPerformanceModel
import pytest
from pytest import approx
import numpy as np

import openmdao.api as om


np.random.seed(0)

def test_combiner_performance():
    prob = om.Problem()
    comp = CombinerPerformanceModel()
    prob.model.add_subsystem("comp", comp, promotes=["*"])
    ivc = om.IndepVarComp()
    ivc.add_output('electricity_input1', val=np.zeros(8760), units='kW')
    ivc.add_output('electricity_input2', val=np.zeros(8760), units='kW')
    prob.model.add_subsystem('ivc', ivc, promotes=['*'])

    prob.setup()

    electricity_input1 = np.random.rand(8760)
    electricity_input2 = np.random.rand(8760)
    electricity_output = electricity_input1 + electricity_input2

    prob.set_val('electricity_input1', electricity_input1, units='kW')
    prob.set_val('electricity_input2', electricity_input2, units='kW')
    prob.run_model()

    assert prob.get_val('electricity_output', units='kW') == approx(electricity_output, rel=1e-5)