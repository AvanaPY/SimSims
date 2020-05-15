import sys
import pygame


APPLICATION_NAME = 'SimsSims'
BACKGROUND_COLOUR = (40, 40, 40)

pygame.init()
pygame.display.set_caption(APPLICATION_NAME)

from assets import Button
from places import Place, Node, Magazine, Barn, Road, Factory, Field, Flat, Diner
from resource import Worker, Food, Product
class SimsSims:
    def __init__(self, dims, framerate=60):
        self._dims = dims
        self._window = pygame.display.set_mode(dims)

        self._main_font  = pygame.font.SysFont('Times New Roman', 24)

        self._running = False

        self._framerate = framerate
        self._clock = pygame.time.Clock()
        self._buttons = []

        self.start_button = Button('Start Simulation', self._main_font, (dims[0] / 2, 20), (100, 20), func = lambda: self.start_simulation(),
                                    background_colour=(200, 0, 0), padx=25, pady=10)
        self.add_button(self.start_button)

        selections = (Magazine, Barn, Road, Factory, Field, Flat, Diner)

        select_btn_width  = self._dims[0] / len(selections)
        select_btn_height = 30
        for i, t in enumerate(selections):
            place = t()
            btn = Button(place.name, self._main_font, ((i + 0.5) * select_btn_width, self._dims[1] - select_btn_height * 0.75), (select_btn_width, select_btn_height),
                    lambda a :print(a), args=[t], background_colour=(100, 100, 255), text_colour=(0, 0, 0))
            self.add_button(btn)

        selections = (Worker, Food, Product)
        select_btn_width  = self._dims[0] / len(selections)
        for i, t in enumerate(selections):
            resource = t()
            btn = Button(resource.name, self._main_font, ((i + 0.5) * select_btn_width, self._dims[1] - select_btn_height * 2), (select_btn_width, select_btn_height),
                    lambda a :print(a), args=[t], background_colour=(100, 255, 100), text_colour=(0, 0, 0))
            self.add_button(btn)
            
    def start(self):
        self._running = True
        while self._running:
            delta_time = self._clock.tick(self._framerate) * 0.001

            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE): self.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = event.pos
                    self.mouse_down(x, y, event.button)

            self.render()
    
    def add_button(self, btn):
        self._buttons.append(btn)

    def start_simulation(self):
        self.start_button.hide()

    def mouse_down(self, mouse_x, mouse_y, button):
        btn = None
        for button in self._buttons:
            if button.point_in_button(mouse_x, mouse_y):
                btn = button
        if btn:
            btn.call()

    def exit(self):
        sys.exit()

    def render(self):
        self._window.fill(BACKGROUND_COLOUR)
        for button in self._buttons:
            if not button.hidden:
                self._window.blit(button.blit, button.position)
        pygame.display.flip()