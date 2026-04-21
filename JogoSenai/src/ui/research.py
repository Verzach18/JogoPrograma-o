import pygame # type: ignore
from config import *
from ui.window import Window

class ResearchWindow(Window):
    def __init__(self, x, y, w, h):
        super().__init__(x, y, w, h, "SCIENCE & RESEARCH")
        self.font = pygame.font.SysFont("Arial", 14)
        self.font_bold = pygame.font.SysFont("Arial", 15, bold=True)
        self.font_btn = pygame.font.SysFont("Arial", 12, bold=True)
        self.scroll_y = 0
        
        self.upgrades = [
            # Software
            {"id": "if_statements", "cat": "SOFTWARE", "name": "LOGIC: CONDITIONALS", "desc": "Unlocks IF/ELSE statements"},
            {"id": "loops", "cat": "SOFTWARE", "name": "LOGIC: LOOPS", "desc": "Unlocks WHILE/FOR loops"},
            {"id": "functions", "cat": "SOFTWARE", "name": "LOGIC: FUNCTIONS", "desc": "Unlocks DEFS"},
            {"id": "navigation_unlock", "cat": "SOFTWARE", "name": "NAV: MODULE I", "desc": "Unlocks drone.move_to()"},
            {"id": "inspector_unlock", "cat": "SOFTWARE", "name": "SENS: INSPECTOR", "desc": "Unlocks drone.inspect()"},
            
            # Hardware
            {"id": "speed_upgrade_1", "cat": "HARDWARE", "name": "ENG: OVERCLOCK I", "desc": "30% faster actions"},
            {"id": "speed_upgrade_2", "cat": "HARDWARE", "name": "ENG: OVERCLOCK II", "desc": "50% faster actions"},
            {"id": "battery_1", "cat": "HARDWARE", "name": "BAT: STORAGE I", "desc": "+50 Max Energy"},
            {"id": "battery_2", "cat": "HARDWARE", "name": "BAT: STORAGE II", "desc": "+100 Max Energy"},
            
            # Planet
            {"id": "miner_unlock", "cat": "PLANET", "name": "IND: MINING I", "desc": "Unlocks Auto Miners"},
            {"id": "atmo_gen_unlock", "cat": "PLANET", "name": "BIO: ATMOSPHERE I", "desc": "Unlocks O2 Generators"},
            {"id": "heater_unlock", "cat": "PLANET", "name": "GEO: THERMAL I", "desc": "Unlocks Heaters"},
        ]
        self.content_h = len(self.upgrades) * 55 + 60
        self.view_h = h - 40

    def handle_event(self, event, progression, drone):
        if not self.active: return False
        res = super().handle_event(event)
        if res == "CLOSE": self.active = False; return True
        if res: return True
        
        if self.active:
            if event.type == pygame.MOUSEWHEEL:
                self.scroll_y = max(0, min(self.scroll_y - event.y * 30, self.content_h - self.view_h))
                return True
                
            if event.type == pygame.MOUSEBUTTONDOWN:
                if not self.rect.collidepoint(event.pos): return False
                
                # Check for clicks on upgrades (offset by scroll)
                for i, upgrade in enumerate(self.upgrades):
                    if not progression.is_visible(upgrade["id"]) and not progression.can_use(upgrade["id"]):
                        continue
                    
                    # Button relative to window top (after title bar)
                    y_pos = 60 + i * 55 - self.scroll_y
                    if y_pos < 30 or y_pos > self.rect.h - 30: continue # Out of view
                    
                    btn_rect = pygame.Rect(self.rect.x + self.rect.w - 110, self.rect.y + y_pos + 8, 100, 25)
                    if btn_rect.collidepoint(event.pos):
                        if progression.buy(upgrade["id"], drone):
                            drone.log(f"RESEARCH COMPLETE: {upgrade['name']}")
                        return True
        return False

    def draw(self, surface, progression, drone):
        if not self.active: return
        self.draw_base(surface)
        if self.minimized: return
        
        # Create a clipping area for the content
        content_rect = pygame.Rect(self.rect.x + 2, self.rect.y + 35, self.rect.w - 4, self.rect.h - 40)
        old_clip = surface.get_clip()
        surface.set_clip(content_rect)
        
        offset_y = 50 - self.scroll_y
        for i, upgrade in enumerate(self.upgrades):
            y_pos = self.rect.y + offset_y + i * 55
            
            # Skip drawing if far outside clip
            if y_pos < self.rect.y - 20 or y_pos > self.rect.bottom + 20:
                continue

            unlocked = progression.can_use(upgrade["id"])
            visible = progression.is_visible(upgrade["id"]) or unlocked
            
            # Category Header (if changed)
            if i == 0 or upgrade["cat"] != self.upgrades[i-1]["cat"]:
                pygame.draw.rect(surface, (40, 45, 70), (self.rect.x + 5, y_pos - 15, self.rect.w - 10, 15), border_radius=4)
                cat_surf = self.font_btn.render(upgrade["cat"], True, (150, 150, 200))
                surface.blit(cat_surf, (self.rect.x + 15, y_pos - 15))

            if not visible:
                name_surf = self.font_bold.render("??? [LOCKED]", True, (80, 80, 90))
                surface.blit(name_surf, (self.rect.x + 15, y_pos + 5))
                pygame.draw.line(surface, (30, 30, 40), (self.rect.x + 10, y_pos + 35), (self.rect.x + self.rect.w - 10, y_pos + 35))
                continue

            # Name & Desc
            name_surf = self.font_bold.render(upgrade["name"], True, COLOR_ACCENT if not unlocked else COLOR_SUCCESS)
            surface.blit(name_surf, (self.rect.x + 15, y_pos + 2))
            
            desc_surf = self.font.render(upgrade["desc"], True, (160, 170, 190))
            surface.blit(desc_surf, (self.rect.x + 15, y_pos + 18))
            
            # Button
            btn_rect = pygame.Rect(self.rect.x + self.rect.w - 110, y_pos + 8, 100, 25)
            cost = COSTS.get(upgrade["id"], 0)
            can_afford = drone.resources["Biomass"] >= cost
            
            if unlocked:
                color = (60, 80, 150)
                btn_text = "UNLOCKED"
            elif can_afford:
                color = (50, 150, 50)
                btn_text = f"BUY ({cost})"
            else:
                color = (80, 40, 40)
                btn_text = f"NEED {cost}"
            
            pygame.draw.rect(surface, color, btn_rect, border_radius=4)
            text_surf = self.font_btn.render(btn_text, True, COLOR_TEXT)
            text_rect = text_surf.get_rect(center=btn_rect.center)
            surface.blit(text_surf, text_rect)
            
            # Separator
            pygame.draw.line(surface, (40, 40, 60), (self.rect.x + 10, y_pos + 42), (self.rect.x + self.rect.w - 10, y_pos + 42))

        # Reset clip
        surface.set_clip(old_clip)
        
        # Draw scrollbar if needed
        if self.content_h > self.view_h:
            bar_h = int(self.view_h * (self.view_h / self.content_h))
            bar_y = self.rect.y + 35 + int(self.scroll_y * (self.view_h / self.content_h))
            pygame.draw.rect(surface, (60, 60, 100), (self.rect.right - 8, bar_y, 4, bar_h), border_radius=2)
