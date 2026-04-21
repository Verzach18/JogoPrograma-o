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
        self.energy = MAX_ENERGY
        self.max_energy = MAX_ENERGY
        self.current_line = -1

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

    def build_solar_panel(self):
        self.command_queue.put(("build_solar_panel", None))
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

    # Advanced Software Modules (Feature 4)
    def move_to(self, x, y):
        if self.progression and not self.progression.can_use("navigation_unlock"):
            self.log("ERROR: Navigation Module not researched!")
            return
            
        self.log(f"CMD::NAVIGATING_TO >> ({x}, {y})")
        while self.x != x or self.y != y:
            dx = 1 if x > self.x else -1 if x < self.x else 0
            dy = 1 if y > self.y else -1 if y < self.y else 0
            
            # Simple Manhattan movement
            if dx != 0:
                self.move(Direction.RIGHT if dx > 0 else Direction.LEFT)
            elif dy != 0:
                self.move(Direction.DOWN if dy > 0 else Direction.UP)
            
            if self._stop_flag: break

    def inspect(self):
        if self.progression and not self.progression.can_use("inspector_unlock"):
            self.log("ERROR: Inspector Module not researched!")
            return None
            
        self.command_queue.put(("inspect", None))
        return self._wait_for_result()

    def _wait_for_result(self):
        # For now, let's assume result is put into a special buffer by execute_step
        self._wait_for_action()
        return getattr(self, "_last_result", None)

    # Execution Logic
    def execute_step(self, world):
        if self.command_queue.empty(): return
        
        action, params = self.command_queue.get()
        tile = world.get_tile(self.x, self.y)
        
        if action == "move":
            if self.energy < MOVE_COST:
                self.log("ERROR: Low Energy!")
            else:
                dx, dy = params.value if isinstance(params, Direction) else (0,0)
                if 0 <= self.x + dx < world.grid_size and 0 <= self.y + dy < world.grid_size:
                    self.x += dx
                    self.y += dy
                    self.energy -= MOVE_COST
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
        elif action == "build_solar_panel":
            cost = 150 # Biomass or Minerals? Let's say Minerals
            if self.resources["Minerals"] >= cost:
                if tile and tile.entity == Entities.NONE:
                    self.resources["Minerals"] -= cost
                    tile.entity = Entities.SOLAR_PANEL
                    self.log("Built Solar Panel!")
                else: self.log("ERROR: Tile must be empty")
            else: self.log(f"ERROR: Need {cost} Minerals")
        elif action == "flip":
            self.is_flipping = True
            self.flip_angle = 0
        elif action == "inspect":
            self._last_result = {
                "x": self.x,
                "y": self.y,
                "tile": tile.entity.name if tile else "NONE",
                "tilled": tile.tilled if tile else False,
                "growth": tile.growth if tile else 0
            }
        
        # Energy Check (Charging from solar panels nearby)
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                check_tile = world.get_tile(self.x + dx, self.y + dy)
                if check_tile and check_tile.entity == Entities.SOLAR_PANEL:
                    self.energy = min(self.max_energy, self.energy + SOLAR_GEN * 10) # Fast charge
        
        # Base recharge at origin
        if self.x == 0 and self.y == 0:
            self.energy = min(self.max_energy, self.energy + 2.0)

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
        glow_size = 70
        glow_surf = pygame.Surface((glow_size, glow_size), pygame.SRCALPHA)
        pulse = (math.sin(time.time() * 10) + 1) / 2
        for r in range(glow_size // 2, 0, -2):
            alpha = int((80 + 40 * pulse) * (1.0 - r / (glow_size // 2)))
            pygame.draw.circle(glow_surf, (*COLOR_ACCENT, alpha), (glow_size // 2, glow_size // 2), r)
        surface.blit(glow_surf, (pos_x - glow_size // 2, pos_y - glow_size // 2))

        # 2. Draw Drone Sprite
        sprite = Assets.get("drone", 40)
        # Handle transparency for generated images with white bg
        sprite.set_colorkey((255, 255, 255))
        
        rotated_drone = pygame.transform.rotate(sprite, self.flip_angle)
        rect = rotated_drone.get_rect(center=(pos_x, pos_y))
        surface.blit(rotated_drone, rect)
