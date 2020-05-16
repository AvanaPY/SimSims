import pygame
from .resource import Resource, Food, Product, Worker
import math
import time
import threading
import random

class Place:
    def __init__(self, name, uses, produces):
        self._name = name
        self._resources = []
        self._ingoing_connections = []
        self._outgoing_connections = []
        self._position = (0, 0)
        self._working = False
        self._uses = uses
        self._produces = produces
    @property
    def name(self):
        return self._name
    @property
    def position(self):
        return self._position

    def uses(self, t):
        return t in self._uses
    
    def produces(self, t):
        if self._produces:
            return t in self._produces
        return False

    def has_required_connections(self):
        for t in self._uses:
            uses = False
            for place in self._ingoing_connections:
                if place.produces(t):
                    uses = True
            if not uses:
                return False
        for t in self._produces:
            produces = False
            for place in self._outgoing_connections:
                if place.uses(t):
                    produces = True
            if not produces:
                return False
        return True

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
        """
            Returns a blit of the object.
        """
        return None

    def connection_points(self):
        """
            Returns a list of pairs of coordinates of outgoing connections
        """
        pairs = []
        w, h = self.dims()
        x, y = self.position[0] + w / 2, self.position[1] + h / 2
        for place in self._outgoing_connections:
            con_x, con_y = place.position[0] + place.dims()[0] / 2, place.position[1] + place.dims()[1] / 2
            pairs.append(((x, y), (con_x, con_y)))
        return pairs

    ## SimSims
    def _count_resources(self, types):
        if isinstance(types, (list, tuple)):
            ret = []
            for t in types:
                ret.append(sum([isinstance(o, t) for o in self._resources]))
            return ret
        return self._count_resources([types])

    def connect_place(self, place):
        """
            Full wrapper for connect_ingoing and connect_outgoing that connects both places.
        """
        if self == place:
            return
        self.connect_outgoing(place)
        place.connect_ingoing(self)

    def connect_ingoing(self, place):
        """
            Adds a place to the ingoing connections.
        """ 
        if not place in self._ingoing_connections:
            self._ingoing_connections.append(place)

    def connect_outgoing(self, place):
        """
            Adds a place to the outgoing connections.
        """ 
        if not place in self._outgoing_connections:
            self._outgoing_connections.append(place)

    def insert(self, r: Resource):
        """
            Inserts an object, it's a virtual method. Returns True of False depending on if it could insert the object or not.
        """
        return False

    def update(self):
        pass

