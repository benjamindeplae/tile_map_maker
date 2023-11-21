from settings import *


class Scrollbar:
    def __init__(self, game):
        self.game = game
        self.small_rect = pygame.Rect(WIDTH - SCROLLBAR_WIDTH, 0, SCROLLBAR_WIDTH, (HEIGHT / self.game.height) * HEIGHT)
        self.long_rect = pygame.Rect(WIDTH - SCROLLBAR_WIDTH, 0, SCROLLBAR_WIDTH, HEIGHT)
        self.clicked = False
        self.first = True

    def draw(self):
        if self.small_rect.collidepoint(self.game.mouse_pos):
            if self.game.key_down_1 and self.game.first_key_down_1:
                self.clicked = True
                if self.first:
                    pygame.mouse.get_rel()  # Reset relative movement
                    self.first = False
        elif self.long_rect.collidepoint(self.game.mouse_pos):
            if self.game.key_down_1 and self.game.first_key_down_1:
                self.small_rect.y = self.game.mouse_pos[1] - self.small_rect.h // 2

        if not self.game.key_down_1:
            self.clicked = False
            self.first = True

        if self.clicked:
            rel = pygame.mouse.get_rel()[1]
            self.small_rect.y += rel

        if self.small_rect.y < 0:
            self.small_rect.y = 0
        elif self.small_rect.y + self.small_rect.h > HEIGHT:
            self.small_rect.y = HEIGHT - self.small_rect.h

        pygame.draw.rect(self.game.screen, LIGHT_GREY, self.long_rect)
        pygame.draw.rect(self.game.screen, MID_LIGHT_GREY, self.small_rect)
