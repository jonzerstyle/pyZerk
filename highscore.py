import os
import json
import pygame
import globals
import sounds
import misc

def is_web_env():
    """Detect if running inside Pygbag WebAssembly / browser environment."""
    try:
        import platform
        return hasattr(platform, "window")
    except Exception:
        return False

def _load_web_storage():
    """Load high score from browser localStorage without touching the filesystem."""
    try:
        import platform
        if hasattr(platform, "window") and hasattr(platform.window, "localStorage"):
            ls = platform.window.localStorage
            stored_score = ls.getItem("pyzerk_high_score")
            stored_init = ls.getItem("pyzerk_high_initials")
            if stored_score is not None:
                globals.HIGH_SCORE = int(stored_score)
                globals.HIGH_SCORE_INITIALS = str(stored_init if stored_init else "CPU")[:3].upper()
                return True
    except Exception:
        pass
    return False

def _save_web_storage(score, initials):
    """Save high score to browser localStorage without touching the filesystem."""
    try:
        import platform
        if hasattr(platform, "window") and hasattr(platform.window, "localStorage"):
            ls = platform.window.localStorage
            ls.setItem("pyzerk_high_score", str(score))
            ls.setItem("pyzerk_high_initials", str(initials))
            return True
    except Exception:
        pass
    return False

