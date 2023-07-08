import pygame


class Text(pygame.sprite.Sprite):

    def __init__(self, text_color, text_pos, text):
        super().__init__()
        self.text = text
        self.text_color = text_color
        self.text_pos = text_pos

    def draw_text(self, font, screen):
        text_surf = font.render(self.text, False, self.text_color)
        text_rect = text_surf.get_rect(center=self.text_pos)
        screen.blit(text_surf, text_rect)
