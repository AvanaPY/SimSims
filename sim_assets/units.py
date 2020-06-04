import pygame
import threading
import math
import time
import random
from .ext import map_from_to, colour_linear_interpolation, compute_bezier_points
# RESOURCES

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
        """
            Turns a resource into a .json dictionary.
        """
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
        """
            Static method that returns a resource from a .json dictionary.
        """
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

class Place:
    PLACE_COUNTER = 0
    def __init__(self, name, uses, produces, *args, **kwargs):
        self._name = name
        self._resources = []
        self._ingoing_connections = []
        self._outgoing_connections = []
        self._position = kwargs.get('position', (0, 0))
        self._working = False
        self._uses = uses
        self._produces = produces

        if kwargs.get('index', 0):
            self._index = kwargs.get('index')
        elif kwargs.get('set_index', True):
            self._index = Place.PLACE_COUNTER
            Place.PLACE_COUNTER += 1
        else:
            self._index = -1

        # Graphics
        self._background = kwargs.get('background', (255, 255, 255))
        self._border = kwargs.get('border', (0, 0, 0))
        self._dims = kwargs.get('dims', (90, 90))

    @property
    def name(self):
        return self._name
    @property
    def position(self):
        return self._position
    @property
    def index(self):
        return self._index
    @property
    def working(self):
        return self._working

    def set_index(self, i):
        self._index = i
    
    def uses(self, t):
        """
            Returns a boolean if this place uses a type.
        """
        return t in self._uses
    
    def produces(self, t):
        """
            Returns a boolean if this place produces a type.
        """
        if self._produces:
            return t in self._produces
        return False

    def has_required_connections(self):
        """
            Returns a boolean if this place has the required connections to operate properly.
        """
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
        """
            Returns if this place contains the point (x, y). This is a virtual method.
        """
        return False

    def set_position(self, pos):
        """
            Sets the position, keep in mind that the place is then centered on the position.
        """
        x, y = pos
        w, h = self.dims()
        pos = x - w / 2, y - h / 2
        self._position = pos

    def dims(self):
        """
            Returns a tuple containing the width and the height of the place.
        """
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
        """
            Counts each resource in types. Types can be of type Resource or a list of Resource types.

            If it's a list, it returns an identical list of counted types.

            If it's a type, it returns a list of size 1.
        """
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

    def disconnect_place(self, place):
        """
            Fully disconnects this place from another place.
        """
        if place in self._ingoing_connections:
            self._ingoing_connections.remove(place)
            place.disconnect_place(self)
        if place in self._outgoing_connections:
            self._outgoing_connections.remove(place)
            place.disconnect_place(self)

    def disconnect_all_connections(self):
        """
            Fully disconnects this place from all places it is connected to, both ingoing and outgoing connections.
        """
        for place in self._ingoing_connections[:] + self._outgoing_connections[:]:
            place.disconnect_place(self)

    def insert(self, r: Resource):
        """
            Inserts an object, it's a virtual method. Returns True of False depending on if it could insert the object or not.
        """
        return False

    def update(self):
        """
            Update loop, it's a virtual method.
        """
        pass

    def json(self):
        """
            Returns a json dictionary of this object.
        """
        index_in_connections = [c.index for c in self._ingoing_connections]
        index_ou_connections = [c.index for c in self._outgoing_connections]
        resource_count = [r.json() for r in self._resources]
        json = {
            'type': self.__class__.__name__,
            'in': index_in_connections,
            'out': index_ou_connections,
            'resources': resource_count
        }
        _dict = self.__dict__.copy()
        for k in ('_ingoing_connections', '_outgoing_connections', '_resources', '_thread_lock', '_produces', '_uses', '_name'):
            _dict.pop(k, None)
        json = {**json, **_dict}  # Merges the two dictionaries
        return json

    @staticmethod
    def from_json(json):
        """
            Returns a Place based on a json dictionary.
        """
        place = CLASS_NAME_MAP_DICT[json['type']](**json)
        for r_json in json['resources']:
            place.insert(Resource.from_json(r_json))
        return place
        
