import pygame

class InputBox:
    def __init__(self, surface: pygame.Surface, x: int, y: int, font_name: str, font_size: int, color: pygame.Color):
        self.font = pygame.font.SysFont(font_name, font_size)
        self.x = x
        self.y = y
        self.color = color
        self.surface = surface
        self.text = ""
        self.backspace_held_for = 0
        
    def track_key_presses(self, event: pygame.event.Event):
        """After if event.type == pygame.KEYDOWN:"""
        if event.key != pygame.K_BACKSPACE and event.key != pygame.K_RETURN:
            self.text += event.unicode

    def track_backspaces(self):
        """To be inside the game loop"""
        keys_down = pygame.key.get_pressed()
        if keys_down[pygame.K_BACKSPACE]:
            if (self.backspace_held_for == 0 or self.backspace_held_for >= 15):
                if keys_down[pygame.K_LCTRL] or keys_down[pygame.K_RCTRL]:
                    last_index = 0
                    for index, letter in reversed(list(enumerate(self.text))):
                        if index == len(self.text) - 1:
                            continue
                        if not letter.isalnum():
                            last_index = index
                            break
                    self.text = self.text[:last_index + (1 if last_index != 0 else 0)]
                elif keys_down[pygame.K_LALT] or keys_down[pygame.K_RALT]:
                    self.text = ""
                else:
                    self.text = self.text[:-1]
            self.backspace_held_for += 1
        else:
            self.backspace_held_for = 0

    def reset(self):
        self.text = ""

    def render(self):
        guess_surface = self.font.render(self.text, True, self.color)
        self.surface.blit(guess_surface, (self.x, self.y))

    def __str__(self):
        return self.text

    def __len__(self):
        return len(self.text)

    def __getitem__(self, key):
        return self.text[key]