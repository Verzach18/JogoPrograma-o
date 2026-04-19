import pygame # type: ignore
import time
from config import *

class Notification:
    def __init__(self, title, message, duration=5.0, color=COLOR_ACCENT):
        self.title = title
        self.message = message
        self.duration = duration
        self.start_time = time.time()
        self.color = color
        self.fade_in = 0.5
        self.fade_out = 0.5
        
    def get_alpha(self):
        elapsed = time.time() - self.start_time
        if elapsed < self.fade_in:
            return int(255 * (elapsed / self.fade_in))
        elif elapsed > self.duration - self.fade_out:
            return int(255 * (1.0 - (elapsed - (self.duration - self.fade_out)) / self.fade_out))
        elif elapsed > self.duration:
            return 0
        return 255

class NotificationSystem:
    def __init__(self):
        self.queue = []
        self.current = None
        self.font_title = pygame.font.SysFont("Arial", 20, bold=True)
        self.font_msg = pygame.font.SysFont("Arial", 16)
        self.icon_ai = None # Could be an image later
        
    def add_notification(self, title, message, duration=5.0, color=COLOR_ACCENT):
        self.queue.append(Notification(title, message, duration, color))
        
    def update(self):
        if self.current:
            if time.time() - self.current.start_time > self.current.duration:
                self.current = None
        
        if not self.current and self.queue:
            self.current = self.queue.pop(0)
            self.current.start_time = time.time()
            
    def draw(self, surface):
        if not self.current:
            return
            
        alpha = self.current.get_alpha()
        if alpha <= 0: return
        
        sw, sh = surface.get_size()
        w, h = 420, 85
        x = (sw - w) // 2
        y = 60 # Below top bar
        
        # Background (Glass)
        notif_surf = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(notif_surf, (15, 20, 35, alpha if alpha < 210 else 210), (0, 0, w, h), border_radius=15)
        pygame.draw.rect(notif_surf, (*self.current.color, alpha), (0, 0, w, h), width=2, border_radius=15)
        
        # AI Icon (Procedural)
        icon_x, icon_y = 35, 42
        # Outer glow
        pygame.draw.circle(notif_surf, (*self.current.color, alpha // 4), (icon_x, icon_y), 22)
        # Core
        pygame.draw.circle(notif_surf, (30, 40, 60, alpha), (icon_x, icon_y), 18)
        # Inner Neon Diamond
        points = [(icon_x, icon_y-12), (icon_x+12, icon_y), (icon_x, icon_y+12), (icon_x-12, icon_y)]
        pygame.draw.polygon(notif_surf, (*self.current.color, alpha), points, width=2)
        pygame.draw.circle(notif_surf, COLOR_TEXT, (icon_x, icon_y), 3)

        # Title
        title_surf = self.font_title.render(self.current.title, True, self.current.color)
        title_surf.set_alpha(alpha)
        notif_surf.blit(title_surf, (70, 15))
        
        # Message
        # Simple text wrapping logic for message if too long
        words = self.current.message.split(' ')
        lines = []
        current_line = []
        for word in words:
            current_line.append(word)
            test_line = ' '.join(current_line)
            if self.font_msg.size(test_line)[0] > w - 90:
                current_line.pop()
                lines.append(' '.join(current_line))
                current_line = [word]
        lines.append(' '.join(current_line))

        for i, line in enumerate(lines[:2]): # Limit to 2 lines
            msg_surf = self.font_msg.render(line, True, COLOR_TEXT)
            msg_surf.set_alpha(alpha)
            notif_surf.blit(msg_surf, (70, 42 + i * 20))
        
        surface.blit(notif_surf, (x, y))
