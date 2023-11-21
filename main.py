import itertools
import math
import os
import sys
import re
from tkinter import filedialog
from button import *
from checkbox import *
from scrollbar import *
from animation import *


class Game:
    def __init__(self):
        pygame.init()
        self.clock = pygame.time.Clock()
        self.delta_time = 1
        self.screen = pygame.display.set_mode(RES)
        icon = pygame.image.load('graphics/pokéball.png').convert_alpha()
        pygame.display.set_icon(icon)
        self.scroll_left = False
        self.scroll_right = False
        self.scroll_up = False
        self.scroll_down = False
        self.scroll = [0, 0]
        self.scroll_speed = SCROLL_SPEED
        self.first_key_down_1 = False
        self.key_down_1 = False
        self.key_down_3 = False
        self.s_pressed = False
        self.l_pressed = False
        self.item_map = []
        self.active_layers = []
        for i in range(LAYER_AMOUNT):
            self.item_map.append({})
        self.current_tile = 0

        self.texts = []
        self.checkboxes = []
        font = pygame.font.Font(None, 25)
        text = font.render("Layers on", True, WHITE)
        rect = text.get_rect()
        rect.topleft = (WIDTH - SIDE_PANEL_WIDTH + MARGIN, MARGIN)
        self.texts.append((text, rect, rect.copy()))
        font = pygame.font.Font(None, 20)
        column = 0
        self.height = MARGIN + 40
        for i in range(LAYER_AMOUNT):
            text = font.render(f'{i + 1}:', True, WHITE)
            rect = text.get_rect()
            rect.topleft = (WIDTH - SIDE_PANEL_WIDTH + MARGIN + SPACE_BETWEEN_CHECKBOX * column, self.height)
            checkbox = Checkbox(self, WIDTH - SIDE_PANEL_WIDTH + MARGIN + 20 + SPACE_BETWEEN_CHECKBOX * column, self.height, i)
            self.texts.append((text, rect, rect.copy()))
            self.checkboxes.append(checkbox)
            column += 1
            if column == CHECKBOX_COLUMN_WIDTH:
                column = 0
                self.height += 40
        if column % COLUMN_WIDTH != 0:
            self.height += 40
        self.height += MARGIN
        self.checkboxes[0].is_on = True
        self.active_layers.append(self.checkboxes[0].layer_number)

        column = 0
        self.tile_image = pygame.image.load('graphics/tiles.1.png').convert_alpha()
        self.sub_rects = self.read_from_file('test.txt')
        self.button_list = []
        self.img_list = []
        # Create a sprite group
        self.all_sprites = pygame.sprite.Group()
        for tuple_rect in self.sub_rects:
            if isinstance(tuple_rect, list):
                animation = Animation(tuple_rect[:-1], tuple_rect[-1], self)
                self.all_sprites.add(animation)
                self.img_list.append(animation)
                self.create_button(animation.image[0], column)
            else:
                img = self.tile_image.subsurface(pygame.Rect(tuple_rect['x'], tuple_rect['y'], tuple_rect['width'], tuple_rect['height'])).convert_alpha()
                scale_width = tuple_rect.get('scale_width', tuple_rect['width'])
                scale_height = tuple_rect.get('scale_height', tuple_rect['height'])
                img = pygame.transform.scale(img, (scale_width, scale_height)).convert_alpha()
                offset_x = tuple_rect.get('offset_x', 0)
                offset_y = tuple_rect.get('offset_y', 0)
                flip_x = tuple_rect.get('flip_x', False)
                flip_y = tuple_rect.get('flip_y', False)
                img = pygame.transform.flip(img, flip_x, flip_y).convert_alpha()
                self.img_list.append((img, (offset_x, offset_y)))
                self.create_button(img, column)

            column += 1
            if column == COLUMN_WIDTH:
                column = 0
                self.height += SPACE_BETWEEN_BUTTONS

        if column % COLUMN_WIDTH != 0:
            self.height += SPACE_BETWEEN_BUTTONS
        self.height += MARGIN

        self.transparent_rect = pygame.Surface((TILE_WIDTH, TILE_HEIGHT), pygame.SRCALPHA)
        self.transparent_rect.fill(TRANSPARENT_RED)

        self.scrollbar = Scrollbar(self)

        self.image_with_alpha = None
        # Set the transparency (alpha) level (0-255, 0 is fully transparent, 255 is fully opaque)
        self.alpha = 120  # You can adjust this value to control the transparency level
        self.create_transparent_current_tile()

        self.mouse_pos = pygame.mouse.get_pos()
        self.x, self.y = int((self.mouse_pos[0] + self.scroll[0]) // TILE_WIDTH), int((self.mouse_pos[1] + self.scroll[1]) // TILE_HEIGHT)

        self.enable_hand = False
        self.first_scroll = True
        self.enable_scroll_map = False
        self.scroll_map = False
        self.scroll_buttons = False
        self.drawing = False

        self.scroll_wheel_speed = SCROLL_WHEEL_SPEED

    def create_button(self, img, column):
        img_width, img_height = img.get_width(), img.get_height()
        if img_width < img_height:
            img = pygame.transform.scale(img, (TILE_WIDTH * (img_width / img_height), TILE_HEIGHT)).convert_alpha()
        else:
            img = pygame.transform.scale(img, (TILE_WIDTH, TILE_HEIGHT * (img_height / img_width))).convert_alpha()
        tile_button = Button(self, WIDTH - SIDE_PANEL_WIDTH + MARGIN + SPACE_BETWEEN_BUTTONS * column, self.height, img, 1)
        self.button_list.append(tile_button)

    @staticmethod
    def read_from_file(filename):
        result = []
        with open(filename, 'r') as file:
            for line in file:
                # Evaluate each line as a tuple and append to the result list
                result.append(eval(line.strip()))
        return result

    def check_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.scroll_left = True
                elif event.key == pygame.K_RIGHT:
                    self.scroll_right = True
                elif event.key == pygame.K_UP:
                    self.scroll_up = True
                elif event.key == pygame.K_DOWN:
                    self.scroll_down = True
                elif event.key == pygame.K_RSHIFT:
                    self.scroll_speed = 4
                elif event.key == pygame.K_LSHIFT:
                    self.enable_scroll_map = not self.enable_scroll_map

            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    self.scroll_left = False
                elif event.key == pygame.K_RIGHT:
                    self.scroll_right = False
                elif event.key == pygame.K_UP:
                    self.scroll_up = False
                elif event.key == pygame.K_DOWN:
                    self.scroll_down = False
                elif event.key == pygame.K_RSHIFT:
                    self.scroll_speed = 2

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.key_down_1 = True
                    self.first_key_down_1 = True
                if event.button == 3:
                    self.key_down_3 = True

                if WIDTH - SIDE_PANEL_WIDTH < pygame.mouse.get_pos()[0] < WIDTH - SCROLLBAR_WIDTH:
                    if event.button == 4:  # Scroll up
                        self.change_scrollbar_pos(self.scroll_wheel_speed * self.delta_time)
                    elif event.button == 5:  # Scroll down
                        self.change_scrollbar_pos(-self.scroll_wheel_speed * self.delta_time)

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.key_down_1 = False
                    self.first_scroll = True
                    self.scroll_map = False
                    self.scroll_buttons = False
                    self.drawing = False
                if event.button == 3:
                    self.key_down_3 = False

            keys = pygame.key.get_pressed()
            ctrl_pressed = False
            if not self.s_pressed and not self.l_pressed:
                if keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]:
                    ctrl_pressed = True

            self.s_pressed = (True if keys[pygame.K_s] else False)
            self.l_pressed = (True if keys[pygame.K_l] else False)

            if ctrl_pressed and self.s_pressed:
                self.open_save_dialog()
            elif ctrl_pressed and self.l_pressed:
                self.open_load_dialog()

    def update(self):
        self.delta_time = self.clock.tick()
        pygame.display.set_caption(f'{self.clock.get_fps() :.1f}')
        pygame.display.flip()

        self.mouse_pos = pygame.mouse.get_pos()
        self.x, self.y = int((self.mouse_pos[0] + self.scroll[0]) // TILE_WIDTH), int((self.mouse_pos[1] + self.scroll[1]) // TILE_HEIGHT)

        if self.scroll_left:
            self.scroll[0] -= 0.3 * self.scroll_speed * self.delta_time
        elif self.scroll_right:
            self.scroll[0] += 0.3 * self.scroll_speed * self.delta_time
        if self.scroll_up:
            self.scroll[1] -= 0.3 * self.scroll_speed * self.delta_time
        elif self.scroll_down:
            self.scroll[1] += 0.3 * self.scroll_speed * self.delta_time

        if self.key_down_1 and self.mouse_pos[0] < WIDTH - SIDE_PANEL_WIDTH:
            if not self.scroll_buttons and not self.enable_scroll_map and self.first_key_down_1:
                self.drawing = True
        if self.key_down_3 and self.mouse_pos[0] < WIDTH - SIDE_PANEL_WIDTH:
            self.remove_item(self.x, self.y)

        if self.drawing and self.mouse_pos[0] < WIDTH - SIDE_PANEL_WIDTH:
            if len(self.active_layers):
                if max(self.active_layers) == LAYER_AMOUNT:
                    self.add_item(self.x, self.y, 1)
                else:
                    self.add_item(self.x, self.y, self.current_tile)

        if WIDTH - SIDE_PANEL_WIDTH < self.mouse_pos[0] < WIDTH - SCROLLBAR_WIDTH:
            if self.key_down_1 and self.first_key_down_1:
                if not self.enable_hand:
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                    self.enable_hand = True
                self.scroll_buttons = True
        elif self.enable_scroll_map:
            if self.mouse_pos[0] < WIDTH - SIDE_PANEL_WIDTH:
                if self.key_down_1 and not self.scroll_buttons and self.first_key_down_1:
                    if not self.enable_hand:
                        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                        self.enable_hand = True
                    self.scroll_map = True

        if self.scroll_map or self.scroll_buttons:
            if self.first_scroll:
                pygame.mouse.get_rel()
                self.first_scroll = False
            if self.scroll_map:
                self.enable_hand_cursor()
                rel = pygame.mouse.get_rel()
                self.scroll[0] -= rel[0]
                self.scroll[1] -= rel[1]
            elif self.scroll_buttons:
                self.enable_hand_cursor()
                self.change_scrollbar_pos(pygame.mouse.get_rel()[1])

        # Update all sprites in the group
        self.all_sprites.update()

    def draw(self):
        # Clear the screen
        self.screen.fill('black')

        # Draw grid
        # Vertical lines
        scroll_x = math.fmod(self.scroll[0], TILE_WIDTH)
        for c in range(VISIBLE_TILE_AMOUNT_X):
            x_coord = c * TILE_WIDTH - scroll_x
            pygame.draw.line(self.screen, WHITE, (x_coord, 0), (x_coord, HEIGHT))

        scroll_y = math.fmod(self.scroll[1], TILE_HEIGHT)
        # Horizontals lines
        for r in range(VISIBLE_TILE_AMOUNT_Y):
            y_coord = r * TILE_HEIGHT - scroll_y
            pygame.draw.line(self.screen, WHITE, (0, y_coord), (WIDTH, y_coord))

        start_x = int(self.scroll[0] // TILE_WIDTH)
        start_y = int(self.scroll[1] // TILE_HEIGHT)
        end_x = start_x + VISIBLE_TILE_AMOUNT_X
        end_y = start_y + VISIBLE_TILE_AMOUNT_Y
        # add this 10 because some tiles are no tiles at all actually but big buildings, so they should also be drawn if the tile fels out the screen in a short radius.
        for i in self.active_layers:
            for y in range(start_y, end_y):
                for x in range(start_x, end_x):
                    if (x, y) in self.item_map[i]:
                        if i == LAYER_AMOUNT - 1:
                            pos = (x * TILE_WIDTH - self.scroll[0], y * TILE_HEIGHT - self.scroll[1])
                            self.screen.blit(self.transparent_rect, pos)
                        else:
                            index = self.item_map[i][(x, y)]
                            if isinstance(self.img_list[index], tuple):
                                pos = (x * TILE_WIDTH - self.scroll[0] + self.img_list[index][1][0], (y + 1) * TILE_HEIGHT - self.scroll[1] + self.img_list[index][1][1] - self.img_list[index][0].get_height())
                                self.screen.blit(self.img_list[index][0], pos)
                            else:
                                self.img_list[index].draw((x * TILE_WIDTH - self.scroll[0], (y + 1) * TILE_HEIGHT - self.scroll[1]))

        if self.mouse_pos[0] < WIDTH - SIDE_PANEL_WIDTH and not self.enable_scroll_map:
            if max(self.active_layers) == LAYER_AMOUNT - 1:
                pos = (self.x * TILE_WIDTH - self.scroll[0], self.y * TILE_HEIGHT - self.scroll[1])
                self.screen.blit(self.transparent_rect, pos)
            else:
                if isinstance(self.img_list[self.current_tile], tuple):
                    pos = (self.x * TILE_WIDTH - self.scroll[0] + self.img_list[self.current_tile][1][0], (self.y + 1) * TILE_HEIGHT - self.scroll[1] + self.img_list[self.current_tile][1][1] - self.img_list[self.current_tile][0].get_height())
                    self.screen.blit(self.image_with_alpha, pos)
                else:
                    pos = (self.x * TILE_WIDTH - self.scroll[0] + self.img_list[self.current_tile].image[1][0], (self.y + 1) * TILE_HEIGHT - self.scroll[1] + self.img_list[self.current_tile].image[1][1] - self.img_list[self.current_tile].image[0].get_height())
                    self.screen.blit(self.image_with_alpha, pos)

        pygame.draw.rect(self.screen, GREY, pygame.Rect(WIDTH - SIDE_PANEL_WIDTH, 0, SIDE_PANEL_WIDTH, HEIGHT))

        # Calculate scroll percentages
        scroll_percentage = self.scrollbar.small_rect.y / (HEIGHT - self.scrollbar.small_rect.h)
        scroll_offset = (scroll_percentage * (self.height - HEIGHT) if self.height > HEIGHT else 0)

        for (text, rect, offset_rect) in self.texts:
            offset_rect.y = rect.y - scroll_offset  # Adjust text position based on offset
            self.screen.blit(text, offset_rect)

        for checkbox in self.checkboxes:
            checkbox.offset_rect.y = checkbox.rect.y - scroll_offset  # Adjust checkbox position based on offset
            checkbox.draw()

        # draw button
        # and choose tile
        for button_count, button in enumerate(self.button_list):
            button.offset_rect.y = button.rect.y - scroll_offset  # Adjust button position based on offset
            if -TILE_HEIGHT <= button.offset_rect.y <= HEIGHT:
                if button.draw():
                    self.current_tile = button_count
                    self.create_transparent_current_tile()

        self.scrollbar.draw()

        if self.enable_hand:
            self.enable_hand = False
        else:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

        self.first_key_down_1 = False

    def enable_hand_cursor(self):
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        self.enable_hand = True

    def change_scrollbar_pos(self, change):
        scroll_percentage = self.scrollbar.small_rect.y / (HEIGHT - self.scrollbar.small_rect.h)
        scroll_offset = (scroll_percentage * (self.height - HEIGHT + MARGIN) if self.height > HEIGHT else 0)
        scroll_offset -= change
        scroll_percentage = min(max(0, scroll_offset / (self.height - HEIGHT + MARGIN)), 1)
        self.scrollbar.small_rect.y = scroll_percentage * (HEIGHT - self.scrollbar.small_rect.h)

    def create_transparent_current_tile(self):
        if isinstance(self.img_list[self.current_tile], tuple):
            image = self.img_list[self.current_tile][0]
            # Create a copy of the image with an alpha channel
            self.image_with_alpha = pygame.Surface(image.get_size(), pygame.SRCALPHA)
            self.image_with_alpha.blit(image, (0, 0))
            # Fill the entire surface with the desired alpha level
            self.image_with_alpha.fill((255, 255, 255, self.alpha), special_flags=pygame.BLEND_RGBA_MULT)
        else:
            image = self.img_list[self.current_tile].image[0]
            # Create a copy of the image with an alpha channel
            self.image_with_alpha = pygame.Surface(image.get_size(), pygame.SRCALPHA)
            self.image_with_alpha.blit(image, (0, 0))
            # Fill the entire surface with the desired alpha level
            self.image_with_alpha.fill((255, 255, 255, self.alpha), special_flags=pygame.BLEND_RGBA_MULT)

    def open_load_dialog(self):
        folder_path = filedialog.askdirectory(title="Select a folder containing saved files")
        if folder_path:
            self.item_map = self.load_files(folder_path)

            # Filter out empty dictionaries
            non_empty_item_map = [d for d in self.item_map if d]
            # Find the dictionary with the smallest (x, y) key
            if non_empty_item_map:
                smallest_dict = min(non_empty_item_map, key=lambda d: min(d.keys()))
                # Find the smallest (x, y) key within the smallest dictionary
                smallest_key = min(smallest_dict.keys())
                self.scroll = [smallest_key[0] * TILE_WIDTH, smallest_key[1] * TILE_HEIGHT]

    def load_files(self, folder_path):
        loaded_data = []
        pattern = r'^layer_(\d+)\.txt$'
        for filename in os.listdir(folder_path):
            if filename.endswith(".txt"):
                match = re.match(pattern, filename)
                if match:
                    file_path = os.path.join(folder_path, filename)
                    with open(file_path, "r") as file:
                        data = {}
                        for line in file:
                            key, value = line.strip().split(": ")
                            # Convert the string representation of a tuple to an actual tuple
                            key = tuple(map(int, key.strip('()').split(', ')))
                            data[key] = int(value)
                    index = self.extract_index_from_filename(filename)  # Extract the index from the filename
                    length = len(loaded_data)  # Get the current length of loaded_data
                    # Extend loaded_data with empty dictionaries to fill gaps if necessary
                    if length < index - 1:
                        loaded_data.extend([{}] * ((index - length) - 1))
                    # Insert the data dictionary at the specified index
                    loaded_data.insert(index, data)
        while len(loaded_data) < LAYER_AMOUNT:
            loaded_data.append({})
        return loaded_data

    def extract_index_from_filename(self, filename):
        match = re.search(r"(\d+)", filename)
        if match:
            return int(match.group(1))
        return None

    def open_save_dialog(self):
        folder_path = filedialog.askdirectory(title="Select a folder to save files")
        if folder_path:
            self.save_files(folder_path)

    def save_files(self, folder_path):
        folder_number = 1
        new_folder = os.path.join(folder_path, f"save{folder_number}")

        while os.path.exists(new_folder):
            folder_number += 1
            new_folder = os.path.join(folder_path, f"save{folder_number}")

        os.makedirs(new_folder, exist_ok=True)  # Create the new folder if it doesn't exist

        for idx, dictionary in enumerate(self.item_map, start=1):
            if len(dictionary):
                file_name = f"layer_{idx}.txt"
                file_path = os.path.join(new_folder, file_name)

                with open(file_path, "w") as file:
                    for key, value in dictionary.items():
                        file.write(f"{key}: {value}\n")

    def add_item(self, x, y, item):
        if len(self.active_layers):
            layer = max(self.active_layers)
            self.item_map[layer][(x, y)] = item

    def remove_item(self, x, y):
        if len(self.active_layers):
            layer = max(self.active_layers)
            if (x, y) in self.item_map[layer]:
                del self.item_map[layer][(x, y)]

    def run(self):
        while 1:
            self.check_events()
            self.update()
            self.draw()


if __name__ == '__main__':
    game = Game()
    game.run()
