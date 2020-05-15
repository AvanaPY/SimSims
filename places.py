class Place:
    def __init__(self, name):
        self._name = name
        self._resources = []
        self._ingoing_connections = []
        self._outgoing_connections = []

    @property
    def name(self):
        return self._name

    def connect_place(self, place):
        pass

    def connect_ingoing(self, place):
        pass

    def connect_outgoing(self, place):
        pass


####################
#       NODES
####################
class Node(Place):
    def __init__(self, name):
        super().__init__(name)

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

class Flat(Node):
    def __init__(self):
        super().__init__('Flat')

    def use_resources(self):
        pass

    def get_resources(self):
        pass

    def update(self):
        pass

class Diner(Node):
    def __init__(self):
        super().__init__('Diner')

    def use_resources(self):
        pass

    def get_resources(self):
        pass

    def update(self):
        pass

###################
#    CONTAINERS
###################

class Container(Place):
    def __init__(self, name):
        super().__init__(name)
    
    def insert(self):
        pass

    def place_resource(self, node: Node):
        pass

class Magazine(Container):
    def __init__(self):
        super().__init__('Magazine')

    def insert(self):
        pass

class Barn(Container):
    def __init__(self):
        super().__init__('Barn')

    def insert(self):
        pass

class Road(Container):
    def __init__(self):
        super().__init__('Road')

    def insert(self):
        pass

    def reduce_viability(self, worker):
        pass