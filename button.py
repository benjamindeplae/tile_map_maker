from settings import *


class Button:
	def __init__(self, game, x, y, image, scale):
		img_width, img_height = image.get_width(), image.get_height()
		if img_width < img_height:
			image = pygame.transform.scale(image, (int(TILE_WIDTH * (img_width / img_height) * scale), int(TILE_HEIGHT * scale))).convert_alpha()
		else:
			image = pygame.transform.scale(image, (int(TILE_WIDTH * scale), int(TILE_HEIGHT * (img_height / img_width) * scale))).convert_alpha()
		self.game = game
		self.image = image
		self.rect = self.image.get_rect()
		self.offset = [0, 0]
		if image.get_width() < TILE_WIDTH:
			self.offset[0] = (TILE_WIDTH - self.rect.width) / 2
			self.rect.width = TILE_WIDTH
		if image.get_height() < TILE_HEIGHT:
			self.offset[1] = (TILE_HEIGHT - self.rect.height) / 2
			self.rect.height = TILE_HEIGHT
		self.rect.topleft = (x, y)
		self.offset_rect = self.rect.copy()

	def draw(self):
		action = False

		if self.offset_rect.collidepoint(self.game.mouse_pos):
			if not self.game.enable_hand:
				self.game.enable_hand_cursor()
			if self.game.first_key_down_1:
				action = True

		self.game.screen.blit(self.image, (self.offset_rect.x + self.offset[0], self.offset_rect.y + self.offset[1]))

		return action

