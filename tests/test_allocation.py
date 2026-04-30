import numpy as np

from realgrowthsim.model.params import ScenarioConfig, SharePolicy
from realgrowthsim.optimize.cvar import cvar_allocation, sample_cvar
from realgrowthsim.optimize.kkt import clipped_kkt_allocation
from realgrowthsim.optimize.robust import robust_concentration_condition
from realgrowthsim.optimize.shares import recommend_shares


def test_robust_concentration_and_diversification_condition():
    robust, top, margin = robust_concentration_condition({"a": 10.0, "b": 4.0}, rho=0.2)
    assert robust
    assert top == "a"
    assert margin > 0
    robust, _, _ = robust_concentration_condition({"a": 10.0, "b": 9.0}, rho=0.2)
    assert not robust


def test_kkt_allocation_respects_floors_and_budget():
    shares = clipped_kkt_allocation({"a": 2.0, "b": 1.0}, {"a": 0.1, "b": 0.1}, 0.8, psi=0.5)
    assert shares["a"] >= 0.1
    assert shares["b"] >= 0.1
    assert abs(sum(shares.values()) - 0.8) < 1e-8


def test_cvar_expected_tail_loss_and_allocation():
    assert sample_cvar([1.0, 2.0, 3.0, 4.0], alpha=0.5) == 3.5
    loss_matrix = np.array([[1.0, 3.0], [2.0, 1.0], [4.0, 0.5]])
    shares = cvar_allocation(loss_matrix, floors=np.array([0.1, 0.1]), budget=1.0, alpha=0.8)
    assert np.all(shares >= 0.1 - 1e-8)
    assert abs(float(shares.sum()) - 1.0) < 1e-6


def test_share_policy_output_valid():
    config = ScenarioConfig()
    config.share_policy.policy = SharePolicy.kkt
    shares = recommend_shares(config.initial_state, config.params, config.share_policy)
    assert sum(shares.values()) <= config.params.investment.s_bar + 1e-12
