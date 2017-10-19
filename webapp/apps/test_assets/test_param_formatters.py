import json
import pytest
import taxcalc
import numpy as np

from ..taxbrain.views import (parse_errors_warnings, read_json_reform,
                              get_reform_from_gui, get_reform_from_file)
from ..taxbrain.helpers import (get_default_policy_param_name, to_json_reform)

from test_reform import (test_coverage_fields, test_coverage_reform,
                         test_coverage_json_reform,
                         test_coverage_exp_read_json_reform,
                         errors_warnings_fields, errors_warnings_reform,
                         errors_warnings_json_reform,
                         errors_warnings_exp_read_json_reform,
                         errors_warnings, exp_errors_warnings,
                         map_back_to_tb)

from test_assumptions import (assumptions_text, exp_assumptions_text, no_assumptions_text)

START_YEAR = 2017

@pytest.fixture
def default_params_Policy():
    return taxcalc.Policy.default_data(start_year=START_YEAR,
                                       metadata=True)


###############################################################################
# Test get_default_policy_param_name
@pytest.mark.parametrize("param,exp_param",
                         [("FICA_ss_trt", "_FICA_ss_trt"),
                          ("ID_BenefitSurtax_Switch_0", "_ID_BenefitSurtax_Switch_medical"),
                          ("CG_brk3_cpi", "_CG_brk3_cpi")])
def test_get_default_policy_param_name_passing(param, exp_param, default_params_Policy):
    act_param = get_default_policy_param_name(param, default_params_Policy)
    assert act_param == exp_param

@pytest.mark.parametrize("param", ["CG_brk3_extra_cpi", "not_a_param"])
def test_get_default_policy_param_name_failing0(param, default_params_Policy):
    match="Received unexpected parameter: {0}".format(param)
    with pytest.raises(ValueError, match=match):
        get_default_policy_param_name(param, default_params_Policy)


def test_get_default_policy_param_name_failing1(default_params_Policy):
    param = "ID_BenefitSurtax_Switch_idx"
    match="Parsing {0}: Index {0} not in range".format(param, "idx")
    with pytest.raises(ValueError, match=match):
        get_default_policy_param_name(param, default_params_Policy)


def test_get_default_policy_param_name_failing2(default_params_Policy):
    param = "ID_BenefitSurtax_Switch_12"
    match="Parsing {}: Expected integer for index but got {}".format(param, "12")
    with pytest.raises(ValueError, match=match):
        get_default_policy_param_name(param, default_params_Policy)

###############################################################################
# Test to_json_reform
@pytest.mark.parametrize(
    ("fields,exp_reform"),
    [(test_coverage_fields, test_coverage_reform),
     (errors_warnings_fields, errors_warnings_reform)]
)
def test_to_json_reform(fields, exp_reform):
    act, _ = to_json_reform(fields, START_YEAR)
    print(exp_reform)
    print(act)
    np.testing.assert_equal(act, exp_reform)

###############################################################################
# Test parse_errors_warnings
def test_parse_errors_warnings():
    act = parse_errors_warnings(errors_warnings, map_back_to_tb)
    np.testing.assert_equal(exp_errors_warnings, act)


###############################################################################
# Test read_json_reform
@pytest.mark.parametrize(
    ("test_reform,test_assump,map_back_to_tb,exp_reform,exp_assump,"
     "exp_errors_warnings"),
    [(test_coverage_json_reform, no_assumptions_text,
      map_back_to_tb, test_coverage_exp_read_json_reform,
      json.loads(no_assumptions_text),
      {'errors': {}, 'warnings': {}}),
     (test_coverage_json_reform, assumptions_text,
      map_back_to_tb, test_coverage_exp_read_json_reform,
      exp_assumptions_text,
      {'errors': {}, 'warnings': {}}),
     (errors_warnings_json_reform, no_assumptions_text,
      map_back_to_tb, errors_warnings_exp_read_json_reform,
      json.loads(no_assumptions_text), exp_errors_warnings)
     ]
)
def test_read_json_reform(test_reform, test_assump, map_back_to_tb,
                          exp_reform, exp_assump, exp_errors_warnings):
    act_reform, act_assump, act_errors_warnings = read_json_reform(
        test_reform,
        test_assump,
        map_back_to_tb
    )
    np.testing.assert_equal(exp_reform, act_reform)
    np.testing.assert_equal(exp_assump, act_assump)
    np.testing.assert_equal(exp_errors_warnings, act_errors_warnings)
