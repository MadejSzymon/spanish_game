import pygame_gui
import pygame


class Textbox(pygame_gui.elements.UITextEntryLine):

    def __init__(self, object_id, manager, pos, size):
        super().__init__(relative_rect=pygame.Rect(pos, size), object_id=object_id)
        self.manager = manager
