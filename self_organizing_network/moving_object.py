from self_organizing_network.utils import WINDOW_SIZE
from self_organizing_network.object import Object


class MovingObject(Object):
    def __init__(self, image, coordinates, velocity=(0, 0), direction=0, image_scale=1):
        super().__init__(image, coordinates, direction, image_scale)
        self.velocity = velocity

    def update(self, surface):
        self.move()
        Object.update(self, surface)

    def move(self):
        next_x = self.coordinates[0] + self.velocity[0]
        next_y = self.coordinates[1] + self.velocity[1]

        if next_x <= 0 or next_x >= WINDOW_SIZE:
            self.velocity = (-self.velocity[0], self.velocity[1])

        if next_y <= 0 or next_y >= WINDOW_SIZE:
            self.velocity = (self.velocity[0], -self.velocity[1])

        self.coordinates = (next_x, next_y)
