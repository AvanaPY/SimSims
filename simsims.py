import sys
import pygame
import os

APPLICATION_NAME = 'SimSims'
BACKGROUND_COLOUR = (255, 255, 255)

pygame.init()
pygame.display.set_caption(APPLICATION_NAME)

import threading
import json

from sim_assets import bindings as keybindings
from sim_assets import UI, Panel, Button
from sim_assets import Place, Node, Magazine, Barn, Road, Factory, Field, Flat, Diner
from sim_assets import Worker, Food, Product
from sim_assets import Map

class SimSims:
    def __init__(self, dims, *args, **kwargs):
        self._dims = dims
        self._window = pygame.display.set_mode(dims)

        self._main_font = pygame.font.SysFont('Times New Roman', 24)
        self._mid_font = pygame.font.SysFont('Times New Roman', 18)
        self._keybindings_font = pygame.font.SysFont('Monospace', 18)
        self._keybindings_font.set_underline(True)
        self._places_name_font = pygame.font.SysFont('Times New Roman', 14)

        self._running = False

        self._framerate = kwargs.get('framerate', 60)
        self._clock = pygame.time.Clock()

        self._save_dir = kwargs.get('save_dir', './')

        ############################################################
        # The graphical user interface
        self._ui: UI = UI()

        self._start_button = Button('Start Simulation', self._main_font, (dims[0] / 2, 20), (100, 20), func = lambda: self.start_simulation(),
                                    background_colour=(200, 0, 0), padx=25, pady=10, keybinding=keybindings.PAUSE_START)
        self._ui.add_button(self._start_button)
        
        self._pause_button = Button('Pause Simulation', self._main_font, (dims[0] / 2, 20), (100, 20), func = lambda: self.pause_simulation(),
                                    background_colour=(200, 0, 0), padx=25, pady=10, keybinding=keybindings.PAUSE_START)
        self._pause_button.hide()
        self._ui.add_button(self._pause_button)
        ## KEYBINDS
        self._show_keybind_panel = False
        self._toggle_keybindings_button = Button('Show Keybindigs', self._mid_font, (5, 5), (80, 20), func=self._toggle_keybindings_panel,
                                                background_colour=(200, 200, 200, 200), text_colour=(0, 0, 0), padx=10, centered=False,
                                                keybinding=keybindings.KEYBINDING_SCREEN)
        self._ui.add_button(self._toggle_keybindings_button)

        self._keybind_panel = Panel((0, 0), (100, dims[1]), background_colour=(230, 230, 230, 230))
        self._ui.add_panel(self._keybind_panel)

        text_l_just = 12
        self._keybind_panel.add_text(f'{keybindings.name_of_key(keybindings.SAVE).ljust(text_l_just)} - Save'                                          , self._keybindings_font)
        self._keybind_panel.add_text(f'{keybindings.name_of_key(keybindings.EXIT).ljust(text_l_just)} - Exit'                                          , self._keybindings_font)
        self._keybind_panel.add_text(f'{keybindings.name_of_key(keybindings.LOAD_SCREEN).ljust(text_l_just)} - Toggle load screen', self._keybindings_font)
        self._keybind_panel.add_text(f'{keybindings.name_of_key(keybindings.PAUSE_START).ljust(text_l_just)} - Pause / Start'                          , self._keybindings_font)
        self._keybind_panel.add_text('', self._keybindings_font)
        self._keybind_panel.add_text(f'{keybindings.name_of_key(keybindings.INTERACT).ljust(text_l_just)} - Build/Select'                              , self._keybindings_font)
        self._keybind_panel.add_text(f'{keybindings.name_of_key(keybindings.DESELECT).ljust(text_l_just)} - Remove selection'                          , self._keybindings_font)
        self._keybind_panel.add_text(f'{keybindings.name_of_key(keybindings.DELETE_PLACE).ljust(text_l_just)} - Delete a place'                        , self._keybindings_font)
        self._keybind_panel.add_text(f'{keybindings.name_of_key(keybindings.DISCONNECT_PLACE_CONNECTIONS).ljust(text_l_just)} - Disconnect connections', self._keybindings_font)
        self._keybind_panel.add_text('', self._keybindings_font)
        self._keybind_panel.add_text(f'{keybindings.name_of_key(keybindings.KEYBINDING_SCREEN).ljust(text_l_just)} - Show keybindings'                 , self._keybindings_font)
        self._keybind_panel.hide()

        ## Saving and loading

        w, h = 100, 20
        self._save_button = Button('Save', self._mid_font, (dims[0] - w - 5, 5), (w, h), func=lambda: self._save(),
                                    background_colour=(40, 40, 40, 100), text_colour=(0, 0, 0), centered=False,
                                    keybinding=keybindings.SAVE)
        self._load_button = Button('Load', self._mid_font, (dims[0] - w - 5, h + 10), (w, h), func=lambda:self._toggle_load_menu(),
                                    background_colour=(40, 40, 40, 100), text_colour=(0, 0, 0), centered=False,
                                    keybinding=keybindings.LOAD_SCREEN)
        self._exit_button = Button('Exit', self._mid_font, (dims[0] - w - 5, h * 2 + 15), (w, h), func=lambda:self.exit(),
                                    background_colour=(40, 40, 40, 100), text_colour=(0, 0, 0), centered=False,
                                    keybinding=keybindings.EXIT)
        self._clear_button = Button('Clear', self._mid_font, (dims[0] - w - 5, h * 3 + 20), (w, h), func=lambda:self._map.clear(),
                                    background_colour=(40, 40, 40, 100), text_colour=(0, 0, 0), centered=False,
                                    keybinding=keybindings.EXIT)
        self._ui.add_button(self._save_button)
        self._ui.add_button(self._load_button)
        self._ui.add_button(self._exit_button)
        self._ui.add_button(self._clear_button)

        w, h = 200, dims[1] - self._save_button.dims[1] - self._load_button.dims[1] - self._exit_button.dims[1] - self._clear_button.dims[1] - 20
        self._load_panel = Panel((dims[0] - w, dims[1] - h ), (w, h), expand=False, background_colour=(200, 200, 200, 200), content_offset=2, border_width=0)

        h = 20
        self._load_panel.hide()
        self._ui.add_panel(self._load_panel)
        self._update_load_panel()
        self._show_load_panel = False

        selections = (Magazine, Barn, Road, Factory, Field, Flat, Diner)

        select_btn_width  = self._dims[0] / len(selections)
        select_btn_height = 30
        for i, t in enumerate(selections):
            place = t(set_index=False)
            key = getattr(keybindings, f'SELECT_TYPE_{place.name.upper()}')
            btn = Button(f'{place.name} ({keybindings.name_of_key(key)})', self._main_font,
                    ((i + 0.5) * select_btn_width, self._dims[1] - select_btn_height * 0.75), (select_btn_width, select_btn_height),
                    self.map_select_build, arg=[t], background_colour=(100, 100, 255), text_colour=(0, 0, 0),
                    keybinding=key)
            self._ui.add_button(btn)

        selections = (Worker, Food, Product)
        select_btn_width  = self._dims[0] / len(selections)
        for i, t in enumerate(selections):
            resource = t()
            key = getattr(keybindings, f'SELECT_TYPE_{resource.name.upper()}')
            btn = Button(f'{resource.name} ({keybindings.name_of_key(key)})', self._main_font,
                    ((i + 0.5) * select_btn_width, self._dims[1] - select_btn_height * 2), (select_btn_width, select_btn_height),
                    self.map_select_resource, arg=[t], background_colour=(100, 255, 100), text_colour=(0, 0, 0),
                    keybinding=key)
            self._ui.add_button(btn)

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
                if event.type == pygame.QUIT: self.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_input(*event.pos, event.button)
                if event.type == pygame.KEYDOWN:
                    self.handle_input(*pygame.mouse.get_pos(), event.key)

            if self._started_sim:
                for node in self._map.places:
                    node.update()

            with thread_lock:
                self.render()

    def start_simulation(self):
        """
            Starts the simulation.
        """
        self._started_sim = True
        self._start_button.hide()
        self._pause_button.unhide()

    def pause_simulation(self):
        self._started_sim = False
        self._wait_threads()
        self._start_button.unhide()
        self._pause_button.hide()
    
    def _wait_threads(self):
        """
            Wrapper for Map._wait_threads:

                It waits for any threads to finish before continuing.
        """
        self._map._wait_threads()
    
    def _toggle_keybindings_panel(self):
        """
            Toggles the keybinding panel.
        """
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

    def handle_input(self, mouse_x, mouse_y, button):
        """
            Handles keyboard input.
        """
        if button == keybindings.DISCONNECT_PLACE_CONNECTIONS:
            self.disconnect_connection(mouse_x, mouse_y)
        elif button == keybindings.DELETE_PLACE:
            self.delete_place_at(mouse_x, mouse_y)
        elif button == keybindings.INTERACT:
            btn = None
            for button in self._ui.buttons:
                if button.point(mouse_x, mouse_y):
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
        else:
            for btn in self._ui.buttons:
                if btn.keybinding == button:
                    if btn.call():
                        return

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

    # Loading and saving

    def _toggle_load_menu(self):
        """
            Toggles the load menu.
        """
        if self._show_load_panel:
            self._load_panel.hide()
            self._show_load_panel = False
        else:
            self._load_panel.unhide()
            self._show_load_panel = True

    def _load(self, item):
        """
            Loads a .json file.
        """
        with open(f'{self._save_dir}/{item}', 'rb') as f:
            obj = json.loads(f.read())
            self._map.load_json(obj)

    def _save(self):
        """
            Saves the current simulation as a .json file.
        """
        state = self._started_sim

        self.pause_simulation()
        self._wait_threads()

        index = 0
        base_name = 'simsims'
        existing_files = [os.path.splitext(l)[0] for l in os.listdir(self._save_dir)]
        while f'{base_name}_{index}' in existing_files:
            index += 1
        name = f'{base_name}_{index}'
        map_json = self._map.json()
        with open(f'{self._save_dir}/{name}.json', 'w') as f:
            obj = json.dump(map_json, f)

        self._update_load_panel()
        self._started_sim = state

    def _update_load_panel(self, content_height=20):
        """
            Updates the content of the load panel.
        """
        self._load_panel.clear()
        for l in os.listdir(self._save_dir):
            name = l
            self._load_panel.add_button(text=l, font=self._mid_font, dims=(self._load_panel.dims[0], content_height), func=self._load, arg=[l],
                                        background_colour=(140, 140, 140))