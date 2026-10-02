import pygame
from state import ModelState
from ui import AppUI
from ui import ImagePicker

def main():
    state = ModelState()
    app = AppUI()
    ip = ImagePicker(parameters=state.parameters,process_image_function=state.pre_process_image)

    while True:
        action = app.handle_events()

        if action == "STOP":
            break

        elif action == "import":
            ip.parameters = state.get_params(app)
            ip.import_image()

        elif action == "save":
            state.save_layers()

        elif action == "change_val":
            state.parameters = state.get_params(app)
            state.pre_process_image()

        elif action == "up_layer":
            state.current_layer += 1
            if state.current_layer > len(state.layers) - 1:
                state.current_layer = -1

            img = state.get_current_display_image()

            label = (
                "Full Preview" if state.current_layer == -1
                else f"Layer {state.current_layer+1} of {len(state.layers)}"
            )

            app.update_preview_rect(img, label_text=label)


        if state.new_image:
            img = state.get_current_display_image()
            app.update_preview_rect(img)
            state.new_image = False

        app.render()

    pygame.quit()

if __name__ == "__main__":
    main()