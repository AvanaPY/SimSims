import sys
import pygame

APPLICATION_NAME = 'SimsSims'
BACKGROUND_COLOUR = (255, 255, 255)

pygame.init()
pygame.display.set_caption(APPLICATION_NAME)

import threading

from sim_assets import bindings as keybindings
from ui_assets import UI, Panel, Button
from sim_assets import Place, Node, Magazine, Barn, Road, Factory, Field, Flat, Diner
from sim_assets import Worker, Food, Product
from sim_assets import Map

class SimsSims:
    def __init__(self, dims, framerate=60):
        self._dims = dims
        self._window = pygame.display.set_mode(dims)

        self._main_font = pygame.font.SysFont('Times New Roman', 24)
        self._mid_font = pygame.font.SysFont('Times New Roman', 18)
        self._places_name_font = pygame.font.SysFont('Times New Roman', 14)

        self._running = False

        self._framerate = framerate
        self._clock = pygame.time.Clock()

        ############################################################
        # The graphical user interface
        self._ui: UI = UI()

        self._start_button = Button('Start Simulation', self._main_font, (dims[0] / 2, 20), (100, 20), func = lambda: self.start_simulation(),
                                    background_colour=(200, 0, 0), padx=25, pady=10)
        self._ui.add_button(self._start_button)

        self._show_keybind_panel = False
        self._toggle_keybindings_button = Button('Show Keybindigs', self._mid_font, (5, 5), (100, 20), func=self._toggle_keybindings_panel,
                                                background_colour=(40, 40, 40, 100), text_colour=(0, 0, 0), padx=25, centered=False)
        self._ui.add_button(self._toggle_keybindings_button)

        self._keybind_panel = Panel((0, 0), (100, dims[1]))
        self._ui.add_panel(self._keybind_panel)

        self._keybind_panel.add_text(f'{keybindings.name_of_key(keybindings.DISCONNECT_PLACE_CONNECTIONS)} - Disconnect connections (Mouse Over)', self._mid_font)
        self._keybind_panel.add_text(f'{keybindings.name_of_key(keybindings.DELETE_PLACE)} - Delete a place (Mouse Over)', self._mid_font)
        self._keybind_panel.add_text(f'{keybindings.name_of_key(keybindings.INTERACT)} - Build/Select (Mouse Over)', self._mid_font)
        self._keybind_panel.add_text(f'{keybindings.name_of_key(keybindings.DESELECT)} - Remove selection (Mouse Over)', self._mid_font)
        self._keybind_panel.hide()

        selections = (Magazine, Barn, Road, Factory, Field, Flat, Diner)

        select_btn_width  = self._dims[0] / len(selections)
        select_btn_height = 30
        for i, t in enumerate(selections):
            place = t()
            key = getattr(keybindings, f'SELECT_TYPE_{place.name.upper()}')
            btn = Button(f'{place.name} ({keybindings.name_of_key(key)})', self._main_font,
                    ((i + 0.5) * select_btn_width, self._dims[1] - select_btn_height * 0.75), (select_btn_width, select_btn_height),
                    self.map_select_build, args=[t], background_colour=(100, 100, 255), text_colour=(0, 0, 0),
                    keybinding=key)
            self._ui.add_button(btn)

        selections = (Worker, Food, Product)
        select_btn_width  = self._dims[0] / len(selections)
        for i, t in enumerate(selections):
            resource = t()
            key = getattr(keybindings, f'SELECT_TYPE_{resource.name.upper()}')
            btn = Button(f'{resource.name} ({keybindings.name_of_key(key)})', self._main_font,
                    ((i + 0.5) * select_btn_width, self._dims[1] - select_btn_height * 2), (select_btn_width, select_btn_height),
                    self.map_select_resource, args=[t], background_colour=(100, 255, 100), text_colour=(0, 0, 0),
                    keybinding=key)
            self._ui.add_button(btn)
        
        ############################################################
        # The map itself of nodes etc.
        self._map = Map()
        self._started_sim = False

    def start(self):
        """
            Starts the application.
        """
        thread_lock = threading.Lock()
        self._running = True
        while self._running:
            delta_time = self._clock.tick(self._framerate) * 0.001 # Mult by 0.001 to get it in milliseconds

            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE): self.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = event.pos
                    self.mouse_down(x, y, event.button)
                if event.type == pygame.KEYDOWN:
                    self.handle_keyboard_input(*pygame.mouse.get_pos(), event.key)

            if self._started_sim:
                for node in self._map.places:
                    node.update()

            with thread_lock:
                self.render()

    def start_simulation(self):
        """
            Starts the simulation.
        """
        self._start_button.hide()
        self._started_sim = True
        
    def _toggle_keybindings_panel(self):
        self._show_keybind_panel = not self._show_keybind_panel
        if self._show_keybind_panel:
            self._toggle_keybindings_button.move(self._keybind_panel.dims[0], 0)
            self._keybind_panel.unhide()
        else:
            self._toggle_keybindings_button.move(-self._keybind_panel.dims[0], 0)
            self._keybind_panel.hide()
    
    def map_select_build(self, t):
        """
            Wrapper for Map.select_build_type
        """
        self._map.select_build_type(t)

    def map_select_resource(self, r):
        """
            Wrapper for Map.select_resource_type
        """
        self._map.select_resource_type(r)

    def mouse_down(self, mouse_x, mouse_y, button):
        """
            Handles the mouse down event.
        """
        if button == keybindings.INTERACT:
            btn = None
            for button in self._ui.buttons:
                if button.point_in_button(mouse_x, mouse_y):
                    btn = button
            if btn:
                btn.call()
            else:
                if self._map.can_build():
                    self._map.build(mouse_x, mouse_y)
                else:
                    self._map.select_building_at(mouse_x, mouse_y)
        elif button == keybindings.DESELECT:
            self._map.deselect_selections()

    def handle_keyboard_input(self, mouse_x, mouse_y, button):
        """
            Handles keyboard input.
        """
        if button == keybindings.DISCONNECT_PLACE_CONNECTIONS:
            self.disconnect_connection(mouse_x, mouse_y)
        elif button == keybindings.DELETE_PLACE:
            self.delete_place_at(mouse_x, mouse_y)
        else:
            for btn in self._ui.buttons:
                if btn.keybinding == button:
                    btn.call()

    def disconnect_connection(self, mouse_x, mouse_y):
        """
            Wrapper for Map.disconnect_from_selection
        """
        self._map.disconnect_from_selection(mouse_x, mouse_y)

    def delete_place_at(self, mouse_x, mouse_y):
        """
            Wrapper for Map.delete_place_at
        """
        self._map.delete_place_at(mouse_x, mouse_y)

    def exit(self):
        """
            Exits the simulation.
        """
        sys.exit()

    def render(self):
        """
            Renders the simulation and flips the display's pixels.
        """
        self._window.fill(BACKGROUND_COLOUR)
        self._window.blit(self._map.blit(self._dims, self._places_name_font), (0, 0))

        # Renders the preview of what is about to be built if possible
        build_preview, text = self._map.selected_build_preview()
        if build_preview:
            w, h = build_preview.get_size()
            mx, my = pygame.mouse.get_pos()
            self._window.blit(build_preview, (mx - w / 2, my - h / 2))

            text_blit = self._places_name_font.render(text, True, (0, 0, 0))
            tw, th = text_blit.get_size()
            self._window.blit(text_blit, (mx - tw / 2, my - th / 2))

        # Render all the UI elements
        for ui_element in self._ui:
            if not ui_element.hidden:
                self._window.blit(ui_element.blit, ui_element.position)
        pygame.display.flip()