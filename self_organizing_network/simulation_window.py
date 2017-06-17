import pygame
import self_organizing_network.utils as u
from self_organizing_network.base_station import BaseStation
from self_organizing_network.mobile_station import MobileStation


class SimulationWindow:
    def __init__(self, finished_listener=None, tick_listener=None, headless=False):
        self._game_over_listener = finished_listener
        self._screen_update_listener = tick_listener

        if headless:
            self._display_size = (1, 1)
        else:
            self._display_size = (u.WINDOW_SIZE, u.WINDOW_SIZE)

        self.time_elapsed = 0
        self.speed = u.DEFAULT_SPEED
        self.show_connections = False
        self.running = False

        self._screen = None
        self._clock = None
        self._pressed_buttons = set()
        self._base_stations = pygame.sprite.Group()
        self._mobile_stations = pygame.sprite.Group()

    def _init(self):
        pygame.init()
        self._screen = pygame.display.set_mode(self._display_size, pygame.HWSURFACE | pygame.DOUBLEBUF)
        self._clock = pygame.time.Clock()
        self.running = True
        self._add_base_stations()
        self._add_mobile_stations(10)

    def _add_base_stations(self):
        self._base_stations.add(BaseStation((100, 100), 650000))
        self._base_stations.add(BaseStation((u.WINDOW_SIZE - 100, 100), 650000))
        self._base_stations.add(BaseStation((100, u.WINDOW_SIZE - 100), 650000))
        self._base_stations.add(BaseStation((u.WINDOW_SIZE - 100, u.WINDOW_SIZE - 100), 650000))
        self._base_stations.add(BaseStation(u.CENTER_POINT, 200000))

    def _add_mobile_stations(self, num):
        for _ in range(num):
            self._mobile_stations.add(MobileStation(u.CENTER_POINT))

    def restart(self):
        self.time_elapsed = 0
        self._clock = pygame.time.Clock()
        self._base_stations = pygame.sprite.Group()
        self._mobile_stations = pygame.sprite.Group()

    def run(self):
        self._init()

        while self.running:
            self._clock.tick(60 * self.speed)

            for event in pygame.event.get():
                if event is not pygame.MOUSEMOTION:
                    self._handle_event(event)

            for _ in self._pressed_buttons:
                pass

            self._render()

        pygame.quit()

    def _consider_fps(self, value):
        fps = self._clock.get_fps()
        if fps != 0:
            result = value * (60/fps)
        else:
            result = value
        return result

    def _handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            self._pressed_buttons.add(event.key)
            if event.key == pygame.K_ESCAPE:
                self.running = False

        elif event.type == pygame.KEYUP:
            if self._pressed_buttons:
                self._pressed_buttons.remove(event.key)
        elif event.type == pygame.QUIT:
            self.running = False

    def _render(self):
        self._screen.fill(u.COLOR_WHITE)
        self._base_stations.update(self._screen)
        self._mobile_stations.update(self._screen)
        self._display_time()
        self._display_fps()
        pygame.display.update()

    def _display_time(self):
        font = pygame.font.SysFont("Consolas", 20)
        label = font.render("Time: " + str(self.time_elapsed), 1, u.COLOR_BLACK)
        self._screen.blit(label, (10, 10))

    def _display_fps(self):
        font = pygame.font.SysFont("Consolas", 20)
        label = font.render("FPS: " + str(int(self._clock.get_fps())), 1, u.COLOR_BLACK)
        self._screen.blit(label, (10, 30))

    def _display_connection(self, mobile_station):
        pygame.draw.line(self._screen,
                         u.COLOR_RED,
                         mobile_station.coordinates,
                         mobile_station.base_station.coordinates)