####################
#       NODES
####################
class Node(Place):
    def __init__(self, name, uses, produces, dims=(60, 60), background=(255, 255, 255), border=(0, 0, 0)):
        super().__init__(name, uses, produces)
        self._dims = dims
        self._background = background
        self._border = border

    def blit(self):
        surface = pygame.Surface(self._dims, pygame.SRCALPHA).convert_alpha()
        surface.fill(self._background)
        pygame.draw.rect(surface, (self._border), pygame.Rect(0, 0, self._dims[0], self._dims[1]), 1)

        x, y = self._dims[0] // 2, self._dims[1] // 2
        has_connections_colour = (0, 200, 0) if self.has_required_connections() else (200, 0, 0)
        pygame.draw.circle(surface, has_connections_colour, (x, y), x // 2, 0)

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
        if not self._working:
            if self.get_resources():
                thread = threading.Thread(target=self.use_resources)
                thread.setDaemon(True)
                thread.start()

    def get_resources(self):
        return False
    def use_resources(self):
        pass
    def deliver_resource(self, r):
        for place in self._outgoing_connections:
            if place.uses(type(r)) and place.insert(r):
                self._resources.remove(r)
                return True
        return False
        
class Factory(Node):
    def __init__(self):
        super().__init__('Factory', (Worker,), (Worker, Product,))
        self._viability_diff = 0.1
        self._chance_of_accident = 0.05

    def random_accident(self):
        return random.random() < self._chance_of_accident

    def use_resources(self, delay=2):
        self._working = True

        time.sleep(delay/3)
        for r in self._resources[:]:
            if type(r) == Worker:
                self._resources.append(Product())

        time.sleep(delay/3)
        for resource in self._resources[:]:  # Copy the list to avoid issues
            t = type(resource)
            if t == Product:
                self.deliver_resource(resource)
            elif t == Worker:
                if self.random_accident() or resource.damage(self._viability_diff):
                    self._resources.remove(resource)
                else:
                    self.deliver_resource(resource)

        time.sleep(delay/3)
        self._working = False

    def get_resources(self):
        if len(self._resources) == 0:
            for place in self._ingoing_connections:
                if isinstance(place, Container) and place.place_resource(self):
                    break
        return self._count_resources(Worker)[0] > 0

    def insert(self, r: Resource):
        if isinstance(r, Worker):
            self._resources.append(r)
            return True
        return False

class Field(Node):
    def __init__(self):
        super().__init__('Field', (Worker,), (Worker, Food,))
        self._chance_of_accident = 0.05

    def random_accident(self):
        return random.random() < self._chance_of_accident

    def use_resources(self, delay=1):
        self._working = True
        time.sleep(delay/3)
        for r in self._resources[:]:
            if type(r) == Worker:
                self._resources.append(Food())
        time.sleep(delay/3)

        for resource in self._resources[:]:  # Copy the list to avoid issues
            t = type(resource)
            if t == Food:
                self.deliver_resource(resource)
            elif t == Worker:
                if self.random_accident():
                    self._resources.remove(resource)
                else:
                    self.deliver_resource(resource)

        time.sleep(delay/3)
        self._working = False

    def get_resources(self):
        if len(self._resources) == 0:
            for place in self._ingoing_connections:
                if isinstance(place, Container) and place.place_resource(self):
                    break
        return self._count_resources(Worker)[0] > 0

    def insert(self, r: Resource):
        if isinstance(r, Worker):
            self._resources.append(r)
            return True
        return False

class Flat(Node):
    def __init__(self):
        super().__init__('Flat', (Worker, Product), (Worker, ))

    def use_resources(self, delay=1):
        self._working = True

        time.sleep(delay/3)
        workers = self._count_resources(Worker)[0]
        if workers == 2:
            self._resources.append(Worker())
        else:
            for resource in self._resources[:]:
                if type(resource) == Worker:
                    resource.restore_viability()
        for resource in self._resources:
            if type(resource) == Product:
                self._resources.remove(resource)

        time.sleep(delay/3)
        for resource in self._resources[:]:  # Copy the list to avoid issues
            if type(resource) == Worker:
                self.deliver_resource(resource)

        time.sleep(delay/3)
        self._working = False

    def get_resources(self):
        counts = self._count_resources((Product, Worker))
        count_sum = sum(counts)
        if counts[0] < 1:
            for place in self._ingoing_connections:
                if isinstance(place, Magazine) and place.place_resource(self):
                    break
        if counts[1] < 2:
            for place in self._ingoing_connections:
                if isinstance(place, Road) and place.place_resource(self):
                    break
        return counts[0] == 1 and counts[1] in (1, 2)

    def insert(self, r: Resource):
        if isinstance(r, (Worker, Product)):
            self._resources.append(r)
            return True
        return False

class Diner(Node):
    def __init__(self):
        super().__init__('Diner', (Worker, Food), (Worker, ))
        self._viability_increase = 0.1

    def use_resources(self, delay=1):
        self._working = True

        fed_workers = 0

        time.sleep(delay/2)
        workers = [r for r in self._resources if type(r) == Worker]
        food_count = min(self._count_resources((Food, Worker)))
        feed_index = 0
        for resource in self._resources[:]:  # Copy the list to avoid issues
            t = type(resource)
            if t == Food:
                if feed_index < food_count:
                    workers[feed_index].add_viability(self._viability_increase)
                    self._resources.remove(resource)
                    feed_index += 1
            elif t == Worker:
                self.deliver_resource(resource)

        time.sleep(delay/2)
        self._working = False

    def get_resources(self):
        counts = self._count_resources((Food, Worker))
        count_sum = sum(counts)
        if counts[0] == 0:
            for place in self._ingoing_connections:
                if isinstance(place, Barn) and place.place_resource(self):
                    break
        if counts[1] == 0:
            for place in self._ingoing_connections:
                if isinstance(place, Road) and place.place_resource(self):
                    break
        return counts[0] > 0 and counts[1] > 0

    def insert(self, r: Resource):
        if isinstance(r, (Worker, Food)):
            self._resources.append(r)
            return True
        return False

###################
#    CONTAINERS
###################
class Container(Place):
    def __init__(self, name, uses, produces, radius=40, background=(255, 255, 255), border=(0, 0, 0)):
        super().__init__(name, uses, produces)
        self._radius = radius
        self._dims = (round(radius*2.1), round(radius*2.1))
        self._background = background
        self._border = border
        self._uses = uses
        self._produces = produces
                
    def dims(self):
        return self._dims

    def blit(self):
        surface = pygame.Surface(self._dims, pygame.SRCALPHA).convert_alpha()
        x, y = (self._dims[0] // 2, self._dims[1] // 2)
        pygame.draw.circle(surface, self._background, (x, y), self._radius-2, 0)
        pygame.draw.circle(surface, self._border, (x, y), self._radius, 2)
        
        x, y = self._dims[0] // 2, self._dims[1] // 2
        has_connections_colour = (0, 200, 0) if self.has_required_connections() else (200, 0, 0)
        pygame.draw.circle(surface, has_connections_colour, (x, y), x // 2, 0)

        max_resources_per_round = 25
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

    def place_resource(self, node: Node):
        for resource in self._resources:
            if node.insert(resource):
                self._resources.remove(resource)
                return True
        return False

class Magazine(Container):
    def __init__(self):
        super().__init__('Magazine', (Product,), (Product,))

    def insert(self, r: Resource):
        if isinstance(r, Product):
            self._resources.append(r)
            return True
        return False

class Barn(Container):
    def __init__(self):
        super().__init__('Barn', (Food, ), (Food, ))

    def insert(self, r: Resource):
        if isinstance(r, Food):
            self._resources.append(r)
            return True
        return False
class Road(Container):
    def __init__(self):
        super().__init__('Road', (Worker,), (Worker,))

    def reduce_viability(self, worker):
        pass

    def insert(self, r: Resource):
        if isinstance(r, Worker):
            self._resources.append(r)
            return True
        return False