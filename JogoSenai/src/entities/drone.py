import pygame # type: ignore
import math
import queue
import threading
import time
from config import *

class Drone:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.resources = {"Biomass": 0, "Minerals": 0}
        self.command_queue = queue.Queue()
        self.completion_event = threading.Event()
        self.flip_angle = 0
        self.is_flipping = False
        self.logs = []
        self._stop_flag = False
        self.progression = None # Injected by executor

    def reset_sync(self):
        self._stop_flag = False
        self.completion_event.clear()
        while not self.command_queue.empty():
            try: self.command_queue.get_nowait()
            except: break

    def stop(self):
        self._stop_flag = True
        self.completion_event.set() # Wake up any waiting script

    def _wait_for_action(self):
        if self._stop_flag: return
        self.completion_event.wait()
        self.completion_event.clear()

    def log(self, msg):
        self.logs.append(str(msg))
        if len(self.logs) > 10: self.logs.pop(0)

    # Programming Interface (Farmer Was Replaced style)
    def move(self, direction):
        self.command_queue.put(("move", direction))
        self._wait_for_action()
        
    def till(self):
        self.command_queue.put(("till", None))
        self._wait_for_action()
        
    def plant(self, entity_type):
        self.command_queue.put(("plant", entity_type))
        self._wait_for_action()
        
    def harvest(self):
        self.command_queue.put(("harvest", None))
        self._wait_for_action()
        
    def build_miner(self):
        self.command_queue.put(("build_miner", None))
        self._wait_for_action()

    def build_atmo_gen(self):
        self.command_queue.put(("build_atmo_gen", None))
        self._wait_for_action()

    def build_heater(self):
        self.command_queue.put(("build_heater", None))
        self._wait_for_action()

    # Sensors (Immediate return, no wait)
    def get_pos(self):
        return (self.x, self.y)
        
    def get_resources(self):
        return self.resources.copy()

    def can_harvest(self) -> bool:
        # Note: In a real simulation, sensors need immediate state.
        # For simplicity in this base, we check current state at execution time.
        # But during script parsing, we'll return a proxy.
        return True 

    def do_a_flip(self):
        self.command_queue.put(("flip", None))
        self._wait_for_action()

    # Execution Logic
    def execute_step(self, world):
        if self.command_queue.empty(): return
        
        action, params = self.command_queue.get()
        tile = world.get_tile(self.x, self.y)
        
        if action == "move":
            dx, dy = params.value if isinstance(params, Direction) else (0,0)
            if 0 <= self.x + dx < world.grid_size and 0 <= self.y + dy < world.grid_size:
                self.x += dx
                self.y += dy
        elif action == "till":
            if tile: tile.tilled = True
        elif action == "plant":
            if tile and tile.tilled and tile.entity == Entities.NONE:
                tile.entity = params
                tile.growth = 0.0
        elif action == "harvest":
            if tile and tile.entity != Entities.NONE and tile.growth >= 1.0:
                self.resources["Biomass"] += 10
                tile.entity = Entities.NONE
                tile.growth = 0.0
                self.log("LOG::RECURSO_COLETADO >> +10 Biomassa")
        elif action == "build_miner":
            cost = COSTS.get("miner_build", 100)
            if self.progression and not self.progression.can_use("miner_unlock"):
                self.log("ERROR: Miner Tech not unlocked!")
            elif tile and tile.entity == Entities.MINERAL_NODE:
                if self.resources["Minerals"] >= cost:
                    self.resources["Minerals"] -= cost
                    tile.entity = Entities.MINER
                    self.log("Built Miner!")
                else:
                    self.log(f"ERROR: Need {cost} Minerals")
            else:
                self.log("ERROR: Must be on Mineral Node")
        elif action == "build_atmo_gen":
            cost = COSTS.get("atmo_gen_build", 300)
            if self.progression and not self.progression.can_use("atmo_gen_unlock"):
                self.log("ERROR: Atmo Gen Tech not unlocked!")
            elif tile and tile.entity == Entities.NONE:
                if self.resources["Biomass"] >= cost:
                    self.resources["Biomass"] -= cost
                    tile.entity = Entities.ATMOSPHERE_GEN
                    self.log("Built Atmosphere Generator!")
                else:
                    self.log(f"ERROR: Need {cost} Biomass")
            else:
                self.log("ERROR: Tile must be empty")
        elif action == "build_heater":
            cost = COSTS.get("heater_build", 500)
            if self.progression and not self.progression.can_use("heater_unlock"):
                self.log("ERROR: Heater Tech not unlocked!")
            elif tile and tile.entity == Entities.NONE:
                if self.resources["Minerals"] >= cost:
                    self.resources["Minerals"] -= cost
                    tile.entity = Entities.HEATER
                    self.log("Built Geothermal Heater!")
                else:
                    self.log(f"ERROR: Need {cost} Minerals")
            else:
                self.log("ERROR: Tile must be empty")
        elif action == "flip":
            self.is_flipping = True
            self.flip_angle = 0
        
        self.completion_event.set()
        return action

    def update(self):
        if self.is_flipping:
            self.flip_angle += 10
            if self.flip_angle >= 360:
                self.is_flipping = False
                self.flip_angle = 0

    def draw(self, surface, camera_offset):
        # Hovering Animation (Sine wave)
        bobbing = math.sin(time.time() * 5) * 5
        
        pos_x = self.x * TILE_SIZE + camera_offset[0] + TILE_SIZE // 2
        pos_y = self.y * TILE_SIZE + camera_offset[1] + TILE_SIZE // 2 + bobbing
        
        # 1. Draw Glow Aura (Transparent Surface)
        glow_size = 60
        glow_surf = pygame.Surface((glow_size, glow_size), pygame.SRCALPHA)
        for r in range(glow_size // 2, 0, -2):
            alpha = int(100 * (1.0 - r / (glow_size // 2)))
            pygame.draw.circle(glow_surf, (*COLOR_ACCENT, alpha), (glow_size // 2, glow_size // 2), r)
        surface.blit(glow_surf, (pos_x - glow_size // 2, pos_y - glow_size // 2))

        # 2. Draw Drone (Futuristic Diamond)
        drone_surf = pygame.Surface((34, 34), pygame.SRCALPHA)
        # Base Body
        pygame.draw.polygon(drone_surf, (40, 50, 80), [(17, 0), (34, 17), (17, 34), (0, 17)])
        # Inner Core (Glowing)
        pygame.draw.polygon(drone_surf, COLOR_ACCENT, [(17, 6), (28, 17), (17, 28), (6, 17)])
        # Detail Lines
        pygame.draw.polygon(drone_surf, (200, 230, 255), [(17, 0), (34, 17), (17, 34), (0, 17)], 2)
        
        rotated_drone = pygame.transform.rotate(drone_surf, self.flip_angle)
        rect = rotated_drone.get_rect(center=(pos_x, pos_y))
        surface.blit(rotated_drone, rect)
