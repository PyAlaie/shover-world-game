from pathlib import Path

class Paths:
    BASE_DIR = Path(__file__).parent
    maps_path = BASE_DIR / 'maps'

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
    perf_sq_initial_age = 10 # set the value

    seed = 42

class GuiVars:
    COLOR_EMPTY = (240, 240, 240)
    COLOR_BARRIER = (80, 80, 80)
    COLOR_LAVA = (200, 40, 40)

    BOX_COLORS = [
        (255, 179, 186),
        (255, 223, 186),
        (255, 255, 186),
        (186, 255, 201),
        (186, 225, 255),
        (200, 200, 255),
        (220, 200, 255),
        (255, 200, 220),
        (210, 255, 230),
        (255, 230, 180),
    ]
    HUD_BG = (30, 30, 30)
    HUD_TEXT = (250, 250, 250)
    GRID_LINE = (200, 200, 200)

    MAX_WINDOW_WIDTH = 1000
    MAX_WINDOW_HEIGHT = 900
    HUD_HEIGHT = 44