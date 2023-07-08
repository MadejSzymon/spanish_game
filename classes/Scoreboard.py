import pygame


class Scoreboard(pygame.sprite.Sprite):

    def __init__(self, limit):
        super().__init__()
        self.score = 0
        self.overall = 0
        self.limit = limit

    def add_point(self, point_to_add):
        self.add_overall()
        self.score += point_to_add
        if self.score > self.limit:
            self.score = 0

    def lose_point(self):
        self.add_overall()
        self.score -= 1
        if self.score < 0:
            self.score = 0

    def add_overall(self):
        self.overall += 1

    def reset_score(self):
        self.overall = 0
        self.score = 0
