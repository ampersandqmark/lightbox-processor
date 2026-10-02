import pygame
import threading
import utils
from tkinter import Tk, filedialog

BG_COLOR = (30, 30, 30)
PANEL_COLOR = (45, 45, 45)

IMAGE_PICKER_OPEN = False
NEW_IMAGE = False

class AppUI:
    def __init__(self):
        pygame.init()
        
        self.width, self.height = 1200, 800
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Tape Art Processor v.1.0")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 28)

        # Setup UI Elements
        self.btn_import = utils.Button(
            20, 30, 310, 50, "Import Image", 
            action="import", 
            font=self.font
        )
        self.slider_layer = utils.Slider(
            20, 130, 310, 20, "Layer Count", 
            3, 12, 6, v_type = "int", 
            action="change_val", 
            font=self.font
        )
        self.slider_contrast = utils.Slider(
            20, 200, 310, 20, "Contrast", 
            0, 50, 0, 
            action="change_val", 
            font=self.font
        )
        self.slider_blur = utils.Slider(
            20, 270, 310, 20, "Gaussian Blur", 
            0, 32, 0, 
            action="change_val", 
            font=self.font
        )
        self.tick_process = utils.Checkbox(
            20, 350, 30, 30, "CLAHE Processing", checked=True,
            action="change_val", 
            font=self.font, 
        )
        self.slider_clip = utils.Slider(
            20, 420, 310, 20, "CLAHE ClipLimit", 
            1.0, 10.0, 3.0, 
            action="change_val", 
            font=self.font
        )
        self.slider_grid = utils.Slider(
            20, 490, 310, 20, "CLAHE GridSize", 
            2, 32, 8, v_type ="int", 
            action="change_val", 
            font=self.font
        )
        self.btn_next = utils.Button(
            20, 560, 310, 50, "Full Preview",
            action="up_layer",
            font=self.font
        )
        self.btn_save = utils.Button(
            20, 720, 310, 50, "Save Layers", 
            action="save", 
            font=self.font
        )

        self.ui_elements = [
            self.btn_import,
            self.slider_layer,
            self.slider_contrast, 
            self.slider_blur, 
            self.tick_process,
            self.slider_clip, 
            self.slider_grid, 
            self.btn_next,
            self.btn_save
        ]

        # Viewport setup
        self.preview_rect = pygame.Rect(370, 20, 810, 760)
        self.preview_surface = None
    
    def update_preview_rect(self, img, label_text=None):
        if not img:
            return
        img = img.convert("RGB")

        raw_surface = pygame.image.fromstring(
            img.tobytes(), img.size, img.mode
        )
        
        self.preview_surface = pygame.transform.smoothscale(
            raw_surface, (self.preview_rect.width, self.preview_rect.height)
        )

        if label_text:
            self.btn_next.text = label_text

    def handle_events(self):
        global NEW_IMAGE
        if NEW_IMAGE:
            NEW_IMAGE = False
            pygame.event.clear() # Dump queue to wipe ghost clicks occurring during load

        # toggle clahe sliders
        self.slider_grid.is_active = (self.tick_process.val == "CLAHE")
        self.slider_clip.is_active = (self.tick_process.val == "CLAHE")

        # 2. Main Pygame Event Loop
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "STOP"
            
            # Disable UI component interactions whilst the dialog thread runs
            if IMAGE_PICKER_OPEN:
                continue
            
            for element in self.ui_elements:
                action = element.handle_event(event)
                if action:
                    return action
                
        return None

    def render(self):
        self.screen.fill(BG_COLOR)
        mouse_pos = pygame.mouse.get_pos()

        # Update hover states (only if dialog isn't blocking UI)
        if not IMAGE_PICKER_OPEN:
            for element in self.ui_elements:
                if isinstance(element, utils.Button):
                    element.check_hover(mouse_pos)
                if isinstance(element, utils.Checkbox):
                    element.check_hover(mouse_pos)

        # Draw Control Panel Side
        pygame.draw.rect(self.screen, PANEL_COLOR, (0, 0, 350, self.height))
        for element in self.ui_elements:
            element.draw(self.screen)

        # Draw Viewport Side
        pygame.draw.rect(self.screen, (20, 20, 20), self.preview_rect)
        
        if IMAGE_PICKER_OPEN:
            wait_text = self.font.render("Waiting for file selection or processing...", True, (150, 150, 250))
            self.screen.blit(wait_text, (self.preview_rect.centerx - 200, self.preview_rect.centery))
        elif self.preview_surface:
            self.screen.blit(self.preview_surface, self.preview_rect.topleft)
        else:
            empty_text = self.font.render("No Preview Available (Import an image)", True, (150, 150, 150))
            self.screen.blit(empty_text, (self.preview_rect.centerx - 180, self.preview_rect.centery))

        pygame.display.flip()
        self.clock.tick(60)


class ImagePicker:
    def __init__(
        self,
        parameters,
        process_image_function    
    ):
        self.parameters = parameters
        self.pre_process_image = process_image_function
    
    def _open_file_dialog_thread(self):
        """Runs the blocking Tkinter dialog and image processing in the background."""
        root = Tk()
        root.withdraw()
        root.attributes('-topmost', True)

        global IMAGE_PICKER_OPEN
        global NEW_IMAGE
        
        image_path = filedialog.askopenfilename(
            parent=root,
            title="Select an image",
            filetypes=[("Image Files", "*.jpg *.jpeg *.png *.bmp *.gif *.webp"), ("All Files", "*.*")]
        )
        root.destroy()
        
        if image_path:
            try:
                # print(f"Loading and processing: {image_path}")  
                # Store tuple for the main thread to convert into Pygame Surface safely
                # self._pending_image_data = self.pre_process_image(image_path)
                self.pre_process_image(new_image_path=image_path)
                NEW_IMAGE = True

            except Exception as e:
                print(f"Error processing image: {e}")
                
        IMAGE_PICKER_OPEN = False

    def import_image(self):
        """Spawns background thread instead of blocking the main thread."""
        global IMAGE_PICKER_OPEN

        if IMAGE_PICKER_OPEN:
            return  # Prevent multiple dialog instances
        
        IMAGE_PICKER_OPEN = True

        threading.Thread(target=self._open_file_dialog_thread, daemon=True).start()
