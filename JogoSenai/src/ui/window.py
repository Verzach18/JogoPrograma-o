import pygame # type: ignore
from config import *

class Window:
    def __init__(self, x, y, w, h, title):
        self.rect = pygame.Rect(x, y, w, h)
        self.full_h = h
        self.title = title
        self.dragging = False
        self.rel_x = 0
        self.rel_y = 0
        self.active = False
        self.minimized = False
        self.font_title = pygame.font.SysFont("Arial", 16, bold=True)
        self.color_close = (200, 50, 50)
        self.color_min = (200, 200, 50)
        self.close_btn_rect = pygame.Rect(self.rect.right - 35, self.rect.y + 5, 25, 25)
        self.min_btn_rect = pygame.Rect(self.rect.right - 65, self.rect.y + 5, 25, 25)
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                # Update rects for clicking
                self.close_btn_rect = pygame.Rect(self.rect.right - 35, self.rect.y + 5, 25, 25)
                self.min_btn_rect = pygame.Rect(self.rect.right - 65, self.rect.y + 5, 25, 25)
                
                if self.close_btn_rect.collidepoint(event.pos):
                    return "CLOSE"
                
                if self.min_btn_rect.collidepoint(event.pos):
                    self.minimized = not self.minimized
                    if self.minimized:
                        self.rect.h = 35
                    else:
                        self.rect.h = self.full_h
                    return True
                
                # Title bar check for dragging
                title_bar = pygame.Rect(self.rect.x, self.rect.y, self.rect.w, 35)
                if title_bar.collidepoint(event.pos):
                    self.dragging = True
                    self.rel_x = self.rect.x - event.pos[0]
                    self.rel_y = self.rect.y - event.pos[1]
                    self.active = True
                    return True
                elif self.rect.collidepoint(event.pos):
                    self.active = True
                    return True
                else:
                    self.active = False
                    
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
            
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                self.rect.x = event.pos[0] + self.rel_x
                self.rect.y = event.pos[1] + self.rel_y
        return False

    def draw_base(self, surface):
        # Create a transparent surface for the window body
        win_surf = pygame.Surface((self.rect.w, self.rect.h), pygame.SRCALPHA)
        
        # Window Body (Glass effect)
        alpha = 240 if self.active else 180
        bg_color = (15, 18, 30, alpha)
        pygame.draw.rect(win_surf, bg_color, (0, 0, self.rect.w, self.rect.h), border_radius=10)
        
        # Title Bar Gradient-ish
        t_color = (45, 55, 90, 255) if self.active else (35, 40, 60, 200)
        pygame.draw.rect(win_surf, t_color, (0, 0, self.rect.w, 35), 
                         border_top_left_radius=10, border_top_right_radius=10,
                         border_bottom_left_radius=10 if self.minimized else 0,
                         border_bottom_right_radius=10 if self.minimized else 0)
        # Subtle light highlight on top of title bar
        pygame.draw.line(win_surf, (100, 120, 200, 150), (10, 1), (self.rect.w - 10, 1), 1)
        
        # Inner Shadow/Glow effect
        if self.active:
            pygame.draw.rect(win_surf, (0, 150, 255, 40), (0, 0, self.rect.w, self.rect.h), width=5, border_radius=10)

        # Border (Neon Glow)
        border_color = COLOR_ACCENT if self.active else (60, 65, 80)
        pygame.draw.rect(win_surf, border_color, (0, 0, self.rect.w, self.rect.h), width=2, border_radius=10)
        
        # Draw on main surface
        surface.blit(win_surf, self.rect)
        
        # Title Text
        title_surf = self.font_title.render(self.title, True, COLOR_TEXT)
        surface.blit(title_surf, (self.rect.x + 15, self.rect.y + 8))
        
        # Buttons
        self.close_btn_rect = pygame.Rect(self.rect.right - 35, self.rect.y + 5, 25, 25)
        self.min_btn_rect = pygame.Rect(self.rect.right - 65, self.rect.y + 5, 25, 25)
        
        # X Button
        pygame.draw.rect(surface, self.color_close, self.close_btn_rect, border_radius=4)
        x_surf = self.font_title.render("X", True, (255, 255, 255))
        surface.blit(x_surf, x_surf.get_rect(center=self.close_btn_rect.center))
        
        # Min Button
        pygame.draw.rect(surface, self.color_min, self.min_btn_rect, border_radius=4)
        m_surf = self.font_title.render("-" if not self.minimized else "+", True, (0, 0, 0))
        surface.blit(m_surf, m_surf.get_rect(center=self.min_btn_rect.center))
