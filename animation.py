import pygame
from collections import deque
from settings import *


class Animation(pygame.sprite.Sprite):
    def __init__(self, image_rects, animation_time, game):
        super().__init__()
        self.game = game
        self.images = deque()
        for tuple_rect in image_rects:
            img = self.game.tile_image.subsurface(pygame.Rect(tuple_rect['x'], tuple_rect['y'], tuple_rect['width'], tuple_rect['height'])).convert_alpha()
            scale_width = tuple_rect.get('scale_width', tuple_rect['width'] * 4)
            scale_height = tuple_rect.get('scale_height', tuple_rect['height'] * 4)
            img = pygame.transform.scale(img, (scale_width, scale_height)).convert_alpha()
            offset_x = tuple_rect.get('offset_x', 0)
            offset_y = tuple_rect.get('offset_y', 0)
            flip_x = tuple_rect.get('flip_x', False)
            flip_y = tuple_rect.get('flip_y', False)
            img = pygame.transform.flip(img, flip_x, flip_y).convert_alpha()
            self.images.append((img, (offset_x, offset_y)))

        self.image = self.images[0]
        self.animation_time_prev = pygame.time.get_ticks()
        self.animation_trigger = False
        self.animation_time = animation_time

    def update(self):
        super().update()
        self.check_animation_time()
        self.animate(self.images)

    def animate(self, images):
        if self.animation_trigger:
            images.rotate(-1)
            self.image = images[0]
            self.game.create_transparent_current_tile()

    def check_animation_time(self):
        self.animation_trigger = False
        time_now = pygame.time.get_ticks()
        if time_now - self.animation_time_prev > self.animation_time:
            self.animation_time_prev = time_now
            self.animation_trigger = True

    def draw(self, pos):
        self.game.screen.blit(self.image[0], (pos[0] + self.image[1][0], pos[1] + self.image[1][1] - self.image[0].get_height()))
