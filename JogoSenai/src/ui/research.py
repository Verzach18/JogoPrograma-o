import pygame # type: ignore
from config import *
from ui.window import Window

class ResearchWindow(Window):
    def __init__(self, x, y, w, h):
        super().__init__(x, y, w, h, "RESEARCH LAB")
        self.font = pygame.font.SysFont("Arial", 16)
        self.font_btn = pygame.font.SysFont("Arial", 14, bold=True)
        self.upgrades = [
            {"id": "loops", "name": "CONTROL FLOW: LOOPS", "desc": "Unlocks while/for loops"},
            {"id": "if_statements", "name": "CONTROL FLOW: IF", "desc": "Unlocks if/else conditions"},
            {"id": "functions", "name": "PROGRAMMING: FUNCTIONS", "desc": "Unlocks def function()"},
            {"id": "speed_upgrade", "name": "HARDWARE: SPEED I", "desc": "Reduces action delay by 20%"},
            {"id": "atmo_gen_unlock", "name": "PLANET: ATMOSPHERE I", "desc": "Unlocks O2 Generators"},
            {"id": "heater_unlock", "name": "PLANET: THERMAL I", "desc": "Unlocks Geothermal Heaters"},
            {"id": "grid_expand", "name": "HARDWARE: RADAR", "desc": "Expands world size"},
        ]

    def handle_event(self, event, progression, drone):
        if not self.active: return False
        
        res = super().handle_event(event)
        if res == "CLOSE":
            self.active = False
            return True
        if res: return True
        
        if self.active and event.type == pygame.MOUSEBUTTONDOWN:
            for i, upgrade in enumerate(self.upgrades):
                btn_rect = pygame.Rect(self.rect.x + self.rect.w - 110, self.rect.y + 60 + i * 60, 100, 30)
                if btn_rect.collidepoint(event.pos):
                    progression.buy(upgrade["id"], drone)
                    return True
        return False

    def draw(self, surface, progression, drone):
        if not self.active: return
        self.draw_base(surface)
        if self.minimized: return
        
        for i, upgrade in enumerate(self.upgrades):
            y_pos = self.rect.y + 50 + i * 60
            
            # Name & Desc
            name_surf = self.font.render(upgrade["name"], True, COLOR_ACCENT)
            surface.blit(name_surf, (self.rect.x + 15, y_pos))
            
            desc_surf = self.font.render(upgrade["desc"], True, (150, 150, 150))
            surface.blit(desc_surf, (self.rect.x + 15, y_pos + 18))
            
            # Button
            btn_rect = pygame.Rect(self.rect.x + self.rect.w - 110, y_pos + 10, 100, 30)
            unlocked = progression.can_use(upgrade["id"])
            cost = COSTS.get(upgrade["id"], 0)
            can_afford = drone.resources["Biomass"] >= cost
            
            color = (50, 200, 50) if not unlocked and can_afford else (100, 100, 100)
            if unlocked: color = (100, 150, 255)
            
            pygame.draw.rect(surface, color, btn_rect, border_radius=4)
            
            btn_text = f"UNLOCK ({cost})" if not unlocked else "UNLOCKED"
            text_surf = self.font_btn.render(btn_text, True, COLOR_TEXT)
            text_rect = text_surf.get_rect(center=btn_rect.center)
            surface.blit(text_surf, text_rect)
            
            # Separator
            pygame.draw.line(surface, (40, 40, 60), (self.rect.x + 10, y_pos + 50), (self.rect.x + self.rect.w - 10, y_pos + 50))
