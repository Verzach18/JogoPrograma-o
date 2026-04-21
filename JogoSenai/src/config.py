import pygame # type: ignore
from enum import Enum

# Screen Settings
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
FULLSCREEN = False 

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
    SOLAR_PANEL = 7

# Directions
class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    RIGHT = (1, 0)
    LEFT = (-1, 0)

# Energy Settings
MAX_ENERGY = 100.0
MOVE_COST = 0.5
ACTION_COST = 1.0
SOLAR_GEN = 0.2

# Sky Colors (Blending)
COLOR_SPACE = (10, 12, 20)
COLOR_SKY_LOW = (30, 45, 80)
COLOR_SKY_FULL = (100, 180, 255)

# Progression Costs (in Biomass/Oxygen)
COSTS = {
    # Software
    "if_statements": 100,
    "loops": 250,
    "functions": 500,
    "navigation_unlock": 150,
    "inspector_unlock": 200,
    
    # Hardware
    "speed_upgrade_1": 100,
    "speed_upgrade_2": 300,
    "battery_1": 150,
    "battery_2": 400,
    
    # Planet
    "miner_unlock": 250,
    "miner_build": 100,
    "atmo_gen_unlock": 400,
    "atmo_gen_build": 300,
    "heater_unlock": 800,
    "heater_build": 500,
}

# Research Dependencies (id -> list of required ids)
RESEARCH_TREE = {
    "loops": ["if_statements"],
    "functions": ["loops"],
    "speed_upgrade_2": ["speed_upgrade_1"],
    "battery_2": ["battery_1"],
}

# Terraforming Goals
GOAL_O2 = 100.0
GOAL_TEMP = 100.0

# Drone Constants
INITIAL_SPEED = 0.5 # Seconds per action

# Asset Management
import os
ASSETS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets")

def load_image(name, size=None):
    path = os.path.join(ASSETS_DIR, f"{name}.png")
    try:
        img = pygame.image.load(path).convert_alpha()
        # Remove white background (common for generated images)
        # Note: convert_alpha is usually better, but if the image has a solid white bg:
        # img.set_colorkey((255, 255, 255))
        if size:
            img = pygame.transform.scale(img, (size, size))
        return img
    except:
        # Fallback to a colored surface if image not found
        surf = pygame.Surface((size or TILE_SIZE, size or TILE_SIZE), pygame.SRCALPHA)
        pygame.draw.rect(surf, COLOR_ACCENT, surf.get_rect(), border_radius=5)
        return surf

class Assets:
    _cache = {}

    @classmethod
    def get(cls, name, size=None):
        key = (name, size)
        if key not in cls._cache:
            cls._cache[key] = load_image(name, size)
        return cls._cache[key]
