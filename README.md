# Shover-World — Milestone 1  
A custom Gym-compatible environment for a grid-based reinforcement-learning game.

## Overview

This project implements the environment required for **Milestone 1** of the *AI 2025 – Shover-World* assignment.  
Shover-World is a Sokoban-inspired grid world featuring:

- Box-pushing mechanics  
- Stamina-based action costs  
- Lava interactions and refunds  
- Detection of perfect squares  
- Two special actions (**Barrier Maker**, **Hellify**)  
- Directional movement with chain pushing  
- Integer-encoded map loading  
- Optional Pygame GUI

The environment follows the Gym API and exposes a `ShoverWorldEnv` class with `reset()` and `step()`.

## Project Structure

```text
.
├── enums.py
├── environment.py # Main Gym environment (ShoverWorldEnv)
├── gui.py # Pygame visualizer / controller
├── maps/
│ ├── map1.txt
│ └── map2.txt
├── PerfectSquare.py # Perfect-square detection utilities
├── settings.py # Configuration parameters
└── README.md
```

---

## Installation

### Requirements

This project depends on:

- `gym`
- `pygame`
- `numpy`

Install all dependencies:

```bash
pip install -r requirements.txt
```

## How to Run

### Run the Environment (Headless)

```bash
python3 environment.py
```
Runs a simple loop using random actions without rendering.

### Run the GUI

```bash
python3 gui.py
```
Launches an interactive Pygame GUI.

### Controls (GUI)
| Input               | Action                              |
| ------------------- | ----------------------------------- |
| **Click on a cell** | Selects the (x, y) target position  |
| **Arrow keys**      | Move the agent (Up/Right/Down/Left) |
| **B**               | Barrier Maker                       |
| **H**               | Hellify                             |

Special actions apply to the oldest detected perfect square.

## Environment API

### Class

```python
ShoverWorldEnv(render_mode=None, ...)
```
Defined in environment.py.

### Action Space

Actions are tuples of the form:
```text
(x, y, z)
```
Where:
- (x, y) is the selected target cell
- z is the action ID:

| z | Meaning       |
| - | ------------- |
| 1 | Move Up       |
| 2 | Move Right    |
| 3 | Move Down     |
| 4 | Move Left     |
| 5 | Barrier Maker |
| 6 | Hellify       |

Invalid actions result in no movement.

### Observation Space

The observation is a dictionary containing:

- Integer grid
- Agent position
- Stamina
- Previous action
- Previously selected position

### Map Format

This project supports integer grid maps only.

| Value | Meaning |
| ----- | ------- |
| -100  | Lava    |
| 0     | Empty   |
| 10    | Box     |
| 100   | Barrier |

## GUI Details

The GUI implemented in gui.py:

- Draws the grid, agent, lava, boxes, and barriers
- Shows stamina and timestep
- Lets the user select a target cell with the mouse
- Uses keyboard for movement and special actions

