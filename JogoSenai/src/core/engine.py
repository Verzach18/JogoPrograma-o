import pygame # type: ignore
import time
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
        self.editor = CodeEditor(side_x, 165, side_w, int(self.sh * 0.38)) 
        self.docs = TutorialWindow(side_x, self.sh - 265, side_w, 250) 
        self.hud = HUD()
        
        console_w = int(self.sw * 0.65)
        self.console = Console(20, self.sh - 150, console_w, 130)
        
        self.run_button = RunButton(side_panel_x, self.sh - 90, side_panel_w, 35)
        self.stop_button = StopButton(side_panel_x, self.sh - 50, side_panel_w, 35)
        self.research_window = ResearchWindow(self.sw//2 - 225, self.sh//2 - 250, 450, 500) # Increased height
        
        # Windows visibility
        self.docs.active = True
        self.editor.active = True
        
        # Window Management (Z-order)
        self.windows = [self.editor, self.docs]
        
        self.last_step_time = 0
        self.drone_speed = INITIAL_SPEED

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
        
        # 1. Mission (Handled by HUD, but we reserve space)
        # y: 55, h: 105
        
        # 2. Editor (Middle)
        self.editor = CodeEditor(side_x, 165, side_w, int(sh * 0.38))
        
        # 3. Tutorial (Bottom)
        self.docs = TutorialWindow(side_x, sh - 265, side_w, 250)
        self.docs.active = True
        
        self.windows = [self.editor, self.docs]
        
        console_w = int(sw * 0.65)
        self.console = Console(20, sh - 150, console_w, 130)
        
        # Move buttons to a more accessible place (Below Console or next to it)
        self.run_button = RunButton(side_x, sh - 95, side_w, 40)
        self.stop_button = StopButton(side_x, sh - 50, side_w, 40)
        self.research_window = ResearchWindow(sw//2 - 225, sh//2 - 200, 450, 400)
        # Note: self.docs.active will be handled by the caller or defaults to False

    def reset_game(self):
        self.world = World()
        self.drone = Drone()
        self.progression = ProgressionManager()
        self.executor = ScriptExecutor(self.drone, self.progression)
        self.oxygen = 0.0
        self.temperature = -50.0

    def update(self):
        if self.state != GameState.PLAYING: return
        
        self.world.update(self)
        self.drone.update()
        
        # Execute Drone Queue
        now = time.time()
        if not self.drone.command_queue.empty() and now - self.last_step_time > self.drone_speed:
            action = self.drone.execute_step(self.world)
            self.missions.update_progress(action, self.drone)
            self.last_step_time = now
            
        self.notifications.update()

    def draw(self):
        if self.state == GameState.MENU:
            self.main_menu.draw(self.screen)
            pygame.display.flip()
            return
            
        if self.state == GameState.SETTINGS:
            self.settings_menu.draw(self.screen)
            pygame.display.flip()
            return

        self.screen.fill(COLOR_BG)
        
        # World & Drone
        self.world.draw(self.screen, self.camera_offset)
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
