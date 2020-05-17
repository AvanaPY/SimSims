class UI:
    def __init__(self):
        self._buttons = []
        self._panels = []

    def __iter__(self):
        return self.Iterator(self._buttons + self._panels)

    @property
    def buttons(self):
        return self.Iterator(self._buttons)

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