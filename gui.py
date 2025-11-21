import pygame
import sys
from typing import Tuple
import numpy as np
import settings
from environment import ShoverWorldEnv
from enums import Actions, is_box

COLOR_EMPTY = settings.GuiVars.COLOR_EMPTY
COLOR_BARRIER = settings.GuiVars.COLOR_BARRIER
COLOR_LAVA = settings.GuiVars.COLOR_LAVA
BOX_COLORS = settings.GuiVars.BOX_COLORS
HUD_BG = settings.GuiVars.HUD_BG
HUD_TEXT = settings.GuiVars.HUD_TEXT
GRID_LINE = settings.GuiVars.GRID_LINE

MAX_WINDOW_WIDTH = settings.GuiVars.MAX_WINDOW_WIDTH
MAX_WINDOW_HEIGHT = settings.GuiVars.MAX_WINDOW_HEIGHT
HUD_HEIGHT = settings.GuiVars.HUD_HEIGHT


class GuiRenderer:
    def __init__(
        self,
        window_max_size: Tuple[int, int] = (MAX_WINDOW_WIDTH, MAX_WINDOW_HEIGHT),
        caption: str = "GridWorld",
        fps: int = 30,
        show_grid_lines: bool = True,
        grid_h=4,
        grid_w=6,
    ):
        pygame.init()
        pygame.font.init()
        self.caption = caption
        pygame.display.set_caption(self.caption)
        self.fps = fps
        self.clock = pygame.time.Clock()
        self.screen = None
        self.window_max_size = window_max_size
        self.show_grid_lines = show_grid_lines

        self.cursor_x = 0
        self.cursor_y = 0

        self.grid_h = grid_h 
        self.grid_w = grid_w

        self.selected_cell = None
        self.action_type = None

        # last action returned from keyboard (so external code can read it)
        self._last_key_action = None
        # flag: whether the user requested quit
        self._quit = False

        # font sizes will be set after knowing cell size
        self.font = pygame.font.SysFont("Arial", 18)
        self.big_font = pygame.font.SysFont("Arial", 20, bold=True)

    def _ensure_screen(self, grid_shape):
        """
        Initialize Pygame screen sized to fit grid (auto-scale).
        """
        nrows, ncols = grid_shape
        max_w, max_h = self.window_max_size

        # compute available area for grid (subtract HUD)
        avail_h = max_h - HUD_HEIGHT
        avail_w = max_w

        # choose cell size to fit both directions
        cell_size_w = max(4, avail_w // ncols)
        cell_size_h = max(4, avail_h // nrows)
        cell_size = min(cell_size_w, cell_size_h)

        # compute final window size based on chosen cell_size
        win_w = cell_size * ncols
        win_h = cell_size * nrows + HUD_HEIGHT

        # create or update screen
        if self.screen is None:
            self.screen = pygame.display.set_mode((win_w, win_h))
        else:
            # if size changed, recreate window surface
            if self.screen.get_width() != win_w or self.screen.get_height() != win_h:
                self.screen = pygame.display.set_mode((win_w, win_h))

        self.cell_size = cell_size
        self.grid_origin = (0, HUD_HEIGHT)
        self.grid_size_px = (win_w, win_h - HUD_HEIGHT)

        # set fonts sized relative to cell
        # number font should be readable inside a cell
        num_font_size = max(12, min(24, cell_size // 2))
        hud_font_size = max(14, min(28, HUD_HEIGHT - 8))
        self.font = pygame.font.SysFont("Arial", num_font_size)
        self.big_font = pygame.font.SysFont("Arial", hud_font_size, bold=True)

    def render(self, env) -> None:
        grid = env.map
        if not isinstance(grid, np.ndarray) or grid.ndim != 2:
            raise ValueError("env.grid must be a 2D numpy array")

        self._ensure_screen(grid.shape)
        surf = self.screen
        surf.fill((0, 0, 0))  # background

        # Draw HUD background
        pygame.draw.rect(
            surf, HUD_BG, pygame.Rect(0, 0, surf.get_width(), HUD_HEIGHT)
        )

        # Draw HUD text (stamina, timestep)
        stamina_text = f"Stamina: {getattr(env, 'stamina', '?')}"
        timestep_text = f"Timestep: {getattr(env, 'timestep', '?')}"
        
        hud_surface = self.big_font.render(stamina_text + "   |   " + timestep_text, True, HUD_TEXT)
        surf.blit(hud_surface, (8, (HUD_HEIGHT - hud_surface.get_height()) // 2))

        # draw grid cells
        nrows, ncols = grid.shape
        cs = self.cell_size
        gx, gy = self.grid_origin

        for r in range(nrows):
            for c in range(ncols):
                val = grid[r, c]
                rect = pygame.Rect(gx + c * cs, gy + r * cs, cs, cs)
                # choose color based on tile value
                if val == 0:
                    color = COLOR_EMPTY
                elif val == 100:
                    color = COLOR_BARRIER
                elif val == -100:
                    color = COLOR_LAVA
                elif 1 <= val <= 1000:  # treat 1..10 and others as boxes (use modulo palette)
                    # box index might be >10; map it
                    idx = int(val - 1) % len(BOX_COLORS)
                    color = BOX_COLORS[idx]
                else:
                    color = COLOR_EMPTY

                pygame.draw.rect(surf, color, rect)

                # optional grid lines
                if self.show_grid_lines:
                    pygame.draw.rect(surf, GRID_LINE, rect, 1)

        pygame.display.flip()
        # tick FPS
        self.clock.tick(self.fps)

    def process_events(self):
        """
            returns
            {
                "position": (x,y),
                "z": z
            }
        """
        
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                self._quit = True
                return None
            
            if ev.type == pygame.MOUSEBUTTONDOWN:
                mx, my = ev.pos
                # convert pixel coords to grid coords
                x = mx // self.cell_size
                y = (my - HUD_HEIGHT) // self.cell_size  # adjust for HUD
                x = max(0, min(self.grid_w - 1, x))
                y = max(0, min(self.grid_h - 1, y))

                temp = x
                x= y 
                y = temp

                self.selected_cell = (x, y)
                print("Selected cell:", self.selected_cell)

            if ev.type == pygame.KEYDOWN and self.selected_cell is not None:
                if ev.key == pygame.K_UP:
                    self.action_type = Actions.MoveUp.value
                elif ev.key == pygame.K_LEFT:
                    self.action_type = Actions.MoveLeft.value
                elif ev.key == pygame.K_DOWN:
                    self.action_type = Actions.MoveDown.value
                elif ev.key == pygame.K_RIGHT:
                    self.action_type = Actions.MoveRight.value
                elif ev.key == pygame.K_b:
                    self.action_type = Actions.BarrierMaker.value
                elif ev.key == pygame.K_h:
                    self.action_type = Actions.Hellify.value

                x,y = self.selected_cell
                z = self.action_type
                self.action_type = None
                self.selected_cell = None
                return {"position": (x,y), "z": z}

    def should_quit(self) -> bool:
        return self._quit

    def close(self):
        pygame.quit()


def main():
    env = ShoverWorldEnv("human", map_name="map2.txt")
    env.reset()
    
    renderer = GuiRenderer(window_max_size=(900, 700), fps=30, grid_h=env.n_rows, grid_w=env.n_cols)

    human_control = True  
    agent_control = True
    terminated = truncated = False
    try:
        running = True
        while running:
            key_action = renderer.process_events()
            if renderer.should_quit():
                break

            if human_control and key_action is not None:
                action = key_action
                print(action)
                obs, reward, terminated, truncated, info = env.step(action)
            
            elif agent_control: # random agent
                while True:
                    action = env.action_space.sample()
                    if is_box(env.map[action["position"][0]][action["position"][1]]):
                        break
                print(action)
                obs, reward, terminated, truncated, info = env.step(action)
            
            if terminated or truncated:
                running = False

            renderer.render(env)

        font = pygame.font.SysFont(None, 72)
        text = font.render("GAME OVER", True, (255, 0, 0))
        text_rect = text.get_rect(center=(renderer.screen.get_width()//2,
                                        renderer.screen.get_height()//2))

        renderer.screen.blit(text, text_rect)
        pygame.display.flip()

        wait = True
        while wait:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    wait = False

    except Exception as e:
        print(e)
    finally:
        renderer.close()
        pygame.quit()
        sys.exit(0)


if __name__ == "__main__":
    main()
