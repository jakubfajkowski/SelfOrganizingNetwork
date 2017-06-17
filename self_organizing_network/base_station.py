import pygame
import math
import self_organizing_network.utils as u
from self_organizing_network.object import Object

POWER_DENSITY_THRESHOLD = 1

class BaseStation(Object):
    def __init__(self, coordinates, power):
        image = pygame.image.load('base_station.png')
        self._power = power
        super().__init__(image=image,
                         coordinates=coordinates,
                         image_scale=1)

    def update(self, surface):
        self.direction += 1
        self._draw_range(surface)
        super(BaseStation, self).update(surface)

    def _draw_range(self, surface):
        radius = int(math.sqrt(self._power / (4 * math.pi * POWER_DENSITY_THRESHOLD)))
        self._draw_circle(surface, u.COLOR_RED, radius, 1)

    def _draw_circle(self, surface, color, radius, thickness):
        x = int(self.coordinates[0])
        y = int(self.coordinates[1])
        pygame.draw.circle(surface, color, (x, y), radius, thickness)