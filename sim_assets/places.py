import pygame
from .resource import Resource, Food, Product, Worker

import math

class Place:
    def __init__(self, name):
        self._name = name
        self._resources = []
        self._ingoing_connections = []
        self._outgoing_connections = []
        self._position = (0, 0)

    @property
    def name(self):
        return self._name
    @property
    def position(self):
        return self._position
    
    def point_in_place(self, x, y):
        return False

    def set_position(self, pos):
        x, y = pos
        w, h = self.dims()
        pos = x - w / 2, y - h / 2
        self._position = pos

    def dims(self):
        return 0, 0

    def blit(self):
        return None

    ## SimSims
    def connect_place(self, place):
        self.connect_outgoing(place)
        place.connect_ingoing(self)

    def connect_ingoing(self, place):
        if not place in self._ingoing_connections:
            self._ingoing_connections.append(place)

    def connect_outgoing(self, place):
        if not place in self._outgoing_connections:
            self._outgoing_connections.append(place)

    def insert(self, r: Resource):
        pass

####################
#       NODES
####################
class Node(Place):
    def __init__(self, name, dims=(160, 160), background=(255, 255, 255), border=(0, 0, 0)):
        super().__init__(name)
        self._dims = dims
        self._background = background
        self._border = border
    
    def blit(self):
        surface = pygame.Surface(self._dims, pygame.SRCALPHA).convert_alpha()
        surface.fill(self._background)
        pygame.draw.rect(surface, (self._border), pygame.Rect(0, 0, self._dims[0], self._dims[1]), 1)

        offset = 5
        x, y = 0, 0
        for resource in self._resources:
            blit = resource.blit()
            w, h = blit.get_size()
            if x + w > self._dims[0]:
                y += h + offset
                x = 0
            elif y + h > self._dims[1]:
                break
            surface.blit(blit, (x + w / 2, y + h / 2))
            x += w + offset
        return surface

    def point_in_place(self, x, y):
        sx, sy = self.position
        w, h = self._dims
        if x < sx or x > sx + w or y < sy or y > sy + h:
            return False
        return True

    def dims(self):
        return self._dims

    def update(self):
        pass
    def use_resources(self):
        pass
    def get_resources(self):
        return False

class Factory(Node):
    def __init__(self):
        super().__init__('Factory')

    def reduce_viability(self, worker):
        pass

    def random_accident(self, worker):
        return False

    def use_resources(self):
        pass

    def get_resources(self):
        pass

    def update(self):
        pass

    def insert(self, r: Resource):
        if isinstance(r, Worker):
            self._resources.append(r)

class Field(Node):
    def __init__(self):
        super().__init__('Field')

    def random_accident(self, worker):
        return False

    def use_resources(self):
        pass

    def get_resources(self):
        pass

    def update(self):
        pass

    def insert(self, r: Resource):
        if isinstance(r, Worker):
            self._resources.append(r)
class Flat(Node):
    def __init__(self):
        super().__init__('Flat')

    def use_resources(self):
        pass

    def get_resources(self):
        pass

    def update(self):
        pass

    def insert(self, r: Resource):
        if isinstance(r, (Worker, Product)):
            self._resources.append(r)
class Diner(Node):
    def __init__(self):
        super().__init__('Diner')

    def use_resources(self):
        pass

    def get_resources(self):
        pass

    def update(self):
        pass

    def insert(self, r: Resource):
        if isinstance(r, (Worker, Food)):
            self._resources.append(r)

###################
#    CONTAINERS
###################
class Container(Place):
    def __init__(self, name, radius=40, background=(255, 255, 255), border=(0, 0, 0)):
        super().__init__(name)
        self._radius = radius
        self._dims = (round(radius*2.1), round(radius*2.1))
        self._background = background
        self._border = border

    def dims(self):
        return self._dims

    def blit(self):
        surface = pygame.Surface(self._dims, pygame.SRCALPHA).convert_alpha()
        x, y = (self._dims[0] // 2, self._dims[1] // 2)
        pygame.draw.circle(surface, self._background, (x, y), self._radius-2, 0)
        pygame.draw.circle(surface, self._border, (x, y), self._radius, 2)
        
        max_resources_per_round = 10
        resources_to_render = self._resources[:]  # Copy the array
        round_count = 1
        while len(resources_to_render) > 0:
            r = self._radius * (1 - 0.2 * round_count)
            angle = -math.pi / 2.
            angle_delta = 2 * math.pi / min(len(resources_to_render), max_resources_per_round)
            for resource in resources_to_render[:max_resources_per_round]:
                x, y = math.cos(angle) * r + self._dims[0] / 2, math.sin(angle) * r + self._dims[1] / 2
                blit = resource.blit()
                w, h = blit.get_size()
                surface.blit(blit, (x - w / 2, y - h / 2))
                resources_to_render.remove(resource)
                angle += angle_delta
            round_count += 1
            
        return surface
        
    def point_in_place(self, x, y):

        sx, sy = self.position
        w, h = self._dims
        if x < sx or x > sx + w or y < sy or y > sy + h:
            return False
        return True

    def insert(self):
        pass

    def place_resource(self, node: Node):
        pass

class Magazine(Container):
    def __init__(self):
        super().__init__('Magazine')

    def insert(self):
        pass

    def insert(self, r: Resource):
        if isinstance(r, Product):
            self._resources.append(r)
class Barn(Container):
    def __init__(self):
        super().__init__('Barn')

    def insert(self):
        pass

    def insert(self, r: Resource):
        if isinstance(r, Food):
            self._resources.append(r)
class Road(Container):
    def __init__(self):
        super().__init__('Road')

    def insert(self):
        pass

    def reduce_viability(self, worker):
        pass

    def insert(self, r: Resource):
        if isinstance(r, Worker):
            self._resources.append(r)