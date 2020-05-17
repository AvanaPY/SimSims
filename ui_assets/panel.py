import pygame

class Panel:
    """
        A panel that can contain things.
    """
    def __init__(self, position: tuple, dims: tuple, background_colour: tuple = (40, 40, 40, 100), border_colour: tuple = (0, 0, 0), border_width: int = 3,
                content_offset=5):
        self._content = []
        self._position = position
        self._dims = dims

        self._position = position
        self._hidden = False

        self._background_colour = background_colour
        self._border_colour = border_colour
        self._border_width = border_width

        self._content_offset = content_offset

        self._blit = None
        self._redraw()

    @property
    def blit(self):
        return self._blit

    @property
    def dims(self):
        return self._dims

    @property
    def position(self):
        return self._position

    @property
    def hidden(self):
        return self._hidden

    def add_text(self, text, font: pygame.font.Font, colour=(0, 0, 0)):
        """
            Adds text as content.
        """
        content = font.render(text, True, colour)
        self._content.append(content)
        self._redraw()

    def _redraw(self):
        """
            Redraws the blit.
        """
        self._calculate_width()
        self._blit = pygame.Surface(self._dims, pygame.SRCALPHA, 32).convert_alpha()
        self._blit.fill(self._background_colour)
        pygame.draw.rect(self._blit, self._border_colour, pygame.Rect(0, 0, *self.dims), self._border_width)

        x, y = self._content_offset, self._content_offset
        for cont in self._content:
            self._blit.blit(cont, (x, y))
            y += cont.get_height() + self._content_offset

    def _calculate_width(self):
        """
            Calculates the maximum width in the content and assigns it to the dimensionality of the panel.
        """
        if self._content:
            w = max([self._dims[0]] + [cont.get_width() + self._content_offset * 2 for cont in self._content])
            self._dims = w, self._dims[1]

    def move(self, dx, dy):
        """
            Moves the panel in both axis.
        """
        self._position = self.position[0] + dx, self.position[1] + dy

    def hide(self):
        """
            Hides the panel.
        """
        self._hidden = True
    def unhide(self):
        """
            Unhides the panel.
        """
        self._hidden = False