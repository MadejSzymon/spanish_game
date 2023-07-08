import pygame


class Light(pygame.sprite.Sprite):

    def __init__(self, light_size, path_to_on, path_to_off):
        super().__init__()
        self.light_index = 0
        image_on = pygame.image.load(path_to_on).convert_alpha()
        image_on = pygame.transform.scale(image_on, light_size)
        image_off = pygame.image.load(path_to_off).convert_alpha()
        image_off = pygame.transform.scale(image_off, light_size)
        self.light_images = [image_off, image_on]
        self.image = self.light_images[self.light_index]

    def update(self, screen, pos):
        self.image = self.light_images[self.light_index]
        screen.blit(self.image, pos)