####################
#       NODES
####################
class Node(Place):
    def __init__(self, name, uses, produces, *args, **kwargs):
        super().__init__(name, uses, produces, *args, **kwargs)
        self._has_waiting_resources = kwargs.get('haswaitingresources', False)
        self._next_available = kwargs.get('nextavailable', 0)

    @property
    def waiting_resources(self):
        return self._has_waiting_resources

    def blit(self):
        # Create a surface
        surface = pygame.Surface(self._dims, pygame.SRCALPHA).convert_alpha()
        surface.fill(self._background)
        pygame.draw.rect(surface, (self._border), pygame.Rect(0, 0, self._dims[0], self._dims[1]), 1)
        
        # If we have all necessary connections we want to indicate this with a green circle inside the form
        # Else we want to indicate we are missing important connections by drawing a red circle inside the form
        # The radius of this circle will be half of the original circle.
        x, y = self._dims[0] // 2, self._dims[1] // 2
        has_connections_colour = (0, 200, 0) if self.has_required_connections() else (200, 0, 0)
        pygame.draw.circle(surface, has_connections_colour, (x, y), x // 2, 0)

        # Simply render them in a grid-like manner starting from the top-left
        offset = 5
        x, y = 0, 0
        for resource in self._resources:
            blit = resource.blit()
            w, h = blit.get_size()
            # If we reach the right edge, increase y and reset x
            if x + w > self._dims[0]:
                y += h + offset
                x = 0
            # If we reach the bottom, simply exit the loop, rendering any more resources would be a waste of time and would look bad
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
        if not self._working and not self._has_waiting_resources and self._next_available - time.time() < 0:
            if self.get_resources():
                thread = threading.Thread(target=self.use_resources, args=(1, ))
                thread.setDaemon(True)
                thread.start()

    def get_resources(self):
        return False
    def use_resources(self, delay=1):
        pass
    def give_resources(self, container):
        """
            If this Node has any resources waiting to be delivered, it will give any resources it can to the container. If a resource can't be given it will simply skip to the next one.
        """
        if self._has_waiting_resources:
            for resource in self._resources[:]:
                if container.uses(type(resource)):
                    container.insert(resource)
                    self._resources.remove(resource)
            self._has_waiting_resources = len(self._resources) != 0
            self._next_available = time.time() + 0.2

class Factory(Node):
    WORKER_DAMAGE = 0.1
    CHANCE_OF_ACCIDENT = 0.05
    def __init__(self, *args, **kwargs):
        super().__init__('Factory', (Worker,), (Worker, Product,), *args, **kwargs)

    def random_accident(self):
        return random.random() < self.CHANCE_OF_ACCIDENT

    def use_resources(self, delay=1):
        self._working = True

        worker = self._resources[0]
        viability_penalty = map_from_to(worker.viability, 0, 1, 2, 1)
        time.sleep(delay/2 * viability_penalty)
        for r in self._resources[:]:
            if type(r) == Worker:
                self._resources.append(Product())
                if self.random_accident() or r.damage(self.WORKER_DAMAGE):
                    self._resources.remove(r)

        time.sleep(delay/2)
        self._working = False
        self._has_waiting_resources = True

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
    CHANCE_OF_ACCIDENT = 0.05
    def __init__(self, *args, **kwargs):
        super().__init__('Field', (Worker,), (Worker, Food,), *args, **kwargs)

    def random_accident(self):
        return random.random() < self.CHANCE_OF_ACCIDENT

    def use_resources(self, delay=1):
        self._working = True
        
        worker = self._resources[0]
        viability_penalty = map_from_to(worker.viability, 0, 1, 2, 1)
        time.sleep(delay/2 * viability_penalty)
        for r in self._resources[:]:
            if type(r) == Worker:
                self._resources.append(Food())
                if self.random_accident():
                    self._resources.remove(r)

        time.sleep(delay/2)
        self._working = False
        self._has_waiting_resources = True

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
    VIABILITY_INCREASE = 0.25
    CHANCE_OF_TWO_WRKR = 0.4
    def __init__(self, *args, **kwargs):
        super().__init__('Flat', (Worker, Product), (Worker, ), *args, **kwargs)

    def use_resources(self, delay=1):
        self._working = True

        time.sleep(delay/2)
        workers = self._count_resources(Worker)[0]
        if workers == 2:
            self._resources.append(Worker())
        else:
            for resource in self._resources[:]:
                if type(resource) == Worker:
                    resource.add_viability(self.VIABILITY_INCREASE)
        self._resources = [r for r in self._resources if type(r) != Product]

        time.sleep(delay/2)
        self._working = False
        self._has_waiting_resources = True

    def get_resources(self):
        counts = self._count_resources((Product, Worker))
        count_sum = sum(counts)
        if counts[0] == 0:
            for place in self._ingoing_connections:
                if isinstance(place, Magazine) and place.place_resource(self):
                    break
        elif counts[1] == 0:
            for _ in range(2):
                for place in self._ingoing_connections:
                    if isinstance(place, Road) and place.place_resource(self):
                        break
                if random.random() > self.CHANCE_OF_TWO_WRKR or self._count_resources(Worker)[0] > 1:
                    break
        return counts[0] == 1 and counts[1] in (1, 2)

    def insert(self, r: Resource):
        if isinstance(r, (Worker, Product)):
            self._resources.append(r)
            return True
        return False

class Diner(Node):
    MAX_VIABILITY_INCREASE = 0.7
    MIN_VIABILITY_INCREASE = 0.2
    FOOD_POISON_CHANCE = 0.2
    FOOD_POISON_FACTOR = -0.5
    def __init__(self, *args, **kwargs):
        super().__init__('Diner', (Worker, Food), (Worker, ), *args, **kwargs)

    @property
    def viability(self):
        return (self.FOOD_POISON_FACTOR if random.random() < self.FOOD_POISON_CHANCE else 1) * random.uniform(self.MIN_VIABILITY_INCREASE, self.MAX_VIABILITY_INCREASE)

    def use_resources(self, delay=1):
        self._working = True

        time.sleep(delay/2)
        worker = [r for r in self._resources if type(r) == Worker][0]
        food = [r for r in self._resources if type(r) == Food][0]

        self._resources.remove(food)
        if worker.add_viability(self.viability):
            self._resources.remove(worker)

        time.sleep(delay/2)
        self._working = False
        self._has_waiting_resources = True

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
    def __init__(self, name, uses, produces, *args, **kwargs):
        self._radius = kwargs.get('radius', 60)
        kwargs['dims'] = (round(self._radius * 2.1), round(self._radius * 2.1))
        super().__init__(name, uses, produces, *args, **kwargs)
        self._thread_lock = threading.Lock()
                
    def dims(self):
        return self._dims

    def blit(self):
        # Create a surface, get the midpoint
        surface = pygame.Surface(self._dims, pygame.SRCALPHA).convert_alpha()
        x, y = (self._dims[0] // 2, self._dims[1] // 2)

        # Render two circles of slightly different radi to create a circle with an outline.
        pygame.draw.circle(surface, self._background, (x, y), self._radius-2, 0)
        pygame.draw.circle(surface, self._border, (x, y), self._radius, 2)
        
        x, y = self._dims[0] // 2, self._dims[1] // 2

        # If we have all necessary connections we want to indicate this with a green circle inside the form
        # Else we want to indicate we are missing important connections by drawing a red circle inside the form
        # The radius of this circle will be half of the original circle.
        has_connections_colour = (0, 200, 0) if self.has_required_connections() else (200, 0, 0)
        pygame.draw.circle(surface, has_connections_colour, (x, y), self._radius // 2, 0)

        # We're going to render them in a circle
        # So we want a maximum amount of resources to render per "loop" inside the circle
        max_resources_per_loop = 10

        # Manage how many loops around the circle we have done
        loop_counter = 1
        loop_radius_diff = 0.2
        r = self._radius * (1 - loop_radius_diff * loop_counter)

        # We have to keep track of the angle we are at and increase it by a percentage of a full circle
        angle = 0
        angle_offset = -math.pi / 2
        angle_delta = 2 * math.pi / max_resources_per_loop

        for resource in self._resources:
            # Compute the x-y coordinate and offset it so it's from the center of the circle
            x, y = math.cos(angle + angle_offset) * r + self._dims[0] / 2, math.sin(angle + angle_offset) * r + self._dims[1] / 2
            
            # Get the resource's blit and dimensions
            blit = resource.blit()
            w, h = blit.get_size()
            
            # Blit it, increase the angle
            surface.blit(blit, (x - w / 2, y - h / 2))
            angle += angle_delta

            # If we have gone a whole loop, reset angle, increase the loop counter and recalculate the radius
            if angle > math.pi * 2:
                loop_counter += 1
                r = self._radius * (1 - loop_radius_diff * loop_counter)
                angle = 0
        return surface
        
    def point_in_place(self, x, y):
        sx, sy = self.position
        w, h = self._dims
        if x < sx or x > sx + w or y < sy or y > sy + h:
            return False
        return True

    def place_resource(self, node: Node):
        with self._thread_lock:
            for resource in self._resources:
                if node.insert(resource):
                    self._resources.remove(resource)
                    return True
            return False
            
    def update(self):
        for place in self._ingoing_connections:
            if isinstance(place, Node):
                place.give_resources(self)

class Magazine(Container):
    def __init__(self, *args, **kwargs):
        super().__init__('Magazine', (Product,), (Product,), *args, **kwargs)

    def insert(self, r: Resource):
        if isinstance(r, Product):
            self._resources.append(r)
            return True
        return False

class Barn(Container):
    def __init__(self, *args, **kwargs):
        super().__init__('Barn', (Food, ), (Food, ), *args, **kwargs)

    def insert(self, r: Resource):
        if isinstance(r, Food):
            self._resources.append(r)
            return True
        return False

class Road(Container):
    VIABILITY_REDUCTION_PER_WORKER = 0.02
    def __init__(self, *args, **kwargs):
        super().__init__('Road', (Worker,), (Worker,), *args, **kwargs)

    @property
    def viability(self):
        return self.VIABILITY_REDUCTION_PER_WORKER * len(self._resources)

    def insert(self, r: Resource):
        if isinstance(r, Worker):
            if not r.damage(self.viability):
                self._resources.append(r)
            return True
        return False

CLASS_NAME_MAP_DICT = {v.__name__: v for v in (Node.__subclasses__() + Container.__subclasses__())}
