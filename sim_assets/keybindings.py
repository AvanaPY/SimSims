import pygame

class Keybindings:
    """
        Keybinding data for SimSims.
    """
    INTERACT = pygame.BUTTON_LEFT
    DESELECT = pygame.BUTTON_RIGHT
    DISCONNECT_PLACE_CONNECTIONS = pygame.K_x
    DELETE_PLACE = pygame.BUTTON_MIDDLE
    PAUSE_START = pygame.K_SPACE

    EXIT = pygame.K_ESCAPE
    SAVE = pygame.K_s
    LOAD_SCREEN = pygame.K_l
    KEYBINDING_SCREEN = pygame.K_TAB 

    SELECT_TYPE_MAGAZINE = pygame.K_1
    SELECT_TYPE_BARN     = pygame.K_2
    SELECT_TYPE_ROAD     = pygame.K_3
    SELECT_TYPE_FACTORY  = pygame.K_4
    SELECT_TYPE_FIELD    = pygame.K_5
    SELECT_TYPE_FLAT     = pygame.K_6
    SELECT_TYPE_DINER    = pygame.K_7
    SELECT_TYPE_WORKER   = pygame.K_8
    SELECT_TYPE_FOOD     = pygame.K_9
    SELECT_TYPE_PRODUCT  = pygame.K_0

    @staticmethod
    def name_of_key(key):
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
        
bindings = Keybindings

if __name__ == '__main__':
    pygame.init()