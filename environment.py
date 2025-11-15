import gymnasium as gym
from gymnasium import spaces
import numpy as np
import os
from enums import Objects, Actions, Move_to_delta
from pathlib import Path
import settings

class ShoverWorldEnv(gym.Env):
    def __init__(
            self, 
            render_mode,
            map_name=None
        ):
        super().__init__()

        self.render_mode = render_mode

        self.n_rows = settings.EnvironmentVars.n_rows
        self.n_cols = settings.EnvironmentVars.n_cols
        self.max_timestep = settings.EnvironmentVars.max_timestep
        self.number_of_boxes = settings.EnvironmentVars.number_of_boxes
        self.number_of_barriers = settings.EnvironmentVars.number_of_barriers
        self.number_of_lavas = settings.EnvironmentVars.number_of_lavas
        self.stamina = settings.EnvironmentVars.initial_stamina
        self.initial_force = settings.EnvironmentVars.initial_force
        self.unit_force = settings.EnvironmentVars.unit_force
        self.perf_sq_initial_age = settings.EnvironmentVars.perf_sq_initial_age
        self.map_path = settings.Paths.maps_path
        self.seed = settings.EnvironmentVars.seed
        self.timestep = 0
        
        self.map_name = map_name

        self.moving_positions = {} # stored as {position, direction}
        self.new_moving_positions = {}
        self.stationary_move = False

        self.action_space = spaces.Dict({
            "position": spaces.MultiDiscrete([self.n_rows, self.n_cols]),
            "z": spaces.Discrete(len(Actions))
        })
        self.observation_space = spaces.Box(low=-100, high=100, shape=(self.n_rows,self.n_cols), dtype=np.int32)

    def step(self, action):
        position = action["position"]
        z = action["z"]

        if z == Actions.BarrierMaker:
            pass
        
        elif z == Actions.Hellify:
            pass

        else: # Action of moving, costs 4 staminas anyway (even if nothing happens)
            res = self._apply_move_action(position, z)

            i, j = position[0], position[1]
            
            if res == 3: # the head box was moved
                if self.moving_positions.get((i,j)) != action:
                    self.stamina -= settings.EnvironmentVars.initial_force
                
                new_position = position + Move_to_delta.get(action)
                self.moving_positions = {(new_position[0], new_position[1]): action}
            
            else:
                self.moving_positions = {}
                
            self.stamina -= 4
        
        self.timestep += 1

        if self._check_termination():
            self.terminated = True

    def _apply_move_action(self, position, action):
        """
            returns:
                1 if there is lava (with award)
                2 if there is a barrier or out of bound (cannot move)
                3 if there was a box that is being moved now so it is empty (chain move)
                4 if it was empty (invalid move)
        """
        
        i, j = position[0], position[1]

        if self.map[i][j] == Objects.Lava.value:
            return 1
        
        if self.map[i][j] == Objects.Barrier or self._out_of_bound(i,j):
            return 2

        # if there is no box...
        if 1 > self.map[i][j] or self.map[i][j] > 10:
            return 4

        new_position = position + Move_to_delta.get(action)
        new_position_status = self._apply_move_action(new_position, action)

        if new_position_status == 1: # if there is lava ahead
            self.stamina -= settings.EnvironmentVars.unit_force
            
            # Box is pused into the lava, so its position would be empty and agent gains stamina  
            self.map[i][j] = Objects.Empty.value
            self.stamina += settings.EnvironmentVars.initial_force

            return 3 # the box is pushed into the lava, so now its position is empty 
        
        elif new_position_status == 3: # if the position ahead is now empty
            self.stamina -= settings.EnvironmentVars.unit_force

            new_i, new_j = new_position

            the_box = self.map[i][j]
            
            self.map[i][j] = Objects.Empty.value
            self.map[new_i][new_j] = the_box

            return 3 # the box is pushed ahead, so now its position is empty 
        
        else: # if we cannot move shit :|
            return 2
            

    def reset(self, *, seed=None):
        super().reset(seed=seed)
        
        self._load_map()
        self.terminated = False
        self.truncated = False

        return self._get_obs(), {}
    
    def _check_termination(self):
        if self.stamina <= 0:
            return True
        
        if self.timestep >= settings.EnvironmentVars.max_timestep:
            return True

        # TODO: if there is no box left, the episode is terminated

        return False
    
    def _out_of_bound(self, i, j):
        if i < 0 or i >= self.n_rows or j < 0 or j >= self.n_cols:
            return True
        return False 

    def _load_map(self, map_name=None):
        load_map = False
        if map_name:
            map_files = os.listdir(self.map_path)
            if map_name in map_files:
                load_map = True

        if load_map:
            file_path = self.map_path / map_name
            self._read_map_from_file(file_path)
            
        else:
            self._generate_random_map()

    def _read_map_from_file(self, file_path):
        with open(file_path, 'r') as file:
            lines = file.readlines()

        lines = [i.split() for i in lines]

        self.n_rows = len(lines)
        self.n_cols = len(lines[0])
        
        grid = np.zeros((self.n_rows, self.n_cols), dtype=int)

        for i in range(self.n_rows):
            for j in range(self.n_cols):
                grid[i][j] = int(lines[i][j])

        self.map = grid

    def _generate_random_map(self):
        total = self.n_rows * self.n_cols

        grid = np.zeros((self.n_rows, self.n_cols), dtype=int)

        indices = np.random.choice(total, self.number_of_barriers + self.number_of_boxes + self.number_of_lavas, replace=False)
        barriers_idx = indices[:self.number_of_barriers]
        boxes_idx = indices[self.number_of_barriers:self.number_of_barriers + self.number_of_boxes]
        lavas_idx = indices[self.number_of_barriers + self.number_of_boxes:]

        flat = grid.ravel()
        flat[barriers_idx] = Objects.Barrier.value
        flat[boxes_idx] = Objects.Box1.value
        flat[lavas_idx] = Objects.Lava.value

        self.map = grid

    def _get_obs(self):
        obs = {
            "grid": self.map,
            "agent": None,
            "stamina": self.stamina,
            "previous_selected_position": None,
            "previous_action": None,
        }

        return obs

if __name__ == "__main__":
    env = ShoverWorldEnv("human")
    env._load_map("map1.txt")
    print(env.stamina)
    env.step({"position": np.array([1,2]), "z":Actions.MoveUp.value})
    env.step({"position": np.array([1,2]), "z":Actions.MoveUp.value})
    print(env.stamina)
    print(env.map)