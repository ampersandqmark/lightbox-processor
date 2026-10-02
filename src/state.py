from dataclasses import dataclass
from processor import ImageProcessor

@dataclass
class ProcessingParams:
    num_layers: int
    contrast: float
    g_blur: float
    process: str
    clip_limit: float
    tile_grid_size: tuple

class ModelState:
    def __init__(self):
        self.image_path = None
        self.preview_pil = None # store processed image
        self.layers = []  # Stores PIL images of processed layers in-memory
        self.current_layer = -1
        self.new_image = False

        self.parameters = ProcessingParams(
            num_layers = 6,
            contrast = 0.0,
            g_blur = 0.0,
            process = "CLAHE",
            clip_limit = 3.0,
            tile_grid_size = (8,8)
        )
    
    def get_params(self, app) -> ProcessingParams:
        """Reads current state of all UI elements into a single dataclass."""
        grid_size = int(app.slider_grid.val)
        return ProcessingParams(
            num_layers=int(app.slider_layer.val),
            contrast=float(app.slider_contrast.val),
            g_blur=float(app.slider_blur.val),
            process="CLAHE" if app.tick_process.checked else "None",
            clip_limit=float(app.slider_clip.val),
            tile_grid_size=(grid_size, grid_size)
        )
    
    def pre_process_image(self, new_image_path=None):
        """Get the necessary arguments and pass to the main processor. returns processed image data"""
        if new_image_path:
            self.image_path = new_image_path

        if self.image_path is None:
            return

        # num_layers: int
        # contrast: float
        # g_blur: float
        # process: str
        # clip_limit: float
        # tile_grid_size: tuple
        parameters = self.parameters

        self.preview_pil, self.layers = ImageProcessor.process_image(
            self.image_path, 
            num_layers=parameters.num_layers, 
            contrast=parameters.contrast, 
            g_blur=parameters.g_blur, 
            process=parameters.process,
            clip_limit=parameters.clip_limit, 
            tile_grid_size=parameters.tile_grid_size
        )

        self.new_image = True
        # print("Image successfully processed.")
    
    def get_current_display_image(self):
        """Returns the PIL image that should currently be rendered."""
        if self.current_layer == -1 or not self.layers:
            return self.preview_pil
        return self.layers[self.current_layer]

    def save_layers(self):
        if not self.layers:
            print("No image processed yet. Please import an image first.")
            return

        self.preview_pil.save(f"posterize_preview.png")
        print(f"Saved posterized preview")
        for i, layer_img in enumerate(self.layers):
            layer_filename = f"layer_{i+1}.png"
            layer_img.save(layer_filename)
            print(f"Saved {layer_filename} (Layer {i+1} of {len(self.layers)})")
        print("\nAll layers saved successfully!")