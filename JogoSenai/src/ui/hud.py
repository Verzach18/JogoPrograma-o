import pygame # type: ignore
import math
import time
from config import *
from ui.window import Window

class HUD:
    def __init__(self):
        self.font = pygame.font.SysFont("Arial", 18, bold=True)
        self.font_small = pygame.font.SysFont("Arial", 14)
        self.research_btn_rect = pygame.Rect(SCREEN_WIDTH - 150, 5, 140, 30)
        
    def wrap_text(self, text, font, max_width):
        words = text.split(' ')
        lines = []
        current_line = []
        for word in words:
            current_line.append(word)
            if font.size(' '.join(current_line))[0] > max_width:
                current_line.pop()
                lines.append(' '.join(current_line))
                current_line = [word]
        lines.append(' '.join(current_line))
        return lines

    def draw_progress_bar(self, surface, x, y, w, h, progress, color):
        pygame.draw.rect(surface, (40, 45, 60), (x, y, w, h), border_radius=4)
        progress_w = int(w * min(progress, 1.0))
        if progress_w > 0:
            pygame.draw.rect(surface, color, (x, y, progress_w, h), border_radius=4)
        pygame.draw.rect(surface, (100, 100, 150), (x, y, w, h), width=1, border_radius=4)

    def draw_progress_bar_custom(self, surface, x, y, w, h, progress, color, alpha):
        bar_surf = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(bar_surf, (40, 45, 60, alpha), (0, 0, w, h), border_radius=4)
        progress_w = int(w * min(progress, 1.0))
        if progress_w > 0:
            pygame.draw.rect(bar_surf, (*color, alpha), (0, 0, progress_w, h), border_radius=4)
        pygame.draw.rect(bar_surf, (100, 100, 150, alpha), (0, 0, w, h), width=1, border_radius=4)
        surface.blit(bar_surf, (x, y))

    def draw(self, surface, engine):
        sw, sh = surface.get_size()
        drone = engine.drone
        progression = engine.progression
        now = time.time()
        
        # Top Bar (Glassmorphism)
        bar_surf = pygame.Surface((sw, 45), pygame.SRCALPHA)
        pygame.draw.rect(bar_surf, (20, 25, 45, 220), (0, 0, sw, 45))
        pygame.draw.line(bar_surf, COLOR_ACCENT, (0, 45), (sw, 45), 2)
        surface.blit(bar_surf, (0, 0))
        
        # Resources
        res_text = f"Biomass: {drone.resources['Biomass']} | Minerals: {drone.resources['Minerals']}"
        res_surf = self.font.render(res_text, True, (0, 255, 100))
        surface.blit(res_surf, (20, 10))

        # Current Mission (Relocated to Side Panel)
        if engine.missions.active_mission:
            m = engine.missions.active_mission
            
            # Position: Top of Sidebar
            box_w = int(sw * 0.30)
            side_x = sw - box_w - 20
            box_h = 100
            box_y = 55
            
            # Shift editor down if needed (handled in engine.py, but let's draw here for now)
            # Actually, let's just draw it at a fixed top-right position
            
            mission_bg = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
            pygame.draw.rect(mission_bg, (15, 20, 35, 230), (0, 0, box_w, box_h), border_radius=8)
            pygame.draw.rect(mission_bg, COLOR_ACCENT, (0, 0, box_w, box_h), width=1, border_radius=8)
            
            # Header
            pygame.draw.rect(mission_bg, (30, 40, 60, 255), (0, 0, box_w, 25), border_top_left_radius=8, border_top_right_radius=8)
            surface.blit(mission_bg, (side_x, box_y))
            
            title = self.font_small.render(f"QUEST: {m.title}", True, COLOR_ACCENT)
            surface.blit(title, (side_x + 10, box_y + 4))
            
            desc_lines = self.wrap_text(m.description, self.font_small, box_w - 20)
            for i, line in enumerate(desc_lines[:2]):
                txt = self.font_small.render(line, True, COLOR_TEXT)
                surface.blit(txt, (side_x + 10, box_y + 30 + i * 18))
            
            # Progress bar
            self.draw_progress_bar(surface, side_x + 10, box_y + 70, box_w - 20, 8, 
                                 m.current_count / m.target_count, COLOR_ACCENT)
            
            if hasattr(m, 'hint') and m.hint:
                hint = self.font_small.render(f"> {m.hint}", True, (150, 150, 200))
                surface.blit(hint, (side_x + 10, box_y + 82))

        # Terraforming Stats (Center)
        stats_x = sw // 2 - 150
        o2_label = self.font_small.render(f"O2: {engine.oxygen:.1f}%", True, (100, 200, 255))
        surface.blit(o2_label, (stats_x, 5))
        self.draw_progress_bar(surface, stats_x, 22, 140, 10, engine.oxygen / 100.0, (100, 200, 255))
        
        temp_label = self.font_small.render(f"TEMP: {engine.temperature:.1f}°C", True, (255, 150, 50))
        surface.blit(temp_label, (stats_x + 160, 5))
        temp_progress = (engine.temperature + 50) / 100.0
        self.draw_progress_bar(surface, stats_x + 160, 22, 140, 10, temp_progress, (255, 150, 50))
        
        # Unlocks Status
        self.research_btn_rect = pygame.Rect(sw - 150, 7, 140, 30)
        status_x = self.research_btn_rect.x - 320
        for i, (feat, unlocked) in enumerate(progression.unlocked.items()):
            if i > 4: break
            color = (0, 255, 0) if unlocked else (100, 100, 100)
            text = self.font_small.render(f"{feat.upper()}", True, color)
            surface.blit(text, (status_x + i*60, 15))

        # Pulse Research button if mission is research
        r_btn_color = (60, 60, 100)
        if engine.missions.active_mission and engine.missions.active_mission.id == "research":
            pulse = (math.sin(now * 5) + 1) / 2
            r_btn_color = (40 + pulse * 40, 60 + pulse * 40, 150 + pulse * 105)

        pygame.draw.rect(surface, r_btn_color, self.research_btn_rect, border_radius=4)
        r_text = self.font_small.render("RESEARCH LAB (R)", True, COLOR_TEXT)
        r_rect = r_text.get_rect(center=self.research_btn_rect.center)
        surface.blit(r_text, r_rect)

