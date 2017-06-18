import random

import pygame
import self_organizing_network.utils as u
from self_organizing_network.base_station import BaseStation
from self_organizing_network.mobile_station import MobileStation


class SimulationWindow:
    def __init__(self, finish_listener=None, tick_listener=None, headless=False):
        self._finish_listener = finish_listener
        self._tick_listener = tick_listener

        if headless:
            self._display_size = (1, 1)
        else:
            self._display_size = (u.WINDOW_SIZE, u.WINDOW_SIZE)

        self.time_elapsed = 0
        self.score = 0
        self.speed = u.DEFAULT_SPEED
        self.display_connections = False
        self.running = False

        self._screen = None
        self._clock = None
        self._base_stations = []
        self._mobile_stations = []

    def _init(self):
        pygame.init()
        self._screen = pygame.display.set_mode(self._display_size, pygame.HWSURFACE | pygame.DOUBLEBUF)
        self._clock = pygame.time.Clock()
        self.running = True
        self._add_base_stations(u.DEFAULT_ROWS, u.DEFAULT_COLS)
        self._add_mobile_stations(u.DEFAULT_MS)

    def _restart(self):
        self.time_elapsed = 0
        self.score = 0
        self._clock = pygame.time.Clock()
        self.running = True
        self._add_base_stations(u.DEFAULT_ROWS, u.DEFAULT_COLS)
        self._add_mobile_stations(u.DEFAULT_MS)

    def _add_base_stations(self, rows, cols):
        self._base_stations = []
        self._create_base_stations(rows, cols)
        self._assign_neighbours(rows, cols)

    def _create_base_stations(self, rows, cols):
        x_offset = u.WINDOW_SIZE / cols
        y_offset = u.WINDOW_SIZE / rows

        for y in range(rows):
            if y % 2 == 0:
                for x in range(cols):
                    self._base_stations.append(BaseStation((x_offset / 2 + x * x_offset,
                                                            y_offset / 2 + y * y_offset),
                                                           u.DEFAULT_BASE_STATION_POWER))
            else:
                for x in range(cols + 1):
                    self._base_stations.append(BaseStation((x * x_offset,
                                                            y_offset / 2 + y * y_offset),
                                                           u.DEFAULT_BASE_STATION_POWER))


    def _assign_neighbours(self, rows, cols):
        for y in range(rows):
            if y % 2 == 0:
                for x in range(cols):
                    bs = self._get_base_station(x, y, rows, cols)
                    bs.add_neighbour(self._get_base_station(x, y - 1, rows, cols))
                    bs.add_neighbour(self._get_base_station(x + 1, y - 1, rows, cols))
                    bs.add_neighbour(self._get_base_station(x - 1, y, rows, cols))
                    bs.add_neighbour(self._get_base_station(x + 1, y, rows, cols))
                    bs.add_neighbour(self._get_base_station(x, y + 1, rows, cols))
                    bs.add_neighbour(self._get_base_station(x + 1, y + 1, rows, cols))
            else:
                for x in range(cols + 1):
                    bs = self._get_base_station(x, y, rows, cols)
                    bs.add_neighbour(self._get_base_station(x - 1, y - 1, rows, cols))
                    bs.add_neighbour(self._get_base_station(x, y - 1, rows, cols))
                    bs.add_neighbour(self._get_base_station(x - 1, y, rows, cols))
                    bs.add_neighbour(self._get_base_station(x + 1, y, rows, cols))
                    bs.add_neighbour(self._get_base_station(x - 1, y + 1, rows, cols))
                    bs.add_neighbour(self._get_base_station(x, y + 1, rows, cols))

    def _get_base_station(self, x, y, rows, cols_per_even_row):
        if y % 2 == 0:
            if not (0 <= y < cols_per_even_row and 0 <= x < rows):
                return None
            even_rows = int(y / 2)
            odd_rows = int(y / 2)
        else:
            if not (0 <= y < cols_per_even_row and 0 <= x <= rows):
                return None
            even_rows = int(y / 2) + 1
            odd_rows = int(y / 2)

        index = (even_rows * cols_per_even_row) + (odd_rows * (cols_per_even_row + 1)) + x
        return self._base_stations[index]


    def _add_mobile_stations(self, num):
        self._mobile_stations = []
        for _ in range(num):
            self._mobile_stations.append(MobileStation(u.CENTER_POINT))

    def run(self):
        self._init()

        while self.running:
            self._clock.tick(60 * self.speed)

            for event in pygame.event.get():
                self._handle_event(event)

            self._refresh_time()
            self._refresh_score()
            self._refresh_connections()
            self._render()
            self._tick()

            if self.time_elapsed == u.DEFAULT_DURATION:
                self._finish()
                self._restart()

        pygame.quit()

    def _handle_event(self, event):
        if event.type == pygame.QUIT:
            self.running = False

    def _refresh_time(self):
        self.time_elapsed += 1

    def _consider_fps(self, value):
        fps = self._clock.get_fps()
        if fps != 0:
            result = value * (60 / fps)
        else:
            result = value
        return result

    def _refresh_score(self):
        for ms in self._mobile_stations:
            score = 1
            for bs in self._base_stations:
                if bs.is_on():
                    score /= (bs.get_power() / 1000)

            if ms.is_connected():
                self.score += score
            else:
                self.score -= score


    def _refresh_connections(self):
        for ms in self._mobile_stations:
            bs, power = self._find_best_base_station(ms)

            if bs is not ms.base_station:
                if ms.is_connected():
                    ms.base_station.disconnect(ms)
                    ms.disconnect()
                if bs is not None:
                    bs.connect(ms)
                    ms.connect(bs)

            ms.power = power

    def _find_best_base_station(self, mobile_station):
        powers = []
        for bs in self._base_stations:
            bs_power_density_in_ms_location = bs.calculate_power_density(mobile_station.coordinates)
            powers.append(bs_power_density_in_ms_location)

        max_power_density = max(powers)

        if max_power_density > u.POWER_DENSITY_THRESHOLD:
            max_index = powers.index(max_power_density)
            return self._base_stations[max_index], max_power_density
        else:
            return None, None

    def _render(self):
        self._screen.fill(u.COLOR_LIGHT_GREY)
        self._display_mobile_stations()
        self._display_base_stations()
        self._display_time()
        self._display_fps()
        pygame.display.update()

    def _display_mobile_stations(self):
        for ms in self._mobile_stations:
            self._display_connection(ms)
            ms.update(self._screen)

    def _display_connection(self, mobile_station):
        if self.display_connections and mobile_station.is_connected():
            pygame.draw.line(self._screen,
                             u.COLOR_GREEN,
                             mobile_station.coordinates,
                             mobile_station.base_station.coordinates)

    def _display_base_stations(self):
        for bs in self._base_stations:
            bs.update(self._screen)

    def _display_time(self):
        font = pygame.font.SysFont("Consolas", 20)
        label = font.render("Time: " + str(self.time_elapsed), 1, u.COLOR_BLACK)
        self._screen.blit(label, (10, 10))

    def _display_fps(self):
        font = pygame.font.SysFont("Consolas", 20)
        label = font.render("FPS: " + str(int(self._clock.get_fps())), 1, u.COLOR_BLACK)
        self._screen.blit(label, (10, 30))

    def _tick(self):
        if self._tick_listener is not None:
            # for bs in self._base_stations:
            bs = self._base_stations[random.randrange(0, len(self._base_stations))]
            power_change = self._tick_listener.on_tick(bs, self._mobile_stations)
            bs.change_power_by(power_change)

    def _finish(self):
        if self._finish_listener is not None:
            self._finish_listener.on_finish()
