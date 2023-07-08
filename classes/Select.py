import pygame_gui
import pygame


class Select(pygame_gui.elements.UISelectionList):
    def __init__(self, object_id, manager, pos, size, item_list, default_selection):
        super().__init__(relative_rect=pygame.Rect(pos, size), object_id=object_id,
                         item_list=item_list, default_selection=default_selection)
        self.manager = manager
