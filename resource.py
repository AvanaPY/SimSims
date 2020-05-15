class Resource:
    def __init__(self, name):
        self._name = name
    @property
    def name(self):
        return self._name
class Worker(Resource):
    def __init__(self):
        super().__init__('Worker')
        self._viability = 1

    def damage(self, viability):
        self._viability -= viability
    
class Food(Resource):
    def __init__(self):
        super().__init__('Food')

class Product(Resource):
    def __init__(self):
        super().__init__('Product')