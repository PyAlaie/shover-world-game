import numpy as np
import pytest
from environment import ShoverWorldEnv
from enums import Actions, Objects
import settings


@pytest.fixture
def env():
    """Create a deterministic environment with a fixed seed."""
    settings.EnvironmentVars.seed = 0
    e = ShoverWorldEnv(render_mode=None, map_name=None)
    obs, _ = e.reset()
    return e


def test_reset_structure(env):
    """Ensure reset returns the correct observation keys."""
    obs, _ = env.reset()
    assert "grid" in obs
    assert "stamina" in obs
    assert "previous_selected_position" in obs
    assert "previous_action" in obs
    assert isinstance(obs["grid"], np.ndarray)


def test_move_action_empty_cell(env):
    """
    If the agent tries to move a box but the selected cell has no box,
    _apply_move_action returns 4 → stamina should decrease by 1.
    """
    initial_stamina = env.stamina
    pos = np.array([0, 0])  # most likely empty
    action = {
        "position": pos,
        "z": Actions.MoveUp.value  # Any move action
    }

    _, reward, _, _, _ = env.step(action)

    assert env.stamina == initial_stamina - 1
    assert reward == 0  # no reward for invalid move


def test_move_action_on_barrier(env):
    """
    Selecting a barrier results in code path returning 2 (cannot move).
    stamina should decrease by 1.
    """
    # Manually place a barrier at a known location
    env.map[1][1] = Objects.Barrier.value

    initial_stamina = env.stamina
    pos = np.array([1, 1])

    action = {
        "position": pos,
        "z": Actions.MoveRight.value,
    }

    _, reward, _, _, _ = env.step(action)

    assert env.stamina == initial_stamina - 1
    assert reward == 0
    assert env.moving_positions == {}


def test_barrier_maker_action(env):
    """
    BarrierMaker should:
    - If perfect squares exist → increase stamina and give reward.
    - If not → stamina -= 1.
    """
    initial_stamina = env.stamina

    # FORCE one perfect square so behavior is deterministic
    class DummySq:
        extend = 3
        age = 10

        def apply_barrier_maker(self, grid):
            return grid  # No-op

    env.perfect_squares = [DummySq()]

    action = {
        "position": np.array([0, 0]),
        "z": Actions.BarrierMaker.value
    }

    _, reward, _, _, _ = env.step(action)

    # Perfect square with extend=3 → gain (3 - 2)^2 = 1 stamina and reward=10*1
    assert env.stamina == initial_stamina + 1
    assert reward == 10
    assert len(env.perfect_squares) == 0


def test_barrier_maker_no_squares(env):
    """
    When there is no perfect square:
    BarrierMaker should penalize stamina by -1.
    """
    env.perfect_squares = []
    initial_stamina = env.stamina

    action = {
        "position": np.array([0, 0]),
        "z": Actions.BarrierMaker.value
    }

    _, reward, _, _, _ = env.step(action)
    assert env.stamina == initial_stamina - 1
    assert reward == 0


def test_hellify_no_valid_square(env):
    """
    Hellify selects the first perfect square with extend >= 5.
    If none exist → stamina -= 1.
    """
    env.perfect_squares = []  # no squares at all
    initial_stamina = env.stamina

    action = {
        "position": np.array([0, 0]),
        "z": Actions.Hellify.value
    }

    _, reward, _, _, _ = env.step(action)

    assert env.stamina == initial_stamina - 1
    assert reward == 0


def test_step_returns_correct_format(env):
    """Check that step returns Gym-style 5-tuple."""
    action = {
        "position": np.array([0, 0]),
        "z": Actions.MoveUp.value
    }

    obs, reward, terminated, truncated, info = env.step(action)

    assert isinstance(obs, dict)
    assert "grid" in obs
    assert isinstance(reward, (int, float))
    assert isinstance(terminated, bool)
    assert isinstance(truncated, bool)
    assert isinstance(info, dict)
