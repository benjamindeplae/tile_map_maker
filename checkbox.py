import bisect
from settings import *


class Checkbox:
	def __init__(self, game, x, y, layer_number):
		self.game = game
		self.rect = pygame.Rect(x, y, 30, 30)
		self.offset_rect = self.rect.copy()
		self.is_on = False
		self.layer_number = layer_number

	def draw(self):
		if self.offset_rect.collidepoint(self.game.mouse_pos):
			if not self.game.enable_hand:
				self.game.enable_hand_cursor()
			if self.game.key_down_1 and self.game.first_key_down_1:
				if self.is_on:
					if len(self.game.active_layers) > 1:
						self.is_on = False
						self.game.active_layers.remove(self.layer_number)
				else:
					self.is_on = True
					bisect.insort(self.game.active_layers, self.layer_number)

		pygame.draw.rect(self.game.screen, WHITE, self.offset_rect)
		if self.is_on:
			pygame.draw.line(self.game.screen, BLACK, self.offset_rect.bottomleft, self.offset_rect.topright, 2)
			pygame.draw.line(self.game.screen, BLACK, self.offset_rect.topleft, self.offset_rect.bottomright, 2)
