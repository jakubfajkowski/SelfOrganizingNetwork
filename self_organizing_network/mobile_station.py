import pygame
import random
from self_organizing_network.moving_object import MovingObject


class MobileStation(MovingObject):
    def __init__(self, coordinates):
        image = pygame.image.load('mobile_station.png')
        v_x = random.uniform(0, 5) - 2.5
        v_y = random.uniform(0, 5) - 2.5
        super().__init__(image, coordinates, velocity=(v_x, v_y))

        self.power = None
        self.base_station = None


    def update(self, surface):
        MovingObject.update(self, surface)

    def connect(self, base_station):
        self.base_station = base_station

    def disconnect(self):
        self.base_station = None

    def is_connected(self):
        return self.base_station is not None