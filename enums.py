from enum import Enum
import numpy as np

class Objects(Enum):
    Lava = -100
    Empty = 0
    Box1 = 1
    Box2 = 2
    Box3 = 3
    Box4 = 4
    Box5 = 5
    Box6 = 6
    Box7 = 7
    Box8 = 8
    Box9 = 9
    Box10 = 10
    Barrier = 100

class Actions(Enum):
    MoveUp = 1
    MoveRight = 2
    MoveDown = 3
    MoveLeft = 4
    BarrierMaker = 5
    Hellify = 6

Move_to_delta = {
    Actions.MoveUp.value: np.array([-1, 0]),
    Actions.MoveRight.value: np.array([0, 1]),
    Actions.MoveDown.value: np.array([1, 0]),
    Actions.MoveLeft.value: np.array([0, -1]),
}

def is_box(value):
    if 1 <= value <= 10:
        return True
    return False

def is_empty(value):
    if value == 0:
        return True
    return False

def is_perfect_square(map, start, extend):
    start_i, start_j = start
    
    for i in range(extend):
        if not is_empty(map[start_i + i][start_j]):
            return False
        if not is_empty(map[start_i + i][start_j + extend - 1]):
            return False
        
    
    for j in range(extend):
        if not is_empty(map[start_i][start_j+j]):
            return False
        if not is_empty(map[start_i+extend - 1][start_j+j]):
            return False
    
    for i in range(1,extend-1):
        for j in range(1,extend-1):
            if not is_box(map[start_i+i][start_j+j]):
                return False
    
    return True