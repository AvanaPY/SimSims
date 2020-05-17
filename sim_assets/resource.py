import pygame
class Resource:
    def __init__(self, name, colour, dims=(8, 8)):
        self._name = name
        self._colour = colour
        self._dims = dims
    @property
    def name(self):
        return self._name
    def blit(self):
        """
            Returns a blit which is coloured based on the sub-classe's choice of colour.
        """
        surface = pygame.Surface(self._dims)
        surface.fill(self._colour)
        return surface

class Worker(Resource):
    """
        Worker class, indicated with the colour black.
    """
    def __init__(self):
        super().__init__('Worker', (0, 0, 0))
        self._viability = 1

    def restore_viability(self, viability=1):
        """
            Restores the worker's viability to a value. Might become useful?
        """
        self._viability = viability

    def add_viability(self, viability):
        """
            Adds a value to the worker's viability.
        """
        self._viability += viability

    def damage(self, viability):
        """
            Subtracts a value from the worker's viability.
        """
        self._viability -= viability
        return self._viability <= 0
    
class Food(Resource):
    """
        Food class, indicated with the colour Green.
    """
    def __init__(self):
        super().__init__('Food', (0, 255, 0))

class Product(Resource):
    """
        Product class, indicated with the colour Red.
    """
    def __init__(self):
        super().__init__('Product', (255, 0, 0))