import pygame # type: ignore
from config import *
from ui.window import Window

class CodeEditor(Window):
    def __init__(self, x, y, w, h):
        super().__init__(x, y, w, h, "main.py")
        self.lines = ["# Bem-vindo ao StarTerra", ""]
        self.cursor_line = 1
        self.cursor_col = 0
        self.font = pygame.font.SysFont("Consolas", 16)
        self.blink_timer = 0
        
        # Autocomplete
        self.suggestions = []
        self.suggestion_idx = 0
        self.show_suggestions = False
        self.keywords = {
            "drone.": ["move(", "till()", "plant(", "harvest()", "build_miner()", "build_atmo_gen()", "build_heater()", "do_a_flip()"],
            "Direction.": ["UP", "DOWN", "LEFT", "RIGHT"],
            "Entities.": ["GRASS", "TREE", "MINER", "ATMOSPHERE_GEN", "HEATER", "MINERAL_NODE"]
        }
        self.all_base_keywords = ["drone", "Direction", "Entities", "while", "for", "if", "else", "True", "False"]

    def get_current_word(self):
        line = self.lines[self.cursor_line]
        start = self.cursor_col
        while start > 0 and (line[start-1].isalnum() or line[start-1] in "._"):
            start -= 1
        return line[start:self.cursor_col]

    def update_suggestions(self):
        word = self.get_current_word()
        self.suggestions = []
        
        if not word:
            self.show_suggestions = False
            return

        # Check for member access (e.g., drone.)
        for key, members in self.keywords.items():
            if word.startswith(key):
                sub_word = word[len(key):]
                self.suggestions = [m for m in members if m.lower().startswith(sub_word.lower())]
                break
        else:
            # Check for base keywords
            self.suggestions = [k for k in self.all_base_keywords if k.lower().startswith(word.lower())]

        self.show_suggestions = len(self.suggestions) > 0
        self.suggestion_idx = min(self.suggestion_idx, max(0, len(self.suggestions)-1))

    def handle_event(self, event):
        if super().handle_event(event): return True
        
        if self.active and event.type == pygame.KEYDOWN:
            # Handle Autocomplete Selection
            if self.show_suggestions:
                if event.key == pygame.K_UP:
                    self.suggestion_idx = (self.suggestion_idx - 1) % len(self.suggestions)
                    return True
                if event.key == pygame.K_DOWN:
                    self.suggestion_idx = (self.suggestion_idx + 1) % len(self.suggestions)
                    return True
                if event.key in [pygame.K_TAB, pygame.K_RETURN]:
                    self.complete_word()
                    return True
                if event.key == pygame.K_ESCAPE:
                    self.show_suggestions = False
                    return True

            # Normal Typing
            if event.key == pygame.K_BACKSPACE:
                if self.cursor_col > 0:
                    line = self.lines[self.cursor_line]
                    self.lines[self.cursor_line] = line[:self.cursor_col-1] + line[self.cursor_col:]
                    self.cursor_col -= 1
                elif self.cursor_line > 0:
                    prev_len = len(self.lines[self.cursor_line-1])
                    self.lines[self.cursor_line-1] += self.lines[self.cursor_line]
                    self.lines.pop(self.cursor_line)
                    self.cursor_line -= 1
                    self.cursor_col = prev_len
            elif event.key == pygame.K_RETURN:
                line = self.lines[self.cursor_line]
                self.lines[self.cursor_line] = line[:self.cursor_col]
                self.lines.insert(self.cursor_line + 1, line[self.cursor_col:])
                self.cursor_line += 1
                self.cursor_col = 0
            elif event.key == pygame.K_UP:
                self.cursor_line = max(0, self.cursor_line - 1)
                self.cursor_col = min(self.cursor_col, len(self.lines[self.cursor_line]))
            elif event.key == pygame.K_DOWN:
                self.cursor_line = min(len(self.lines) - 1, self.cursor_line + 1)
                self.cursor_col = min(self.cursor_col, len(self.lines[self.cursor_line]))
            elif event.key == pygame.K_LEFT:
                self.cursor_col = max(0, self.cursor_col - 1)
            elif event.key == pygame.K_RIGHT:
                self.cursor_col = min(len(self.lines[self.cursor_line]), self.cursor_col + 1)
            elif event.key == pygame.K_TAB:
                # Add 4 spaces if no suggestions
                line = self.lines[self.cursor_line]
                self.lines[self.cursor_line] = line[:self.cursor_col] + "    " + line[self.cursor_col:]
                self.cursor_col += 4
            else:
                if event.unicode and event.unicode.isprintable():
                    line = self.lines[self.cursor_line]
                    self.lines[self.cursor_line] = line[:self.cursor_col] + event.unicode + line[self.cursor_col:]
                    self.cursor_col += 1
            
            self.update_suggestions()
            return True
        return False

    def complete_word(self):
        if not self.suggestions: return
        
        word = self.get_current_word()
        completion = self.suggestions[self.suggestion_idx]
        
        # Find where the current word starts
        line = self.lines[self.cursor_line]
        start = self.cursor_col
        while start > 0 and (line[start-1].isalnum() or line[start-1] in "._"):
            start -= 1
            
        # Determine what to replace
        # If it's a member access like 'drone.mo', we replace 'mo' with 'move('
        if "." in word:
            dot_idx = word.rfind(".")
            replace_start = start + dot_idx + 1
        else:
            replace_start = start
            
        self.lines[self.cursor_line] = line[:replace_start] + completion + line[self.cursor_col:]
        self.cursor_col = replace_start + len(completion)
        self.show_suggestions = False

    def get_text(self):
        return "\n".join(self.lines)

    def draw(self, surface, engine=None):
        self.draw_base(surface)
        if self.minimized: return
        
        # Line Number Gutter
        gutter_w = 35
        gutter_rect = pygame.Rect(self.rect.x + 2, self.rect.y + 35, gutter_w, self.rect.h - 37)
        pygame.draw.rect(surface, (20, 22, 35), gutter_rect, border_bottom_left_radius=12)
        pygame.draw.line(surface, (60, 60, 100), (gutter_rect.right, gutter_rect.y), (gutter_rect.right, gutter_rect.bottom), 1)

        # Draw Text Area
        clip_rect = pygame.Rect(self.rect.x + gutter_w + 5, self.rect.y + 45, self.rect.w - gutter_w - 20, self.rect.h - 60)
        text_surface = pygame.Surface((clip_rect.w, clip_rect.h), pygame.SRCALPHA)
        
        for i, line in enumerate(self.lines):
            # Line Number
            num_surf = self.font.render(str(i+1), True, (80, 85, 120))
            num_rect = num_surf.get_rect(right=gutter_rect.right - 5, y=clip_rect.y + i * 22)
            surface.blit(num_surf, num_rect)

            # Highlighting current line
            if i == self.cursor_line and self.active:
                h_rect = pygame.Rect(0, i * 22, clip_rect.w, 22)
                pygame.draw.rect(text_surface, (50, 60, 100, 100), h_rect)

            # Code
            color = COLOR_TEXT
            if line.strip().startswith("#"): color = (100, 150, 100)
            elif any(k in line for k in ["while", "if", "for", "def"]): color = (255, 120, 120)
            elif "drone." in line: color = COLOR_ACCENT
            
            surf = self.font.render(line, True, color)
            text_surface.blit(surf, (0, i * 22))
            
            # Cursor
            if i == self.cursor_line and self.active:
                self.blink_timer = (self.blink_timer + 1) % 60
                if self.blink_timer < 30:
                    cursor_x = self.font.size(line[:self.cursor_col])[0]
                    pygame.draw.line(text_surface, COLOR_SUCCESS, (cursor_x, i*22 + 2), (cursor_x, i*22 + 20), 2)
                    
        surface.blit(text_surface, (clip_rect.x, clip_rect.y))
        
        # Draw Suggestions Popup (rest unchanged)
        if self.show_suggestions and self.active:
            cursor_x = self.font.size(self.lines[self.cursor_line][:self.cursor_col])[0]
            pos_x = clip_rect.x + cursor_x
            pos_y = clip_rect.y + (self.cursor_line + 1) * 20
            
            popup_w = 180
            popup_h = len(self.suggestions) * 20 + 4
            
            # Border & BG
            pygame.draw.rect(surface, (25, 25, 40), (pos_x, pos_y, popup_w, popup_h))
            pygame.draw.rect(surface, COLOR_ACCENT, (pos_x, pos_y, popup_w, popup_h), 1)
            
            for i, suggestion in enumerate(self.suggestions):
                bg_color = (60, 80, 150) if i == self.suggestion_idx else (25, 25, 40)
                if i == self.suggestion_idx:
                    pygame.draw.rect(surface, bg_color, (pos_x + 1, pos_y + 1 + i*20, popup_w - 2, 20))
                
                txt = self.font.render(suggestion, True, (255, 255, 255))
                surface.blit(txt, (pos_x + 5, pos_y + 2 + i*20))
