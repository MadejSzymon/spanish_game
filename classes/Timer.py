import pygame


class Timer(pygame.sprite.Sprite):

    def __init__(self, word_limit):
        super().__init__()
        self.start_time = 0
        self.word_limit = word_limit
        self.time_left = self.word_limit
        self.too_late = False
        self.current_time = 0

    def count_time(self):
        self.current_time = pygame.time.get_ticks() / 1000 - self.start_time
        self.too_late = False
        if self.current_time > self.word_limit:
            self.too_late = True
            self.start_time += self.current_time
        self.time_left = self.word_limit - self.current_time

    def reset_timer(self):
        self.current_time = pygame.time.get_ticks() / 1000 - self.start_time
        self.start_time += self.current_time
