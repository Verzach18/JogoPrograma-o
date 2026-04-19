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

    def draw(self, surface, screen_pos):
        rect = pygame.Rect(screen_pos[0], screen_pos[1], TILE_SIZE, TILE_SIZE)
        
        # Draw Base Tile
        color = COLOR_GRID
        if self.tilled:
            color = (60, 45, 35) # Dark rich brown
        
        pygame.draw.rect(surface, color, rect, border_radius=2)
        pygame.draw.rect(surface, (40, 45, 65), rect, 1, border_radius=2) # Subtle Border
        
        # Draw Entity
        if self.entity == Entities.GRASS:
            # Color intensity based on growth
            g_color = (34, int(100 + self.growth * 100), 34)
            inner_rect = rect.inflate(-10 * (1.0 - self.growth), -10 * (1.0 - self.growth))
            pygame.draw.rect(surface, g_color, inner_rect, border_radius=4)
        elif self.entity == Entities.TREE:
            pygame.draw.rect(surface, (139, 69, 19), rect.inflate(-20, -10))
            if self.growth > 0.5:
                pygame.draw.circle(surface, (0, 100, 0), rect.center, int(15 * self.growth))
        elif self.entity == Entities.MINERAL_NODE:
            pygame.draw.circle(surface, (80, 85, 100), rect.center, 14)
            pygame.draw.circle(surface, (140, 150, 180), rect.center, 8)
            pygame.draw.circle(surface, (200, 220, 255), rect.center, 3) # Highlight
        elif self.entity == Entities.MINER:
            # Pulsing miner
            pulse = (math.sin(time.time() * 10) + 1) / 2
            pygame.draw.rect(surface, (60, 60, 70), rect.inflate(-10, -10), border_radius=6)
            pygame.draw.rect(surface, (255, 200, 0), rect.inflate(-25, -25), border_radius=2)
            if pulse > 0.5:
                pygame.draw.rect(surface, (255, 255, 100), rect.inflate(-20, -20), 2, border_radius=4)
        elif self.entity == Entities.ATMOSPHERE_GEN:
            pulse = (math.sin(time.time() * 3) + 1) / 2
            pygame.draw.rect(surface, (30, 80, 150), rect.inflate(-10, -10), border_radius=10)
            glow_c = (100, 200, 255, int(50 + 50 * pulse))
            pygame.draw.circle(surface, glow_c, rect.center, int(10 + 5 * pulse))
        elif self.entity == Entities.HEATER:
            pulse = (math.sin(time.time() * 6) + 1) / 2
            pygame.draw.rect(surface, (150, 40, 30), rect.inflate(-10, -10), border_radius=4)
            core_c = (255, 100 + 100 * pulse, 50)
            pygame.draw.rect(surface, core_c, rect.inflate(-22, -22), border_radius=2)

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

    def draw(self, surface, camera_offset):
        for x in range(self.grid_size):
            for y in range(self.grid_size):
                pos = (x * TILE_SIZE + camera_offset[0], y * TILE_SIZE + camera_offset[1])
                self.grid[x][y].draw(surface, pos)
