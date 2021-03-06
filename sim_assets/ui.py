import pygame
class UI:
    def __init__(self):
        self._buttons = []
        self._panels = []

    def __iter__(self):
        return self.Iterator(self._buttons + self._panels)

    @property
    def buttons(self):
        btns = [b for b in self._buttons]
        for panel in self._panels:
            btns += panel.buttons
        return self.Iterator(btns)

    def add_panel(self, panel):
        """
            Adds a panel to the UI.        
        """
        self._panels.append(panel)

    def add_button(self, btn):
        """
            Adds a button object to the ui.
        """
        self._buttons.append(btn)

    class Iterator:
        """
            An iterator subclass for improved multithreading if necessary.
        """
        def __init__(self, data):
            self.data = data
            self.n = len(data)
            self.p = -1

        def __iter__(self):
            return self
        def __next__(self):
            self.p += 1
            if self.p < self.n:
                return self.data[self.p]
            raise StopIteration

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
        if border_width > 0:
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
        if self._hidden:
            return False
        if self._args:
            self._func(*self._args)
        else:
            self._func()
        return True

class Panel:
    """
        A panel that can contain things.
    """
    def __init__(self, position: tuple, dims: tuple,
                background_colour: tuple = (40, 40, 40), border_colour: tuple = (0, 0, 0), border_width: int = 3,
                content_offset=10, expand=True):
        self._content = []
        self._position = position
        self._dims = dims

        self._position = position
        self._hidden = False

        self._background_colour = background_colour
        self._border_colour = border_colour
        self._border_width = border_width

        self._content_offset = content_offset

        self._expand = expand
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

    @property
    def buttons(self):
        if self._hidden:
            return []
        else:
            return [b.content for b in self._content if type(b.content) == Button]

    def next_y(self):
        y = self._content_offset
        for content in self._content:
            y += content.get_height() + self._content_offset
        return y

    def add_text(self, text, font: pygame.font.Font, colour=(0, 0, 0), *args, **kwargs):
        """
            Adds text as content.
        """
        blit = font.render(text, True, colour)
        self._content.append(self.PanelContent(self._content_offset, self.next_y(), text, blit))
        self._redraw()

    def add_button(self, *args, **kwargs):
        """
            Adds a button as content.
        """
        x, y = 0, self.next_y()
        kwargs['position'] = x + self.position[0], y + self.position[1]
        kwargs['centered'] = False
        button = Button(*args, **kwargs)
        content = self.PanelContent(x, y, button, button.blit)
        self._content.append(content)
        self._redraw()

    def _redraw(self):
        """
            Redraws the blit.
        """
        self._calculate_width()
        self._blit = pygame.Surface(self._dims, pygame.SRCALPHA, 32).convert_alpha()
        self._blit.fill(self._background_colour)
        if self._border_width > 0:
            pygame.draw.rect(self._blit, self._border_colour, pygame.Rect(0, 0, *self.dims), self._border_width)

        for cont in self._content:
            self._blit.blit(cont.blit, cont.pos)

    def _calculate_width(self):
        """
            Calculates the maximum width in the content and assigns it to the dimensionality of the panel.
        """
        if self._content and self._expand:
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

    def clear(self):
        """
            Clears the content of the panel.
        """
        self._content.clear()
        self._redraw()

    class PanelContent:
        def __init__(self, x, y, content, blit):
            self.pos = (x, y)  # Position on screen
            self.blit = blit
            self.content = content  # Content to display
        def get_width(self):
            return self.blit.get_width()
        def get_height(self):
            return self.blit.get_height()