def get_highscore_path():
    """Return absolute path for persistent highscore storage (desktop only)."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, "highscore.json")

def load_high_score():
    """Load high score and initials. Uses localStorage on web, file on desktop, with clean defaults."""
    # 1. In web environment: strictly use browser localStorage (no file operations)
    if is_web_env():
        if _load_web_storage():
            return globals.HIGH_SCORE, globals.HIGH_SCORE_INITIALS

    # 2. Desktop environment: load from local highscore.json
    if not is_web_env():
        try:
            path = get_highscore_path()
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    globals.HIGH_SCORE = int(data.get("score", 100))
                    globals.HIGH_SCORE_INITIALS = str(data.get("initials", "CPU"))[:3].upper()
                    return globals.HIGH_SCORE, globals.HIGH_SCORE_INITIALS
        except Exception:
            pass

    # 3. Default fallback
    globals.HIGH_SCORE = 100
    globals.HIGH_SCORE_INITIALS = "CPU"
    return globals.HIGH_SCORE, globals.HIGH_SCORE_INITIALS

def save_high_score(score, initials):
    """Save high score and 3-letter initials. Uses localStorage on web, file on desktop."""
    clean_initials = "".join([c for c in initials.upper() if c.isalnum() or c in "!?-"])[:3]
    if len(clean_initials) == 0:
        clean_initials = "AAA"
    while len(clean_initials) < 3:
        clean_initials += "_"
        
    globals.HIGH_SCORE = int(score)
    globals.HIGH_SCORE_INITIALS = clean_initials
    
    # 1. In web environment: strictly write to browser localStorage (NO file writes allowed)
    if is_web_env():
        _save_web_storage(globals.HIGH_SCORE, globals.HIGH_SCORE_INITIALS)
        return globals.HIGH_SCORE, globals.HIGH_SCORE_INITIALS

    # 2. Desktop environment: write to local highscore.json
    try:
        path = get_highscore_path()
        data = {
            "score": globals.HIGH_SCORE,
            "initials": globals.HIGH_SCORE_INITIALS
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception:
        pass
        
    return globals.HIGH_SCORE, globals.HIGH_SCORE_INITIALS

def is_high_score(score):
    """Check if the provided score qualifies as a new record."""
    return score > globals.HIGH_SCORE and score > 0


class Class_HighScoreEntry:
    """Arcade-style modal dialog allowing players to enter up to 3 initials."""
    def __init__(self, score):
        self.score = score
        self.initials = ["A", "A", "A"]
        self.char_index = 0
        self.active = True
        self.confirmed = False
        
        # Valid character set
        self.chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!?"
        
        # Fonts
        self.font_title = pygame.font.Font(None, 46)
        self.font_sub = pygame.font.Font(None, 24)
        self.font_score = pygame.font.Font(None, 34)
        self.font_char = pygame.font.Font(None, 62)
        self.font_arrow = pygame.font.Font(None, 22)
        self.font_hint = pygame.font.Font(None, 20)
        self.font_btn = pygame.font.Font(None, 24)

    def get_initials_string(self):
        """Return 3-character string from initials list."""
        res = "".join(self.initials).strip()
        return res if len(res) > 0 else "AAA"

    def handle_event(self, event):
        """Process keyboard input for initials entry. Returns 'CONFIRMED' when done."""
        if not self.active:
            return None

        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                save_high_score(self.score, self.get_initials_string())
                sounds.playSound(sounds.welcomeSound)
                self.active = False
                self.confirmed = True
                return "CONFIRMED"

            elif event.key == pygame.K_BACKSPACE:
                sounds.play_nav_sound()
                if self.char_index > 0:
                    self.char_index -= 1
                    self.initials[self.char_index] = "A"

            elif event.key == pygame.K_LEFT:
                sounds.play_nav_sound()
                self.char_index = max(0, self.char_index - 1)

            elif event.key == pygame.K_RIGHT:
                sounds.play_nav_sound()
                self.char_index = min(2, self.char_index + 1)

            elif event.key == pygame.K_UP:
                sounds.play_nav_sound()
                cur = self.initials[self.char_index]
                idx = self.chars.find(cur)
                if idx == -1:
                    idx = 0
                self.initials[self.char_index] = self.chars[(idx + 1) % len(self.chars)]

            elif event.key == pygame.K_DOWN:
                sounds.play_nav_sound()
                cur = self.initials[self.char_index]
                idx = self.chars.find(cur)
                if idx == -1:
                    idx = 0
                self.initials[self.char_index] = self.chars[(idx - 1) % len(self.chars)]

            else:
                # Direct letter typing
                if event.unicode and len(event.unicode) == 1:
                    ch = event.unicode.upper()
                    if ch in self.chars:
                        self.initials[self.char_index] = ch
                        sounds.play_nav_sound()
                        if self.char_index < 2:
                            self.char_index += 1

        return None

    def draw(self, surface):
        """Render high score entry arcade overlay onto surface."""
        sw, sh = surface.get_size()
        
        # Dimensions
        panel_w = 540
        panel_h = 330
        px = (sw - panel_w) // 2
        py = (sh - panel_h) // 2
        
        # Backdrop overlay with double arcade border
        panel_rect = pygame.Rect(px, py, panel_w, panel_h)
        pygame.draw.rect(surface, (12, 10, 20), panel_rect)
        pygame.draw.rect(surface, (255, 215, 0), panel_rect, 3)
        pygame.draw.rect(surface, (0, 200, 255), pygame.Rect(px + 4, py + 4, panel_w - 8, panel_h - 8), 1)

        # 1. Header Banner
        title_surf = self.font_title.render("★ NEW HIGH SCORE! ★", True, (255, 220, 40))
        surface.blit(title_surf, title_surf.get_rect(center=(px + panel_w // 2, py + 34)))

        sub_surf = self.font_sub.render("YOU ACHIEVED A NEW RECORD!", True, (0, 240, 255))
        surface.blit(sub_surf, sub_surf.get_rect(center=(px + panel_w // 2, py + 68)))

        score_text = self.font_score.render(f"FINAL SCORE: {self.score}", True, (255, 255, 255))
        surface.blit(score_text, score_text.get_rect(center=(px + panel_w // 2, py + 104)))

        # 2. Initials Input Boxes
        box_w = 64
        box_h = 72
        spacing = 24
        total_w = 3 * box_w + 2 * spacing
        start_x = px + (panel_w - total_w) // 2
        box_y = py + 138

        # Cursor blink animation
        now = pygame.time.get_ticks()
        is_blink_on = (now // 350) % 2 == 0

        for i in range(3):
            bx = start_x + i * (box_w + spacing)
            box_rect = pygame.Rect(bx, box_y, box_w, box_h)
            is_active = (i == self.char_index)

            # Box fill and border
            bg_col = (30, 25, 45) if is_active else (20, 18, 25)
            border_col = (255, 255, 0) if (is_active and is_blink_on) else ((0, 200, 220) if is_active else (80, 80, 100))
            pygame.draw.rect(surface, bg_col, box_rect)
            pygame.draw.rect(surface, border_col, box_rect, 3 if is_active else 1)

            # Up / Down Chevron indicators for active box
            if is_active:
                up_txt = self.font_arrow.render("▲", True, (255, 255, 0))
                dn_txt = self.font_arrow.render("▼", True, (255, 255, 0))
                surface.blit(up_txt, up_txt.get_rect(center=(bx + box_w // 2, box_y - 12)))
                surface.blit(dn_txt, dn_txt.get_rect(center=(bx + box_w // 2, box_y + box_h + 12)))

            # Character
            char = self.initials[i]
            char_col = (255, 255, 100) if is_active else (220, 220, 220)
            char_surf = self.font_char.render(char, True, char_col)
            surface.blit(char_surf, char_surf.get_rect(center=box_rect.center))

        # 3. Instruction & Confirmation Hint
        hint1 = self.font_hint.render("TYPE LETTERS (A-Z) OR USE UP/DOWN ARROWS TO CYCLE", True, (190, 190, 190))
        surface.blit(hint1, hint1.get_rect(center=(px + panel_w // 2, py + 252)))

        hint2 = self.font_btn.render("[PRESS ENTER TO CONFIRM INITIALS]", True, (255, 230, 60))
        surface.blit(hint2, hint2.get_rect(center=(px + panel_w // 2, py + 284)))
