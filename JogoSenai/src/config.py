import pygame # type: ignore
from enum import Enum

# Screen Settings
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
FULLSCREEN = True 

class WindowMode(Enum):
    WINDOWED = 0
    FULLSCREEN = 1
    BORDERLESS = 2

# Game States
class GameState(Enum):
    MENU = 0
    PLAYING = 1
    PAUSED = 2
    SETTINGS = 3
    GAMEOVER = 4

# Available Resolutions
RESOLUTIONS = [
    (1280, 720),
    (1366, 768),
    (1600, 900),
    (1920, 1080)
]

# Tile Settings
TILE_SIZE = 48
INITIAL_GRID_SIZE = 10

# Colors (Cyberpunk / Space Theme)
COLOR_BG = (10, 12, 20)
COLOR_GRID = (25, 28, 45)
COLOR_TEXT = (230, 235, 255)
COLOR_ACCENT = (0, 190, 255)      # Cyan Neon
COLOR_SECONDARY = (255, 0, 150)   # Magenta Neon
COLOR_SUCCESS = (0, 255, 150)     # Emerald
COLOR_WARN = (255, 200, 0)
COLOR_DANGER = (255, 50, 80)
COLOR_UI_BG = (20, 22, 35, 200)   # Semi-transparent

# Entity Types
class Entities(Enum):
    NONE = 0
    GRASS = 1
    TREE = 2
    MINER = 3
    ATMOSPHERE_GEN = 4
    MINERAL_NODE = 5
    HEATER = 6

# Directions
class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    RIGHT = (1, 0)
    LEFT = (-1, 0)

# Progression Costs (in Biomass/Oxygen)
COSTS = {
    "loops": 50,
    "if_statements": 150,
    "functions": 500,
    "speed_upgrade": 100,
    "grid_expand": 300,
    "miner_unlock": 250,
    "miner_build": 100, # Cost in Minerals
    "atmo_gen_unlock": 500,
    "atmo_gen_build": 300, # Cost in Biomass
    "heater_unlock": 1000,
    "heater_build": 500, # Cost in Minerals
}

# Terraforming Goals
GOAL_O2 = 100.0
GOAL_TEMP = 100.0

# Drone Constants
INITIAL_SPEED = 0.5 # Seconds per action
