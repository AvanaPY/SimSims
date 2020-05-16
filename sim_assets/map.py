import pygame

class Map:
    def __init__(self):
        
        self._places = []
        self._selected_build_type = None
        self._selected_resource_type = None

    def select_build_type(self, t):
        self._selected_build_type = t
        self._selected_resource_type = None

    def select_resource_type(self, r):
        self._selected_resource_type = r
        self._selected_build_type = None

    def get_place_at(self, x, y):
        place = None
        for p in self._places:
            if p.point_in_place(x, y):
                place = p
        return place

    def build(self, x, y):
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
    
    def selected_build_preview(self):
        if self._selected_build_type:
            blit = self._selected_build_type().blit()
            blit.fill((0, 180, 220, 100), special_flags=pygame.BLEND_RGBA_MULT)
            return blit
        return None

    def blit(self, dims, text_font : pygame.font.Font):
        surface = pygame.Surface(dims, pygame.SRCALPHA, 32).convert_alpha()
        for place in self._places:
            blit = place.blit()
            if blit:
                txt_blit = text_font.render(place.name, True, (0, 0, 0))

                x, y = blit.get_size()
                x = x / 2 - txt_blit.get_width() / 2
                y = y / 2 - txt_blit.get_height() / 2
                
                blit.blit(txt_blit, (x, y))
                surface.blit(blit, place.position)
        return surface