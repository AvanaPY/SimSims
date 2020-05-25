import pygame

class Keybindings:
    """
        Keybinding data for SimSims.
    """
    def __init__(self):
        self.INTERACT = pygame.BUTTON_LEFT
        self.DESELECT = pygame.BUTTON_RIGHT
        self.DISCONNECT_PLACE_CONNECTIONS = pygame.K_x
        self.DELETE_PLACE = pygame.BUTTON_MIDDLE
        self.PAUSE_START = pygame.K_SPACE

        self.EXIT = pygame.K_ESCAPE
        self.SAVE = pygame.K_s
        self.LOAD_SCREEN = pygame.K_l
        self.KEYBINDING_SCREEN = pygame.K_TAB

        self.SELECT_TYPE_MAGAZINE = pygame.K_1
        self.SELECT_TYPE_BARN     = pygame.K_2
        self.SELECT_TYPE_ROAD     = pygame.K_3
        self.SELECT_TYPE_FACTORY  = pygame.K_4
        self.SELECT_TYPE_FIELD    = pygame.K_5
        self.SELECT_TYPE_FLAT     = pygame.K_6
        self.SELECT_TYPE_DINER    = pygame.K_7
        self.SELECT_TYPE_WORKER   = pygame.K_8
        self.SELECT_TYPE_FOOD     = pygame.K_9
        self.SELECT_TYPE_PRODUCT  = pygame.K_0

    def name_of_key(self, key):
        """
            Returns a pygame key name for a key id
        """
        m = {
            pygame.BUTTON_LEFT: 'Mouse Left',
            pygame.BUTTON_RIGHT: 'Mouse Right',
            pygame.BUTTON_MIDDLE: 'Mouse Middle'
        }
        if key in m:
            return m[key]
        return pygame.key.name(key).capitalize()
        
bindings = Keybindings()

if __name__ == '__main__':
    pygame.init()