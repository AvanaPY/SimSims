import pygame
class Resource:
    def __init__(self, name, colour, dims=(5, 5)):
        self._name = name
        self._colour = colour
        self._dims = dims
    @property
    def name(self):
        return self._name
    def blit(self):
        surface = pygame.Surface(self._dims)
        surface.fill(self._colour)
        return surface
class Worker(Resource):
    def __init__(self):
        super().__init__('Worker', (0, 0, 0))
        self._viability = 1

    def damage(self, viability):
        self._viability -= viability
    
class Food(Resource):
    def __init__(self):
        super().__init__('Food', (0, 255, 0))

class Product(Resource):
    def __init__(self):
        super().__init__('Product', (255, 0, 0))