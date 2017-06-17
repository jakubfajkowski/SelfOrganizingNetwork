import pygame
import random
from self_organizing_network.moving_object import MovingObject


class MobileStation(MovingObject):
    def __init__(self, coordinates):
        image = pygame.image.load('mobile_station.png')
        v_x = random.uniform(0, 1) - 0.5
        v_y = random.uniform(0, 1) - 0.5
        super().__init__(image, coordinates, velocity=(v_x, v_y))


    def update(self, surface):
        MovingObject.update(self, surface)