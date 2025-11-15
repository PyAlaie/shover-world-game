from pathlib import Path

class Paths:
    BASE_DIR = Path(__file__).parent
    DATA_PATH = BASE_DIR / 'data'

    maps_path = Path('maps')

class EnvironmentVars:
    n_rows = 6
    n_cols = 6

    number_of_boxes = 2
    number_of_lavas = 2
    number_of_barriers = 2

    max_timestep = 400
    initial_stamina = 1000
    initial_force = 40
    unit_force = 10 
    r_lava = initial_force
    perf_sq_initial_age = 5 # set the value

    seed = 42
