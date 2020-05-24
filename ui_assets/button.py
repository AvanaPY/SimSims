import pygame

class Button:
    """
        A button
    """
    def __init__(self, text: str, font: pygame.font.Font,
                position: tuple, dims: tuple, func, arg: list = None, keybinding=None,
                text_aa=True, text_colour: tuple = (255, 255, 255),
                background_colour: tuple = (40, 40, 40), border_colour: tuple = (0, 0, 0), border_width: int = 1,
                expand: bool = True, padx: int = 0, pady: int = 0, centered: bool = True, *args, **kwargs):
        self._text = text
        self._func = func
        self._args = arg
        # Create the text blit of the button
        txt_blit = font.render(text, text_aa, text_colour)
        txt_dims = (txt_blit.get_width(), txt_blit.get_height())

        # IF we want to expand, check if the text is bigger than the given dimensions
        if not expand:
            self._dims = dims
        else:
            self._dims = (max(txt_dims[0], dims[0]) + padx, max(txt_dims[1], dims[1]) + pady)

        # Create the final surface and apply the background colour and border
        blit = pygame.Surface(self._dims, pygame.SRCALPHA, 32).convert_alpha()
        blit.fill(background_colour)
        pygame.draw.rect(blit, border_colour, pygame.Rect(0, 0, self._dims[0], self._dims[1]), border_width)

        # Blit the text to it
        blit.blit(txt_blit, (self._dims[0] / 2 - txt_dims[0] / 2, self._dims[1] / 2 - txt_dims[1] / 2))

        self._blit = blit
        if centered:
            self._position = (position[0] - blit.get_width() / 2, position[1] - blit.get_height() / 2)
        else:
            self._position = position
        self._hidden = False

        self._keybinding = keybinding
    @property
    def blit(self):
        return self._blit

    @property
    def position(self):
        return self._position

    @property
    def hidden(self):
        return self._hidden

    @property
    def keybinding(self):
        return self._keybinding

    @property
    def dims(self):
        return self._dims

    def move(self, dx, dy):
        """
            Moves the button in both axis.
        """
        self._position = self.position[0] + dx, self.position[1] + dy

    def hide(self):
        """
            Hides the button.
        """
        self._hidden = True
    def unhide(self):
        """
            Unhides the button.
        """
        self._hidden = False

    def point(self, x, y):
        """
            Returns a boolean if a point (x, y) is contained inside the button, useful for checking if it's about to be clicked.
        """
        if self._hidden:
            return False
        if x < self._position[0] or x > self._position[0] + self._dims[0] or y < self._position[1] or y > self._position[1] + self._dims[1]:
            return False
        return True

    def call(self):
        """
            Method that clals the button's function.
        """
        if self._args:
            self._func(*self._args)
        else:
            self._func()