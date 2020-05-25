
import pygame
from .ext import map_from_to, compute_bezier_points, colour_linear_interpolation
import math
import time
import threading
import random

from .units import *

class Map:
    def __init__(self):
        self._places = []
        self._selected_build_type = None        # Which type to build
        self._selected_resource_type = None     # Which resource to place 
        self._selected_place = None             # Which place is currently selected
        
        self._selected_previews = {}
        for buildable in (Magazine, Barn, Road, Diner, Factory, Field, Flat):
            b = buildable(set_index=False)
            blit = b.blit()
            blit.fill((0, 180, 220, 100), special_flags=pygame.BLEND_RGBA_MULT)
            self._selected_previews[buildable] = (blit, b.name)

    @property
    def places(self):
        return self._places

    def _wait_threads(self):
        """
            Waits for any places that aren't finished with their current transition to finish the transition.
        """
        for place in self._places:
            while place.working:
                pass

    def select_build_type(self, t):
        """
            Selects a Place type.
        """
        self._selected_build_type = t
        self._selected_resource_type = None
        self._selected_place = None

    def select_resource_type(self, r):
        """
            Selects a resource type.
        """
        self._selected_resource_type = r
        self._selected_build_type = None
        self._selected_place = None

    def select_building_at(self, x, y):
        """
            Selects a building that contains the point (x, y)
        """
        place_at = self.get_place_at(x, y)
        if place_at:
            self._selected_place = place_at

    def deselect_selections(self):
        """
            Deselects all selections.
        """
        self._selected_resource_type = None
        self._selected_build_type = None
        self._selected_place = None

    def get_place_at(self, x, y):
        """
            Returns the place which contains the point (x, y), None if there is no such place.
        """
        place = None
        for p in self._places:
            if p.point_in_place(x, y):
                place = p
        return place

    def disconnect_from_selection(self, x, y):
        """
            Disconnects the currently selected place from whichever place contains the point (x, y)
        """
        if self._selected_place:
            place = self.get_place_at(x, y)
            if place:
                self._selected_place.disconnect_place(place)

    def delete_place_at(self, x, y):
        """
            Fully deletes the place that contains the point (x, y), disconnects any connections to that place
        """
        place = self.get_place_at(x, y)
        if place:
            place.disconnect_all_connections()
            self._places.remove(place)

    def can_build(self):
        """
            Returns a boolean if any buildable type or place is selected.
        """
        return self._selected_build_type or self._selected_place or self._selected_resource_type

    def build(self, x, y):
        """
            Builds a selected building in a location (x, y).
        """
        if self._selected_build_type:
            t = self._selected_build_type()
            w, h = t.dims()
            t.set_position((x, y))
            self._places.append(t)
        elif self._selected_resource_type:
            place = self.get_place_at(x, y)
            if place:
                r = self._selected_resource_type()
                place.insert(r)
        elif self._selected_place:
            place = self.get_place_at(x, y)
            if place:
                self._selected_place.connect_place(place)
    
    def selected_build_preview(self):
        """
            Returns a (blit, name) preview pair of the selected object. Returns (None, "") if no building is selected.
        """
        if self._selected_build_type:
            blit, name = self._selected_previews[self._selected_build_type]
            return blit, name
        return None, ''

    def blit(self, dims, text_font: pygame.font.Font):
        """
            Returns the blit of the map.
        """
        surface = pygame.Surface(dims, pygame.SRCALPHA, 32).convert_alpha()
        for place in self._places:
            pairs = place.connection_points()
            for a, b in pairs:
                self._draw_bezier(surface, a, b)
        for place in self._places:
            blit = place.blit()
            if blit:
                if place == self._selected_place:
                    blit.fill((0, 120, 240, 20), special_flags=pygame.BLEND_RGB_MULT)
                txt_blit = text_font.render(place.name, True, (0, 0, 0))

                x, y = blit.get_size()
                x = x / 2 - txt_blit.get_width() / 2
                y = y / 2 - txt_blit.get_height() / 2
                
                blit.blit(txt_blit, (x, y))
                surface.blit(blit, place.position)

        return surface

    def _draw_bezier(self, surface, pos1, pos2, bend_factor=0.2):
        """
            Returns a pygame.Surface object containing a curved line.
        """
        direction = pos2[0] - pos1[0], pos2[1] - pos1[1]
        orth = -direction[1] * bend_factor, direction[0] * bend_factor
        ctrl_point = pos1[0] + direction[0] * 0.5 + orth[0], pos1[1] + direction[1] * 0.5 + orth[1]
        b_points = compute_bezier_points((pos1, ctrl_point, pos2))
        length = sum([math.dist(b_points[i], b_points[i + 1]) for i in range(len(b_points) - 1)])  # Evaluate sum of all the "segment" lengths of the bezier curve
        walked = 0

        start_col = (255, 0, 0)
        end_col = (0, 120, 255)
        for i in range(len(b_points) - 1):
            walked += math.dist(b_points[i], b_points[i + 1])
            col = colour_linear_interpolation(start_col, end_col, walked / length)
            pygame.draw.line(surface, col, b_points[i], b_points[i + 1], 3)

    def json(self):
        """
            Returns a json object representing the map.
        """
        for i, p in enumerate(self._places):
            p.set_index(i)
        places = []
        for place in self._places:
            p_json = place.json()
            p_json = {k.replace('_',''):v for k, v in p_json.items()}
            places.append(p_json)
        return places
        
    def load_json(self, json):
        self._places.clear()
        index_map = {}
        for place_json in json:
            place = Place.from_json(place_json)
            self._places.append(place)
            index_map[place_json['index']] = place

        for place_json in json:
            place = index_map[place_json['index']]
            for index in place_json['out']:
                p = index_map[index]
                place.connect_place(p)