import pygame


class Object(pygame.sprite.Sprite):
    def __init__(self, image, coordinates, direction=90, image_scale=1):
        pygame.sprite.Sprite.__init__(self)
        self._image = self._scale_image(image, image_scale)
        self.coordinates = coordinates
        self.direction = direction  # from 0 to 359 where 0 is right and 90 is up

    def update(self, surface):
        rotated = self._rotate_image(self.direction)
        x = self.coordinates[0] - self._image.get_width() / 2
        y = self.coordinates[1] - self._image.get_height() / 2
        top_left = (x, y)
        surface.blit(rotated, top_left)

    def _rotate_image(self, angle):
        """rotate an image while keeping its center and size"""
        orig_rect = self._image.get_rect()
        rot_image = pygame.transform.rotate(self._image, angle)
        rot_rect = orig_rect.copy()
        rot_rect.center = rot_image.get_rect().center
        rot_image = rot_image.subsurface(rot_rect).copy()
        return rot_image

    @staticmethod
    def _scale_image(image, scale):
        scaled_width = int(image.get_width() * scale)
        scaled_height = int(image.get_height() * scale)
        scaled_image = pygame.transform.scale(image, (scaled_width, scaled_height))
        return scaled_image
