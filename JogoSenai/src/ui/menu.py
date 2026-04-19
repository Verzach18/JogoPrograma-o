import pygame # type: ignore
from config import *
import math
import time

class Button:
    def __init__(self, x, y, w, h, text, color=COLOR_ACCENT):
        # x, y will be treated as offsets if we use dynamic centering
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.color = color
        self.font = pygame.font.SysFont("Arial", 20, bold=True)
        self.hovered = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.hovered and event.button == 1:
                return True
        return False

    def draw(self, surface):
        c = list(self.color)
        if self.hovered:
            c = [min(v + 30, 255) for v in c]
        
        pygame.draw.rect(surface, c, self.rect, border_radius=8)
        pygame.draw.rect(surface, COLOR_TEXT, self.rect, 2, border_radius=8)
        
        txt = self.font.render(self.text, True, COLOR_TEXT)
        surface.blit(txt, txt.get_rect(center=self.rect.center))

class MainMenu:
    def __init__(self):
        self.title_font = pygame.font.SysFont("Verdana", 64, bold=True)
        self.buttons = [
            Button(0, 300, 300, 50, "INICIAR JOGO", COLOR_SUCCESS),
            Button(0, 370, 300, 50, "CONFIGURAÇÕES", COLOR_ACCENT),
            Button(0, 440, 300, 50, "SAIR", COLOR_DANGER)
        ]

    def handle_event(self, event):
        for i, btn in enumerate(self.buttons):
            if btn.handle_event(event):
                return i 
        return None

    def draw(self, surface):
        sw, sh = surface.get_size()
        surface.fill(COLOR_BG)
        title_surf = self.title_font.render("STARTERRA", True, COLOR_ACCENT)
        title_rect = title_surf.get_rect(center=(sw//2, 150))
        surface.blit(title_surf, title_rect)
        for btn in self.buttons:
            btn.rect.centerx = sw // 2
            btn.draw(surface)

class PauseMenu:
    def __init__(self):
        self.font = pygame.font.SysFont("Arial", 48, bold=True)
        self.buttons = [
            Button(0, 250, 300, 50, "CONTINUAR", COLOR_SUCCESS),
            Button(0, 320, 300, 50, "REINICIAR", COLOR_WARN),
            Button(0, 390, 300, 50, "VOLTAR AO MENU", COLOR_DANGER)
        ]

    def handle_event(self, event):
        for i, btn in enumerate(self.buttons):
            if btn.handle_event(event):
                return i 
        return None

    def draw(self, surface):
        sw, sh = surface.get_size()
        overlay = pygame.Surface((sw, sh), pygame.SRCALPHA)
        overlay.fill((10, 10, 20, 180))
        surface.blit(overlay, (0, 0))
        title = self.font.render("PAUSADO", True, COLOR_TEXT)
        surface.blit(title, title.get_rect(center=(sw//2, 180)))
        for btn in self.buttons:
            btn.rect.centerx = sw // 2
            btn.draw(surface)

class SettingsWindow:
    def __init__(self):
        self.font = pygame.font.SysFont("Arial", 24)
        self.title_font = pygame.font.SysFont("Arial", 32, bold=True)
        self.active = False
        self.current_res_idx = 0
        self.current_mode = WindowMode.WINDOWED
        
        self.btn_res = Button(0, 240, 320, 45, "ALTERAR RESOLUÇÃO")
        self.btn_mode = Button(0, 350, 320, 45, "ALTERAR MODO")
        self.btn_back = Button(0, 500, 320, 50, "VOLTAR E APLICAR", COLOR_SUCCESS)

    def handle_event(self, event):
        if not self.active: return None
        if self.btn_res.handle_event(event):
            self.current_res_idx = (self.current_res_idx + 1) % len(RESOLUTIONS)
            return "RES_CHANGE"
        if self.btn_mode.handle_event(event):
            modes = list(WindowMode)
            idx = modes.index(self.current_mode)
            self.current_mode = modes[(idx + 1) % len(modes)]
            return "MODE_CHANGE"
        if self.btn_back.handle_event(event):
            return "APPLY"
        return None

    def draw(self, surface):
        if not self.active: return
        sw, sh = surface.get_size()
        surface.fill(COLOR_BG)
        title = self.title_font.render("CONFIGURAÇÕES", True, COLOR_ACCENT)
        surface.blit(title, title.get_rect(center=(sw//2, 100)))
        
        res = RESOLUTIONS[self.current_res_idx]
        res_txt = self.font.render(f"Resolução Selecionada: {res[0]}x{res[1]}", True, COLOR_ACCENT)
        mode_txt = self.font.render(f"Modo Selecionado: {self.current_mode.name}", True, COLOR_ACCENT)
        
        surface.blit(res_txt, res_txt.get_rect(center=(sw//2, 210)))
        self.btn_res.rect.centerx = sw // 2
        self.btn_res.draw(surface)
        
        surface.blit(mode_txt, mode_txt.get_rect(center=(sw//2, 320)))
        self.btn_mode.rect.centerx = sw // 2
        self.btn_mode.draw(surface)
        
        self.btn_back.rect.centerx = sw // 2
        self.btn_back.draw(surface)
