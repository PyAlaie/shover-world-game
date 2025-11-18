import gymnasium as gym
from gymnasium import spaces
import numpy as np
import os
from enums import Objects, Actions, Move_to_delta
import settings
from PerfectSquare import PerfectSquare

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

        self.perfect_squares = []

        self.action_space = spaces.Dict({
            "position": spaces.MultiDiscrete([self.n_rows, self.n_cols]),
            "z": spaces.Discrete(len(Actions))
        })
        self.observation_space = spaces.Box(low=-100, high=100, shape=(self.n_rows,self.n_cols), dtype=np.int32)

    def step(self, action):
        position = action["position"]
        z = action["z"]

        if z == Actions.BarrierMaker.value:
            self._apply_barrier_maker_action()
        
        elif z == Actions.Hellify.value:
            self._apply_hellify_action()
            pass

        else: # Action of moving, costs 4 staminas anyway (even if nothing happens)
            res = self._apply_move_action(position, z)

            i, j = position[0], position[1]
            
            if res == 3: # the head box was moved
                if self.moving_positions.get((i,j)) != action:
                    self.stamina -= settings.EnvironmentVars.initial_force
                
                new_position = position + Move_to_delta.get(z)
                self.moving_positions = {(new_position[0], new_position[1]): action}

                for sq in self.perfect_squares:
                    if sq.includes(position):
                        self.perfect_squares.remove(sq)
                        break
            
            else:
                self.moving_positions = {}


        # increase the age of all perfect squares
        for perfect_square in self.perfect_squares:
            perfect_square.increase_age()

        # find new perfect squres
        new_perf_sqs = PerfectSquare.find_new_perfect_squares(self.map, self.perfect_squares)
        self.perfect_squares.extend(new_perf_sqs)

        # Automatic Dissolution of Perfect Squares
        perf_sq_indexs_to_dissolute = []
        for i, perfect_square in enumerate(self.perfect_squares):
            if perfect_square.exeeded_max_age(self.perf_sq_initial_age):
                perf_sq_indexs_to_dissolute.append(i)
                
        for sq_index in reversed(perf_sq_indexs_to_dissolute):
            sq = self.perfect_squares[sq_index]
            self.map = sq.dissolute(self.map)
            del self.perfect_squares[sq_index]
        
        self.timestep += 1

        if self._check_termination():
            self.terminated = True

    def _apply_barrier_maker_action(self):
        sorted_perf_sqs = list(reversed(sorted(self.perfect_squares, key=lambda x:x.age)))
        if len(sorted_perf_sqs) == 0:
            return 
        
        sq = sorted_perf_sqs[0]
        self.map = sq.apply_barrier_maker(self.map)
        self.perfect_squares.remove(sq)
        self.stamina += (sq.extend - 2)**2

    def _apply_move_action(self, position, action):
        """
            returns:
                1 if there is lava (with award)
                2 if there is a barrier or out of bound (cannot move)
                3 if there was a box that is being moved now so it is empty (chain move)
                4 if it was empty (invalid move)
        """
        
        i, j = position[0], position[1]
        if self._out_of_bound(i,j) or self.map[i][j] == Objects.Barrier:
            return 2
        
        if self.map[i][j] == Objects.Lava.value:
            return 1

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
        
        elif new_position_status == 3 or new_position_status == 4: # if the position ahead is now empty
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
        
        self._load_map(self.map_name)
        self.terminated = False
        self.truncated = False

        self.perfect_squares = PerfectSquare.find_new_perfect_squares(self.map, [])

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
    env = ShoverWorldEnv("human", map_name="map2.txt")
    # env._load_map("map2.txt")
    env.reset()
    print(env.perfect_squares)
    # print(env.stamina)
    # env.step({"position": np.array([1,3]), "z":Actions.MoveUp.value})
    # env.step({"position": np.array([1,2]), "z":Actions.MoveUp.value})
    # print(env.stamina)
    # print(env.map)
    # a = PerfectSquare.find_new_perfect_squares(env.map, [])
    # print(a)