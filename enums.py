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