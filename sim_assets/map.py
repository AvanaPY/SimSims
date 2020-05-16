import pygame
import math
from .ext import compute_bezier_points
class Map:
    def __init__(self):
        self._places = []
        self._selected_build_type = None        # Which type to build
        self._selected_resource_type = None     # Which resource to place 
        self._selected_place = None             # Which place is currently selected

    @property
    def places(self):
        return self._places
        
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

    def can_build(self):
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
            t = self._selected_build_type()
            blit = t.blit()
            blit.fill((0, 180, 220, 100), special_flags=pygame.BLEND_RGBA_MULT)
            return blit, t.name
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
        pygame.draw.lines(surface, (200, 0, 0), False, b_points, 3)