import pygame
import math
import self_organizing_network.utils as u
from self_organizing_network.object import Object

class BaseStation(Object):
    def __init__(self, coordinates, power):
        image = pygame.image.load('base_station.png')
        super().__init__(image=image,
                         coordinates=coordinates,
                         image_scale=1)

        self._power = power
        self._mobile_stations = []
        self._neighbours = []


    def update(self, surface):
        self.direction += 1
        self._draw_range(surface)
        super(BaseStation, self).update(surface)

    def _draw_range(self, surface):
        radius = int(math.sqrt(self._power / (4 * math.pi * u.POWER_DENSITY_THRESHOLD)))
        self._draw_circle(surface, u.COLOR_RED, radius, 1)

    def _draw_circle(self, surface, color, radius, thickness):
        x = int(self.coordinates[0])
        y = int(self.coordinates[1])
        if radius >= thickness:
            pygame.draw.circle(surface, color, (x, y), radius, thickness)

    def calculate_power_density(self, coordinates):
        d_x = self.coordinates[0] - coordinates[0]
        d_y = self.coordinates[1] - coordinates[1]
        distance_square = d_x**2 + d_y**2

        if distance_square != 0:
            return self._power / (4 * math.pi * distance_square)
        else:
            return self._power

    def connect(self, mobile_station):
        self._mobile_stations.append(mobile_station)

    def disconnect(self, mobile_station):
        self._mobile_stations.remove(mobile_station)

    def get_mobile_stations(self):
        return self._mobile_stations

    def change_power_by(self, power_change):
        self._power += power_change
        if self._power < 0:
            self._power = 0

    def get_power(self):
        return self._power

    def is_on(self):
        return self._power != 0

    def add_neighbour(self, base_station):
        if base_station != None:
            self._neighbours.append(base_station)

    def get_neighbours(self):
        return self._neighbours