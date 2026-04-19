import pygame # type: ignore
from config import *

class Console:
    def __init__(self, x: int, y: int, width: int, height: int):
        self.rect = pygame.Rect(x, y, width, height)
        self.font = pygame.font.SysFont("Consolas", 14)
        
    def draw(self, surface: pygame.Surface, logs: list):
        pygame.draw.rect(surface, (15, 23, 42, 150), self.rect, border_radius=8)
        pygame.draw.rect(surface, COLOR_GRID, self.rect, width=1, border_radius=8)
        
        title = self.font.render("CONSOLE LOGS", True, COLOR_ACCENT)
        surface.blit(title, (self.rect.x + 10, self.rect.y + 5))
        
        for i, log in enumerate(logs[-12:]): # Show last 12 logs
            color = COLOR_TEXT
            if "ERROR" in log: color = (239, 68, 68)
            elif "---" in log: color = COLOR_ACCENT
            
            log_surf = self.font.render(f"> {log}", True, color)
            surface.blit(log_surf, (self.rect.x + 10, self.rect.y + 30 + i * 18))

class RunButton:
    def __init__(self, x: int, y: int, width: int, height: int):
        self.rect = pygame.Rect(x, y, width, height)
        self.font = pygame.font.SysFont("Arial", 20, bold=True)
        self.color = COLOR_SUCCESS
        
    def draw(self, surface: pygame.Surface):
        mouse_pos = pygame.mouse.get_pos()
        color = self.color
        if self.rect.collidepoint(mouse_pos):
            color = (min(color[0]+20, 255), min(color[1]+20, 255), min(color[2]+20, 255))
            
        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        text = self.font.render("EXECUTAR SCRIPT (F5)", True, COLOR_TEXT)
        text_rect = text.get_rect(center=self.rect.center)
        surface.blit(text, text_rect)
        
    def is_clicked(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                return True
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F5:
                return True
        return False
        
class StopButton:
    def __init__(self, x: int, y: int, width: int, height: int):
        self.rect = pygame.Rect(x, y, width, height)
        self.font = pygame.font.SysFont("Arial", 20, bold=True)
        self.color = COLOR_DANGER
        
    def draw(self, surface: pygame.Surface):
        mouse_pos = pygame.mouse.get_pos()
        color = self.color
        if self.rect.collidepoint(mouse_pos):
            color = (min(color[0]+20, 255), min(color[1]+20, 255), min(color[2]+20, 255))
            
        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        text = self.font.render("PARAR", True, COLOR_TEXT)
        text_rect = text.get_rect(center=self.rect.center)
        surface.blit(text, text_rect)
        
    def is_clicked(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                return True
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F6: # Stop shortcut
                return True
        return False
