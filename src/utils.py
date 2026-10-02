import pygame

TEXT_COLOR = (220, 220, 220)
BUTTON_COLOR = (70, 130, 180)
BUTTON_HOVER = (100, 150, 200)
SAVE_COLOR = (80, 170, 90)
SAVE_HOVER = (100, 200, 110)
SLIDER_BG = (20, 20, 20)
SLIDER_FG = (70, 130, 180)
SLIDER_GRAY = (130, 140, 180)

class Button:
    def __init__(
                self, 
                x, y, w, h, 
                text, 
                action=None, 
                font=None
            ):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.action = action
        self.is_hovered = False
        self.font = font

    def draw(self, surface):
        if self.action=="save":
            color = SAVE_HOVER if self.is_hovered else SAVE_COLOR
        else:
            color = BUTTON_HOVER if self.is_hovered else BUTTON_COLOR

        pygame.draw.rect(surface, color, self.rect, border_radius=5)
        text_surf = self.font.render(self.text, True, TEXT_COLOR)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_hovered and self.action:
                # print(f"[ACTION] Triggered: {self.action}")
                return self.action
        return None

class Checkbox:
    def __init__(
                self, 
                x, y, w, h, 
                text, 
                checked=False, 
                action=None, 
                font=None
            ):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.action = action
        self.is_hovered = False
        self.font = font
        self.checked = True
        self.val = "CLAHE"

    def draw(self, surface):
        inflate = 5 if self.is_hovered else 2
        
        # Draw the outer checkbox square
        pygame.draw.rect(surface, TEXT_COLOR, self.rect, border_radius=3)
        pygame.draw.rect(surface, BUTTON_COLOR, self.rect, inflate, border_radius=3) # Border outline

        # If checked, draw a smaller inner box or a checkmark indicator inside
        if self.checked:
            inner_rect = self.rect.inflate(-8, -8)
            pygame.draw.rect(surface, BUTTON_COLOR, inner_rect, border_radius=2)

        # Draw the label text next to the checkbox
        if self.font and self.text:
            text_surf = self.font.render(self.text, True, TEXT_COLOR)
            # Position text to the right of the checkbox box with some spacing
            text_rect = text_surf.get_rect(midleft=(self.rect.right + 10, self.rect.centery))
            surface.blit(text_surf, text_rect)

    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_hovered:
                # print("Ticked")
                self.checked = not self.checked
                self.val = "CLAHE" if self.checked else None
                return self.action
        return None

class Slider:
    def __init__(
                self, 
                x, y, w, h, 
                label, 
                min_val, 
                max_val, 
                start_val, 
                v_type=None, 
                action=None, 
                font=None
            ):
        self.rect = pygame.Rect(x, y, w, h)
        self.label = label
        self.action = action
        self.min_val = min_val
        self.max_val = max_val
        self.val = start_val
        self.v_type = v_type
        self.is_dragging = False
        self.font = font
        self.label_surf = self.font.render(f"{self.label}: {self.val:.1f}", True, TEXT_COLOR)
        self.is_active = True

    def draw(self, surface):
        surface.blit(self.label_surf, (self.rect.x, self.rect.y - 25))

        fill_color = SLIDER_FG if self.is_active else SLIDER_GRAY
        
        pygame.draw.rect(surface, SLIDER_BG, self.rect, border_radius=3)
        fill_width = int(((self.val - self.min_val) / (self.max_val - self.min_val)) * self.rect.width)
        fill_rect = pygame.Rect(self.rect.x, self.rect.y, fill_width, self.rect.height)
        pygame.draw.rect(surface, fill_color, fill_rect, border_radius=3)

    def handle_event(self, event):
        if not self.is_active:
            return None

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.is_dragging = True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1 and self.is_dragging == True:
            self.is_dragging = False
            # print(self.label, self.val)
            return self.action
        elif event.type == pygame.MOUSEMOTION:
            if self.is_dragging:
                rel_x = max(0, min(event.pos[0] - self.rect.x, self.rect.width))
                ratio = rel_x / self.rect.width
                self.val = self.min_val + ratio * (self.max_val - self.min_val)
                if self.v_type == "int": # snap values if int input
                    self.val = int(self.val)
                self.label_surf = self.font.render(f"{self.label}: {self.val:.1f}", True, TEXT_COLOR)
        return None