class TutorialWindow(Window):
    def __init__(self, x, y, w, h):
        super().__init__(x, y, w, h, "Guia de Comandos")
        self.font = pygame.font.SysFont("Arial", 13)
        
    def handle_event(self, event):
        res = super().handle_event(event)
        # We don't allow closing the tutorial window in the sidebar layout
        return res
        
    def draw(self, surface, engine):
        self.draw_base(surface)
        if self.minimized: return
        
        content = []
        prog = engine.progression
        
        content.append("COMANDOS BÁSICOS:")
        content.append("- drone.move(Direction.UP/DOWN/LEFT/RIGHT)")
        content.append("- drone.till(): Preparar solo")
        content.append("- drone.plant(Entities.GRASS): Plantar")
        content.append("- drone.harvest(): Coletar biomassa")
        
        content.append("")
        content.append("ESTRUTURAS:")
        if prog.can_use("miner"):
            content.append("- drone.build_miner(): Minerador Automático")
        else: content.append("- (Bloqueado) Minerador")
            
        if prog.can_use("atmo_gen_unlock"):
            content.append("- drone.build_atmo_gen(): Gerador de O2")
        else: content.append("- (Bloqueado) Gerador O2")

        if prog.can_use("loops") or prog.can_use("if_statements"):
            content.append("")
            content.append("PROGRAMAÇÃO AVANÇADA:")
            if prog.can_use("loops"): content.append("- while True: (Loop infinito)")
            if prog.can_use("if_statements"): content.append("- if drone.can_harvest(): (Condicional)")

        for i, line in enumerate(content):
            color = COLOR_TEXT
            px = 15
            if "BÁSICOS" in line or "ESTRUTURAS" in line or "AVANÇADA" in line: 
                color = COLOR_SUCCESS
                px = 10
                # Small underline for headers
                pygame.draw.line(surface, (40, 50, 80), (self.rect.x + 10, self.rect.y + 60 + i * 18), 
                                 (self.rect.right - 10, self.rect.y + 60 + i * 18), 1)
            elif "-" in line: 
                color = (200, 200, 255)
                px = 20
            elif "(Bloqueado)" in line: 
                color = (100, 100, 110)
                px = 20
            
            surf = self.font.render(line, True, color)
            surface.blit(surf, (self.rect.x + px, self.rect.y + 45 + i * 18))
