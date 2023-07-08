import pygame_gui
import pygame


class Button(pygame_gui.elements.UIButton):
    def __init__(self, object_id, manager, pos, size, text):
        super().__init__(relative_rect=pygame.Rect(pos, size), text=text, object_id=object_id)
        self.manager = manager
