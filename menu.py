import pygame
import globals
import sounds

class Class_StartMenu:
    """Start menu for pyZerk.
    
    Features:
    1.0 Start a game
    2.0 Set music volume with sample output
    3.0 Set other sounds volume with sample output
    Explains key controls for the user.
    """
    def __init__(self):
        self.selected_index = 0
        self.sample_active_until = 0
        self.sample_type = ""
        
        # Color palette (retro arcade)
        self.BG_COLOR = (0, 0, 0)
        self.TITLE_COLOR = (0, 255, 64)
        self.TITLE_SHADOW = (0, 80, 20)
        self.SUBTITLE_COLOR = (0, 220, 255)
        self.TEXT_COLOR = (230, 230, 230)
        self.SELECT_COLOR = (255, 255, 0)
        self.HINT_COLOR = (160, 160, 160)
        self.PANEL_BORDER = (0, 180, 220)
        self.PANEL_BG = (10, 15, 25)
        self.PANEL_HEADER = (255, 230, 80)
        self.KEY_LABEL_COLOR = (0, 255, 255)
        self.KEY_DESC_COLOR = (240, 240, 240)
        self.BAR_BG = (40, 40, 40)
        self.BAR_FILL = (0, 230, 100)
        self.BAR_BORDER = (200, 200, 200)
        self.SAMPLE_ACTIVE_COLOR = (255, 100, 255)
        
        # Fonts (Pygame default font ensures universal compatibility)
        self.font_title = pygame.font.Font(None, 52)
        self.font_subtitle = pygame.font.Font(None, 22)
        self.font_menu = pygame.font.Font(None, 26)
        self.font_small = pygame.font.Font(None, 20)
        self.font_ctrl_title = pygame.font.Font(None, 22)
        self.font_ctrl = pygame.font.Font(None, 20)
        
        # Clickable rects for mouse navigation
        self.item_rects = []
        self.vol_music_minus_rect = None
        self.vol_music_plus_rect = None
        self.vol_music_sample_rect = None
        self.vol_sfx_minus_rect = None
        self.vol_sfx_plus_rect = None
        self.vol_sfx_sample_rect = None
        self.last_press_time = 0
        self.last_press_button = ""

    def handle_event(self, event):
        """Handle a single pygame event. Returns action string or None."""
        if event.type == pygame.QUIT:
            return "QUIT"
        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "QUIT"
            
            # Arrow key / WASD navigation
            elif event.key in (pygame.K_UP, pygame.K_w):
                self.selected_index = (self.selected_index - 1) % 3
                sounds.play_nav_sound()
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.selected_index = (self.selected_index + 1) % 3
                sounds.play_nav_sound()
            
            # Number keys quick select
            elif event.key in (pygame.K_1, pygame.K_KP1):
                self.selected_index = 0
                return "START_GAME"
            elif event.key in (pygame.K_2, pygame.K_KP2):
                self.selected_index = 1
                self.play_music_sample()
            elif event.key in (pygame.K_3, pygame.K_KP3):
                self.selected_index = 2
                self.play_sfx_sample()
            
            # Left / Right volume adjustments
            elif event.key in (pygame.K_LEFT, pygame.K_a):
                self.last_press_time = pygame.time.get_ticks() + 180
                self.last_press_button = "minus"
                if self.selected_index == 1:
                    new_vol = round(max(0.0, sounds.get_music_volume() - 0.1), 1)
                    sounds.set_music_volume(new_vol)
                    sounds.play_nav_sound()
                    self.sample_active_until = pygame.time.get_ticks() + 1500
                    self.sample_type = "music"
                elif self.selected_index == 2:
                    new_vol = round(max(0.0, sounds.get_sfx_volume() - 0.1), 1)
                    sounds.set_sfx_volume(new_vol)
                    sounds.play_sfx_sample()
                    self.sample_active_until = pygame.time.get_ticks() + 1500
                    self.sample_type = "sfx"
            
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                self.last_press_time = pygame.time.get_ticks() + 180
                self.last_press_button = "plus"
                if self.selected_index == 1:
                    new_vol = round(min(1.0, sounds.get_music_volume() + 0.1), 1)
                    sounds.set_music_volume(new_vol)
                    sounds.play_nav_sound()
                    self.sample_active_until = pygame.time.get_ticks() + 1500
                    self.sample_type = "music"
                elif self.selected_index == 2:
                    new_vol = round(min(1.0, sounds.get_sfx_volume() + 0.1), 1)
                    sounds.set_sfx_volume(new_vol)
                    sounds.play_sfx_sample()
                    self.sample_active_until = pygame.time.get_ticks() + 1500
                    self.sample_type = "sfx"
            
            # Enter / Space to confirm / sample
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                if self.selected_index == 0:
                    return "START_GAME"
                elif self.selected_index == 1:
                    self.play_music_sample()
                    sounds.play_nav_sound()
                elif self.selected_index == 2:
                    self.play_sfx_sample()

        elif event.type == pygame.MOUSEMOTION:
            pos = event.pos
            for idx, r in enumerate(self.item_rects):
                if r.collidepoint(pos):
                    self.selected_index = idx

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos
            if len(self.item_rects) > 0 and self.item_rects[0].collidepoint(pos):
                self.selected_index = 0
                return "START_GAME"
            elif self.vol_music_minus_rect and self.vol_music_minus_rect.collidepoint(pos):
                self.selected_index = 1
                new_vol = round(max(0.0, sounds.get_music_volume() - 0.1), 1)
                sounds.set_music_volume(new_vol)
                sounds.play_nav_sound()
                self.last_press_time = pygame.time.get_ticks() + 180
                self.last_press_button = "minus"
                self.sample_active_until = pygame.time.get_ticks() + 1500
                self.sample_type = "music"
            elif self.vol_music_plus_rect and self.vol_music_plus_rect.collidepoint(pos):
                self.selected_index = 1
                new_vol = round(min(1.0, sounds.get_music_volume() + 0.1), 1)
                sounds.set_music_volume(new_vol)
                sounds.play_nav_sound()
                self.last_press_time = pygame.time.get_ticks() + 180
                self.last_press_button = "plus"
                self.sample_active_until = pygame.time.get_ticks() + 1500
                self.sample_type = "music"
            elif self.vol_music_sample_rect and self.vol_music_sample_rect.collidepoint(pos):
                self.selected_index = 1
                self.play_music_sample()
                sounds.play_nav_sound()
            elif self.vol_sfx_minus_rect and self.vol_sfx_minus_rect.collidepoint(pos):
                self.selected_index = 2
                new_vol = round(max(0.0, sounds.get_sfx_volume() - 0.1), 1)
                sounds.set_sfx_volume(new_vol)
                sounds.play_sfx_sample()
                self.last_press_time = pygame.time.get_ticks() + 180
                self.last_press_button = "minus"
                self.sample_active_until = pygame.time.get_ticks() + 1500
                self.sample_type = "sfx"
            elif self.vol_sfx_plus_rect and self.vol_sfx_plus_rect.collidepoint(pos):
                self.selected_index = 2
                new_vol = round(min(1.0, sounds.get_sfx_volume() + 0.1), 1)
                sounds.set_sfx_volume(new_vol)
                sounds.play_sfx_sample()
                self.last_press_time = pygame.time.get_ticks() + 180
                self.last_press_button = "plus"
                self.sample_active_until = pygame.time.get_ticks() + 1500
                self.sample_type = "sfx"
            elif self.vol_sfx_sample_rect and self.vol_sfx_sample_rect.collidepoint(pos):
                self.selected_index = 2
                self.play_sfx_sample()

        return None

    def play_music_sample(self):
        sounds.play_music_sample(duration_ms=3500)
        self.sample_active_until = pygame.time.get_ticks() + 2500
        self.sample_type = "music"

    def play_sfx_sample(self):
        sounds.play_sfx_sample("gun")
        self.sample_active_until = pygame.time.get_ticks() + 1500
        self.sample_type = "sfx"

    def draw(self, surface):
        """Draw the entire start menu with title, options, and key controls."""
        now = pygame.time.get_ticks()
        is_sample_active = now < self.sample_active_until
        
        surface.fill(self.BG_COLOR)
        sw, sh = surface.get_size()
        
        # 1. Header Title & Subtitle
        title_str = "P  Y  Z  E  R  K"
        title_shadow = self.font_title.render(title_str, True, self.TITLE_SHADOW)
        title_surf = self.font_title.render(title_str, True, self.TITLE_COLOR)
        title_rect = title_surf.get_rect(center=(sw // 2, 32))
        surface.blit(title_shadow, (title_rect.x + 2, title_rect.y + 2))
        surface.blit(title_surf, title_rect)
        
        sub_str = "INTRUDER ALERT! DESTROY THE ROBOTS - ESCAPE THE MAZE"
        sub_surf = self.font_subtitle.render(sub_str, True, self.SUBTITLE_COLOR)
        surface.blit(sub_surf, sub_surf.get_rect(center=(sw // 2, 64)))
        
        # Decorative top divider line
        pygame.draw.line(surface, (0, 100, 130), (40, 80), (sw - 40, 80), 1)
        
        # 2. Menu Items
        self.item_rects = []
        base_y = 100
        row_height = 40
        
        # Item 0: 1.0 START A GAME
        y0 = base_y
        is_sel_0 = (self.selected_index == 0)
        col_0 = self.SELECT_COLOR if is_sel_0 else self.TEXT_COLOR
        prefix_0 = "> " if is_sel_0 else "  "
        text_0 = self.font_menu.render(f"{prefix_0}1.0  START A GAME", True, col_0)
        r0 = surface.blit(text_0, (50, y0))
        self.item_rects.append(pygame.Rect(45, y0 - 4, 300, 32))
        if is_sel_0:
            prompt_0 = self.font_small.render("[Press ENTER to Play]", True, (0, 255, 200))
            surface.blit(prompt_0, (320, y0 + 4))

        # Item 1: 2.0 SET MUSIC VOLUME
        y1 = base_y + row_height
        is_sel_1 = (self.selected_index == 1)
        col_1 = self.SELECT_COLOR if is_sel_1 else self.TEXT_COLOR
        prefix_1 = "> " if is_sel_1 else "  "
        text_1 = self.font_menu.render(f"{prefix_1}2.0  SET MUSIC VOLUME", True, col_1)
        surface.blit(text_1, (50, y1))
        self.item_rects.append(pygame.Rect(45, y1 - 4, 310, 32))
        
        # Music Volume Slider & Buttons
        music_vol = sounds.get_music_volume()
        self.vol_music_minus_rect, self.vol_music_plus_rect, self.vol_music_sample_rect = \
            self._draw_volume_control(surface, 360, y1 + 2, music_vol, is_sel_1,
                                     is_sample_active and self.sample_type == "music", "music")

        # Item 2: 3.0 SET OTHER SOUNDS VOLUME
        y2 = base_y + row_height * 2
        is_sel_2 = (self.selected_index == 2)
        col_2 = self.SELECT_COLOR if is_sel_2 else self.TEXT_COLOR
        prefix_2 = "> " if is_sel_2 else "  "
        text_2 = self.font_menu.render(f"{prefix_2}3.0  SET OTHER SOUNDS VOLUME", True, col_2)
        surface.blit(text_2, (50, y2))
        self.item_rects.append(pygame.Rect(45, y2 - 4, 310, 32))
        
        # SFX Volume Slider & Buttons
        sfx_vol = sounds.get_sfx_volume()
        self.vol_sfx_minus_rect, self.vol_sfx_plus_rect, self.vol_sfx_sample_rect = \
            self._draw_volume_control(surface, 360, y2 + 2, sfx_vol, is_sel_2,
                                     is_sample_active and self.sample_type == "sfx", "sfx")

        # Menu navigation hint
        nav_hint = "NAVIGATE: UP/DOWN | ADJUST: LEFT/RIGHT | SELECT / SAMPLE: ENTER | QUICK: 1, 2, 3"
        hint_surf = self.font_small.render(nav_hint, True, self.HINT_COLOR)
        surface.blit(hint_surf, hint_surf.get_rect(center=(sw // 2, 230)))

        # 3. Key Controls Panel
        self._draw_controls_panel(surface, 40, 248, sw - 80, 222)

    def _draw_volume_control(self, surface, x, y, volume, is_selected, is_sampling, vol_type):
        """Draw interactive volume bar, percentage, -/+ buttons, and sample button."""
        now = pygame.time.get_ticks()
        is_minus_pressed = is_selected and (now < self.last_press_time) and (self.last_press_button == "minus")
        is_plus_pressed = is_selected and (now < self.last_press_time) and (self.last_press_button == "plus")
        
        bar_w = 120
        bar_h = 16
        
        # Minus Button [ < ]
        minus_rect = pygame.Rect(x, y, 24, bar_h)
        m_bg = (255, 255, 0) if is_minus_pressed else ((60, 60, 80) if is_selected else (45, 45, 45))
        m_border = (255, 255, 0) if is_selected else (140, 140, 140)
        m_fg = (0, 0, 0) if is_minus_pressed else ((255, 255, 255) if is_selected else (200, 200, 200))
        pygame.draw.rect(surface, m_bg, minus_rect)
        pygame.draw.rect(surface, m_border, minus_rect, 1)
        m_txt = self.font_small.render("<", True, m_fg)
        surface.blit(m_txt, m_txt.get_rect(center=minus_rect.center))
        
        # Bar background & fill
        bar_x = x + 30
        bar_rect = pygame.Rect(bar_x, y, bar_w, bar_h)
        pygame.draw.rect(surface, self.BAR_BG, bar_rect)
        
        fill_w = int(bar_w * max(0.0, min(1.0, volume)))
        if fill_w > 0:
            fill_rect = pygame.Rect(bar_x, y, fill_w, bar_h)
            fill_color = (0, 255, 120) if is_selected else self.BAR_FILL
            pygame.draw.rect(surface, fill_color, fill_rect)
            
        # Draw segment notch ticks (every 10%)
        for i in range(1, 10):
            notch_x = bar_x + int(bar_w * (i / 10.0))
            pygame.draw.line(surface, (20, 20, 20), (notch_x, y), (notch_x, y + bar_h - 1), 1)
        bar_border_color = (255, 255, 0) if is_selected else self.BAR_BORDER
        pygame.draw.rect(surface, bar_border_color, bar_rect, 1)
        
        # Plus Button [ > ]
        plus_x = bar_x + bar_w + 6
        plus_rect = pygame.Rect(plus_x, y, 24, bar_h)
        p_bg = (255, 255, 0) if is_plus_pressed else ((60, 60, 80) if is_selected else (45, 45, 45))
        p_border = (255, 255, 0) if is_selected else (140, 140, 140)
        p_fg = (0, 0, 0) if is_plus_pressed else ((255, 255, 255) if is_selected else (200, 200, 200))
        pygame.draw.rect(surface, p_bg, plus_rect)
        pygame.draw.rect(surface, p_border, plus_rect, 1)
        p_txt = self.font_small.render(">", True, p_fg)
        surface.blit(p_txt, p_txt.get_rect(center=plus_rect.center))
        
        # Percentage text
        pct_str = f"{int(round(volume * 100))}%"
        if volume <= 0.001:
            pct_str = "OFF"
        pct_color = (255, 255, 0) if is_selected else (240, 240, 240)
        pct_surf = self.font_small.render(pct_str, True, pct_color)
        surface.blit(pct_surf, (plus_x + 30, y + 1))
        
        # Sample Button [SAMPLE]
        sample_x = plus_x + 72
        sample_rect = pygame.Rect(sample_x, y, 110, bar_h)
        btn_bg = (90, 20, 80) if is_sampling else ((50, 50, 70) if is_selected else (35, 35, 45))
        btn_border = self.SAMPLE_ACTIVE_COLOR if is_sampling else ((255, 255, 0) if is_selected else (120, 120, 140))
        pygame.draw.rect(surface, btn_bg, sample_rect)
        pygame.draw.rect(surface, btn_border, sample_rect, 1)
        
        if is_sampling:
            s_label = "* PLAYING... *"
            s_color = self.SAMPLE_ACTIVE_COLOR
        else:
            s_label = "[ENTER: Sample]" if is_selected else "TEST SAMPLE"
            s_color = (255, 255, 200) if is_selected else (200, 200, 200)
        sample_txt = self.font_small.render(s_label, True, s_color)
        surface.blit(sample_txt, sample_txt.get_rect(center=sample_rect.center))
        
        return minus_rect, plus_rect, sample_rect

    def _draw_controls_panel(self, surface, x, y, w, h):
        """Draw a retro arcade panel explaining all key controls clearly."""
        # Panel background and double border
        panel_rect = pygame.Rect(x, y, w, h)
        pygame.draw.rect(surface, self.PANEL_BG, panel_rect)
        pygame.draw.rect(surface, self.PANEL_BORDER, panel_rect, 2)
        pygame.draw.rect(surface, (0, 70, 100), pygame.Rect(x + 3, y + 3, w - 6, h - 6), 1)
        
        # Header banner
        header_surf = self.font_ctrl_title.render("=== KEY CONTROLS & HOW TO PLAY ===", True, self.PANEL_HEADER)
        surface.blit(header_surf, header_surf.get_rect(center=(x + w // 2, y + 16)))
        pygame.draw.line(surface, (0, 120, 160), (x + 20, y + 28), (x + w - 20, y + 28), 1)
        
        # Control lines
        controls = [
            ("ARROW KEYS:", "Move / Run character in 8 directions (Up, Down, Left, Right, Diagonals)"),
            ("LEFT CTRL:",  "HOLD Left Ctrl + Arrow Keys to aim laser gun and shoot"),
            ("LIVES SYSTEM:", "Start with 3 lives. Pass every 10 levels to earn +1 extra life!"),
            ("ENTER KEY:",  "Return back to Main Menu anytime during gameplay"),
            ("MENU KEYS:",  "UP/DOWN = Select option | LEFT/RIGHT = Volume | ENTER = Confirm / Sample"),
            ("OBJECTIVE:",  "Eliminate all robots or reach maze exits! Beware of bouncing OTTO!")
        ]
        
        line_y = y + 36
        for key_label, desc in controls:
            lbl_surf = self.font_ctrl.render(key_label, True, self.KEY_LABEL_COLOR)
            desc_surf = self.font_ctrl.render(desc, True, self.KEY_DESC_COLOR)
            surface.blit(lbl_surf, (x + 20, line_y))
            surface.blit(desc_surf, (x + 135, line_y))
            line_y += 28
