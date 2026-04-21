import pygame # type: ignore
import random
import math
import time
from config import *

class Tile:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.tilled = False
        self.entity = Entities.NONE
        self.growth = 0.0 # 0.0 to 1.0
        self.growth_speed = 0.001
        
    def update(self):
        if self.entity != Entities.NONE and self.growth < 1.0:
            if self.entity in [Entities.GRASS, Entities.TREE]:
                self.growth += self.growth_speed
                if self.growth > 1.0: self.growth = 1.0

    def draw(self, surface, screen_pos, engine=None):
        rect = pygame.Rect(screen_pos[0], screen_pos[1], TILE_SIZE, TILE_SIZE)
        
        # Draw Base Tile
        color = COLOR_GRID
        if engine:
            # Shift grid color towards "Earthly" green/brown as O2/Temp rise
            o2_factor = min(1.0, engine.oxygen / 100.0)
            t_factor = min(1.0, (engine.temperature + 50) / 100.0)
            base_r = int(25 + 10 * t_factor)
            base_g = int(28 + 30 * o2_factor)
            base_b = int(45 - 20 * o2_factor)
            color = (base_r, base_g, base_b)

        if self.tilled:
            color = (65, 50, 40) # Slightly lighter brown
            pygame.draw.rect(surface, color, rect, border_radius=4)
            # Add some "tilled" lines
            for i in range(2, TILE_SIZE, 8):
                pygame.draw.line(surface, (50, 35, 25), (screen_pos[0] + i, screen_pos[1] + 2), 
                                 (screen_pos[0] + i, screen_pos[1] + TILE_SIZE - 2), 1)
        else:
            pygame.draw.rect(surface, color, rect, border_radius=4)
            # Add subtle tech pattern to grid
            pygame.draw.rect(surface, (35, 40, 60), rect.inflate(-TILE_SIZE//2, -TILE_SIZE//2), 1)

        pygame.draw.rect(surface, (45, 50, 75), rect, 1, border_radius=4) # Subtle Border
        
        # Draw Entity
        sprite = None
        if self.entity == Entities.GRASS:
            sprite = Assets.get("grass", int(TILE_SIZE * self.growth))
        elif self.entity == Entities.TREE:
            sprite = Assets.get("tree", int(TILE_SIZE * (0.5 + 0.5 * self.growth)))
        elif self.entity == Entities.MINERAL_NODE:
            # We don't have mineral sprite yet, so improved procedural
            pygame.draw.circle(surface, (100, 110, 130), rect.center, 16)
            pulse = (math.sin(time.time() * 5) + 1) / 2
            pygame.draw.circle(surface, (0, 150, 255), rect.center, int(6 + 2 * pulse))
            pygame.draw.circle(surface, (200, 240, 255), rect.center, 3)
        elif self.entity == Entities.MINER:
            sprite = Assets.get("miner", TILE_SIZE - 4)
        elif self.entity == Entities.ATMOSPHERE_GEN:
            sprite = Assets.get("atmo_gen", TILE_SIZE - 4)
        elif self.entity == Entities.HEATER:
            sprite = Assets.get("heater", TILE_SIZE - 4)
        elif self.entity == Entities.SOLAR_PANEL:
            # Procedural Solar Panel (Blue grid with metallic frame)
            pygame.draw.rect(surface, (40, 40, 50), rect.inflate(-4, -4), border_radius=4)
            inner = rect.inflate(-10, -10)
            pygame.draw.rect(surface, (20, 50, 120), inner, border_radius=2)
            # Grid lines
            for x in range(inner.x, inner.right, 6):
                pygame.draw.line(surface, (60, 100, 200), (x, inner.y), (x, inner.bottom), 1)
            for y in range(inner.y, inner.bottom, 6):
                pygame.draw.line(surface, (60, 100, 200), (inner.x, y), (inner.right, y), 1)

        if sprite:
            sprite.set_colorkey((255, 255, 255))
            s_rect = sprite.get_rect(center=rect.center)
            surface.blit(sprite, s_rect)

class World:
    def __init__(self):
        self.grid_size = INITIAL_GRID_SIZE
        self.grid = [[Tile(x, y) for y in range(self.grid_size)] for x in range(self.grid_size)]
        self._spawn_minerals()
        
    def _spawn_minerals(self):
        for _ in range(5):
            x, y = random.randint(0, self.grid_size-1), random.randint(0, self.grid_size-1)
            self.grid[x][y].entity = Entities.MINERAL_NODE

    def update(self, engine):
        drone = engine.drone
        for row in self.grid:
            for tile in row:
                tile.update()
                if tile.entity == Entities.MINER:
                    if random.random() < 0.01:
                        drone.resources["Minerals"] += 1
                elif tile.entity == Entities.ATMOSPHERE_GEN:
                    if drone.resources["Biomass"] > 0:
                        drone.resources["Biomass"] -= 0.01 # Consume biomass
                        engine.oxygen += 0.005 # Increase O2
                elif tile.entity == Entities.HEATER:
                    if drone.resources["Minerals"] > 0:
                        drone.resources["Minerals"] -= 0.01
                        engine.temperature += 0.005
                
    def get_tile(self, x, y):
        if 0 <= x < self.grid_size and 0 <= y < self.grid_size:
            return self.grid[x][y]
        return None

    def draw(self, surface, camera_offset, engine=None):
        for x in range(self.grid_size):
            for y in range(self.grid_size):
                pos = (x * TILE_SIZE + camera_offset[0], y * TILE_SIZE + camera_offset[1])
                self.grid[x][y].draw(surface, pos, engine)
