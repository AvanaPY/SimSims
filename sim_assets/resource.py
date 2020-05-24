import pygame
class Resource:
    def __init__(self, *args, **kwargs):
        self._name = kwargs.get('name', 'Resource')
        self._colour = kwargs.get('colour', (0, 0, 0))
        self._dims = kwargs.get('dims', (8, 8))
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

    def json(self):
        json = {
            'type':self.__class__.__name__
        }
        json = {**json, **self.__dict__}
        json = {k.replace('_', ''): v for k, v in json.items()}
        for k in ('name', 'colour', 'dims'):
            json.pop(k, None)
        return json

    @staticmethod
    def from_json(json):
        type_map = {v.__name__:v for v in Resource.__subclasses__()}
        t = type_map[json['type']](**json)
        return t

class Worker(Resource):
    """
        Worker class, indicated with the colour black.
    """
    def __init__(self, *args, **kwargs):
        kwargs['colour'] = 0, 0, 0
        kwargs['name'] = self.__class__.__name__
        super().__init__(*args, **kwargs)
        self._viability = kwargs.get('viability', 1)
    @property
    def viability(self):
        return self._viability
    def restore_viability(self, viability=1):
        """
            Restores the worker's viability to a value. Might become useful?
        """
        self._viability = min(1, viability)

    def add_viability(self, viability):
        """
            Adds a value to the worker's viability.
        """
        self._viability += viability
        if self._viability > 1:
            self._viability = 1

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
    def __init__(self, *args, **kwargs):
        kwargs['colour'] = 0, 255, 0
        kwargs['name'] = self.__class__.__name__
        super().__init__(*args, **kwargs)

class Product(Resource):
    """
        Product class, indicated with the colour Red.
    """
    def __init__(self, *args, **kwargs):
        kwargs['colour'] = 255, 0, 0
        kwargs['name'] = self.__class__.__name__
        super().__init__(*args, **kwargs)