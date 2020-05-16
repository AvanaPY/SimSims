class UI:
    def __init__(self):
        self._buttons = []

    def __iter__(self):
        return self.Iterator(self._buttons)

    @property
    def buttons(self):
        return self.Iterator(self._buttons)

    def add_button(self, btn):
        """
            Adds a button object to the ui.
        """
        self._buttons.append(btn)

    class Iterator:
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