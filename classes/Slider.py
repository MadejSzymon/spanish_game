import pygame_gui
import pygame


class Slider(pygame_gui.elements.UIHorizontalSlider):
    def __init__(self, object_id, manager, pos, size, start_value, value_range):
        super().__init__(relative_rect=pygame.Rect(pos, size), object_id=object_id,
                         start_value=start_value, value_range=value_range, click_increment=1)
        self.manager = manager
