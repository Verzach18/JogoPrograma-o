import pygame # type: ignore
import time
import random
from config import *
from entities.world import World
from entities.drone import Drone
from core.progression import ProgressionManager
from core.scripting import ScriptExecutor
from ui.editor import CodeEditor
from ui.hud import HUD, TutorialWindow
from ui.console import Console, RunButton, StopButton
from ui.research import ResearchWindow
from ui.menu import MainMenu, PauseMenu, SettingsWindow
from core.missions import MissionManager
from ui.notification import NotificationSystem

class GameEngine:
    def __init__(self):
        pygame.init()
        pygame.key.set_repeat(500, 50)
        
        # Menus (Must be initialized before apply_display_settings)
        self.settings_menu = SettingsWindow()
        self.main_menu = MainMenu()
        self.pause_menu = PauseMenu()
        
        self.sw, self.sh = SCREEN_WIDTH, SCREEN_HEIGHT
        self.apply_display_settings()

        pygame.display.set_caption("StarTerra: Farmer Was Replaced Edition")
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = GameState.MENU
        
        
        # Camera
        self.camera_offset = [50, 80]
        
        # Planet Stats
        self.oxygen = 0.0
        self.temperature = -50.0 # Starts cold
        
        # Core
        self.world = World()
        self.drone = Drone()
        self.progression = ProgressionManager()
        self.executor = ScriptExecutor(self.drone, self.progression)
        self.missions = MissionManager()
        self.notifications = NotificationSystem()
        self.missions.notifications = self.notifications
        
        # Welcome Notification
        self.notifications.add_notification("BEM-VINDO AO STARTERRA", "Siga os objetivos para terraformar o planeta.", duration=6.0)
        
        # UI (Relative Positioning)
        side_panel_x = int(self.sw * 0.68)
        side_panel_w = int(self.sw * 0.30)
        
        # Proportional sidebar stack (No overlap)
        side_w = int(self.sw * 0.30)
        side_x = self.sw - side_w - 20
        # Adjusted heights and positions for a clean stack
        self.editor = CodeEditor(side_x, 165, side_w, int(self.sh * 0.35)) 
        self.docs = TutorialWindow(side_x, 165 + int(self.sh * 0.35) + 10, side_w, int(self.sh * 0.22)) 
        self.hud = HUD()
        
        console_w = int(self.sw * 0.65)
        self.console = Console(20, self.sh - 150, console_w, 130)
        
        self.run_button = RunButton(side_x, self.sh - 90, side_w, 35)
        self.stop_button = StopButton(side_x, self.sh - 50, side_w, 35)
        self.research_window = ResearchWindow(self.sw//2 - 225, self.sh//2 - 250, 450, 500)
        
        # Windows visibility
        self.docs.active = True
        self.editor.active = True
        
        # Window Management (Z-order)
        self.windows = [self.editor, self.docs]
        
        self.last_step_time = 0
        self.drone_speed = INITIAL_SPEED

        # Visual Effects
        self.stars = []
        for _ in range(200):
            self.stars.append({
                "pos": [random.randint(0, self.sw), random.randint(0, self.sh)],
                "size": random.uniform(0.5, 2.5),
                "speed": random.uniform(0.02, 0.1),
                "color": random.choice([(255, 255, 255), (200, 220, 255), (255, 240, 200)])
            })
        self.particles = []

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT: self.running = False
            
            if self.state == GameState.MENU:
                choice = self.main_menu.handle_event(event)
                if choice == 0: self.state = GameState.PLAYING
                if choice == 1: self.state = GameState.SETTINGS; self.settings_menu.active = True
                if choice == 2: self.running = False
                continue

            if self.state == GameState.SETTINGS:
                res = self.settings_menu.handle_event(event)
                if res == "APPLY":
                    self.apply_display_settings()
                    self.state = GameState.MENU
                    self.settings_menu.active = False
                continue

            if self.state == GameState.PAUSED:
                choice = self.pause_menu.handle_event(event)
                if choice == 0: self.state = GameState.PLAYING
                if choice == 1: self.reset_game(); self.state = GameState.PLAYING
                if choice == 2: self.state = GameState.MENU
                continue

            # Playing State Events
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.state = GameState.PAUSED
                    continue

            if self.run_button.is_clicked(event):
                self.executor.execute(self.editor.get_text())
                
            if self.stop_button.is_clicked(event):
                self.executor.stop()
                
            if self.research_window.handle_event(event, self.progression, self.drone): 
                self.missions.update_progress("research", self.drone)
                continue

            # Handle windows events (No Z-order change)
            clicked_any = False
            for win in self.windows:
                res = win.handle_event(event)
                if res:
                    if win.active:
                        for other in self.windows:
                            if other != win: other.active = False
                    clicked_any = True
                    break
            
            if clicked_any: continue

            # Toggle Research Window
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                self.research_window.active = not self.research_window.active

            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.hud.research_btn_rect.collidepoint(event.pos):
                    self.research_window.active = not self.research_window.active

        # Camera Movement (WASD)
        keys = pygame.key.get_pressed()
        if not self.editor.active:
            if keys[pygame.K_w]: self.camera_offset[1] += 5
            if keys[pygame.K_s]: self.camera_offset[1] -= 5
            if keys[pygame.K_a]: self.camera_offset[0] += 5
            if keys[pygame.K_d]: self.camera_offset[0] -= 5

    def apply_display_settings(self):
        res = RESOLUTIONS[self.settings_menu.current_res_idx]
        mode = self.settings_menu.current_mode
        
        self.sw, self.sh = res
        flags = pygame.DOUBLEBUF | pygame.HWSURFACE
        
        if mode == WindowMode.FULLSCREEN:
            flags |= pygame.FULLSCREEN
            # Use desktop resolution for real fullscreen
            self.screen = pygame.display.set_mode((0,0), flags)
            info = pygame.display.Info()
            self.sw, self.sh = info.current_w, info.current_h
        elif mode == WindowMode.BORDERLESS:
            flags |= pygame.NOFRAME
            self.screen = pygame.display.set_mode((self.sw, self.sh), flags)
        else:
            self.screen = pygame.display.set_mode((self.sw, self.sh), flags)
            
        # Re-initialize UI positions
        was_active = self.docs.active if hasattr(self, 'docs') else True
        self.reposition_ui()
        self.docs.active = was_active

    def reposition_ui(self):
        # Sidebar positioning (Right side)
        sw, sh = self.sw, self.sh
        side_w = int(sw * 0.30)
        side_x = sw - side_w - 20
        
        # Proportional heights to avoid overlap in any resolution
        # Editor takes 35% of screen height
        editor_h = int(sh * 0.35)
        self.editor = CodeEditor(side_x, 165, side_w, editor_h)
        
        # Tutorial takes 25% of screen height, positioned below editor
        docs_y = 165 + editor_h + 10
        docs_h = int(sh * 0.25)
        self.docs = TutorialWindow(side_x, docs_y, side_w, docs_h)
        
        # Buttons are at the bottom of the sidebar area
        self.run_button = RunButton(side_x, sh - 95, side_w, 40)
        self.stop_button = StopButton(side_x, sh - 50, side_w, 40)
        
        # Ensure windows don't overlap the buttons
        if docs_y + docs_h > sh - 100:
            self.docs.rect.h = (sh - 105) - docs_y
            self.docs.full_h = self.docs.rect.h
            
        self.windows = [self.editor, self.docs]
        
        console_w = int(sw * 0.65)
        self.console = Console(20, sh - 150, console_w, 130)
        self.research_window = ResearchWindow(sw//2 - 225, sh//2 - 200, 450, 400)

    def reset_game(self):
        self.world = World()
        self.drone = Drone()
        self.progression = ProgressionManager()
        self.executor = ScriptExecutor(self.drone, self.progression)
        self.oxygen = 0.0
        self.temperature = -50.0

    def update(self):
        if self.state != GameState.PLAYING: return
        
        # Calculate Speed (Hardware upgrades)
        self.drone_speed = INITIAL_SPEED
        if self.progression.can_use("speed_upgrade_1"): self.drone_speed *= 0.7
        if self.progression.can_use("speed_upgrade_2"): self.drone_speed *= 0.5

        self.world.update(self)
        self.drone.update()
        
        # Execute Drone Queue
        now = time.time()
        if not self.drone.command_queue.empty() and now - self.last_step_time > self.drone_speed:
            action = self.drone.execute_step(self.world)
            self.missions.update_progress(action, self.drone)
            self.last_step_time = now
            
            # Emit particles for actions
            if action in ["till", "plant", "harvest"]:
                self.emit_particles(self.drone.x, self.drone.y, COLOR_ACCENT if action == "plant" else (100, 70, 50))
            
        self.notifications.update()
        
        # Update Particles
        for p in self.particles[:]:
            p["pos"][0] += p["vel"][0]
            p["pos"][1] += p["vel"][1]
            p["life"] -= 1
            if p["life"] <= 0:
                self.particles.remove(p)

    def emit_particles(self, x, y, color):
        px = x * TILE_SIZE + self.camera_offset[0] + TILE_SIZE // 2
        py = y * TILE_SIZE + self.camera_offset[1] + TILE_SIZE // 2
        for _ in range(10):
            self.particles.append({
                "pos": [px, py],
                "vel": [random.uniform(-2, 2), random.uniform(-2, 2)],
                "life": random.randint(20, 40),
                "color": color,
                "size": random.randint(2, 5)
            })

    def draw(self):
        if self.state == GameState.MENU:
            self.main_menu.draw(self.screen)
            pygame.display.flip()
            return
            
        if self.state == GameState.SETTINGS:
            self.settings_menu.draw(self.screen)
            pygame.display.flip()
            return

        # Calculate Dynamic Sky Color (Feature 1)
        o2_factor = min(1.0, self.oxygen / 100.0)
        if o2_factor < 0.5:
            # Transition Space -> Low Sky
            t = o2_factor * 2.0
            sky_color = [int(COLOR_SPACE[i] + (COLOR_SKY_LOW[i] - COLOR_SPACE[i]) * t) for i in range(3)]
        else:
            # Transition Low Sky -> Full Sky
            t = (o2_factor - 0.5) * 2.0
            sky_color = [int(COLOR_SKY_LOW[i] + (COLOR_SKY_FULL[i] - COLOR_SKY_LOW[i]) * t) for i in range(3)]

        self.screen.fill(sky_color)
        
        # 1. Draw Starfield (Parallax) - Stars fade as sky gets brighter
        star_alpha = max(0, 255 - int(o2_factor * 300))
        for star in self.stars:
            if star_alpha <= 0: break
            px = (star["pos"][0] + self.camera_offset[0] * star["speed"]) % self.sw
            py = (star["pos"][1] + self.camera_offset[1] * star["speed"]) % self.sh
            
            # Star color with alpha
            s_color = (*star["color"], star_alpha)
            s_surf = pygame.Surface((int(star["size"])*2, int(star["size"])*2), pygame.SRCALPHA)
            pygame.draw.circle(s_surf, s_color, (int(star["size"]), int(star["size"])), int(star["size"]))
            self.screen.blit(s_surf, (int(px), int(py)))

        # World & Drone
        self.world.draw(self.screen, self.camera_offset, self)
        self.drone.draw(self.screen, self.camera_offset)
        
        # Draw Windows in Z-order
        for win in self.windows:
            win.draw(self.screen, self)
                
        # Draw HUD (Always on top)
        self.hud.draw(self.screen, self)
        self.console.draw(self.screen, self.drone.logs)
        self.run_button.draw(self.screen)
        self.stop_button.draw(self.screen)
        self.research_window.draw(self.screen, self.progression, self.drone)
        self.notifications.draw(self.screen)
        
        # Draw Particles
        for p in self.particles:
            alpha = int(255 * (p["life"] / 40))
            p_surf = pygame.Surface((p["size"], p["size"]), pygame.SRCALPHA)
            pygame.draw.circle(p_surf, (*p["color"][:3], alpha), (p["size"]//2, p["size"]//2), p["size"]//2)
            self.screen.blit(p_surf, p["pos"])
        
        if self.state == GameState.PAUSED:
            self.pause_menu.draw(self.screen)

        pygame.display.flip()

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        pygame.quit()
