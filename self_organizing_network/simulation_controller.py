import pygame
import threading
from self_organizing_network.simulation_window import SimulationWindow


class SimulationController:
    """@brief Controller for Asteroids game.
    Class connecting the Asteroids game with user interface. Allows to modify speed and appearance of the game.
    @author Jakub Fajkowski
    """

    def __init__(self, stats_window, key_threshold=0.75):
        """@brief Constructor.
        Constructor setting key mappings and connecting class with
        :param stats_window: Window that will listen for game over and screen update events.
        :param key_threshold: Threshold for counting keys as pressed.
        """
        self.stats_window = stats_window
        self.current_game = None
        self.current_game_thread = None
        self._key_threshold = key_threshold
        self._key_mappings = [pygame.K_w,
                              pygame.K_s,
                              pygame.K_a,
                              pygame.K_d,
                              pygame.K_RETURN]

    def start(self, headless):
        """@brief Starts the game.
        Method that starts the game in separate thread. Allows to initialize game in normal and headless mode.
        :param headless: if true game will start in headless mode.
        """
        self.current_game = SimulationWindow(finished_listener=self.stats_window,
                                             tick_listener=self.stats_window,
                                             headless=headless)
        self.current_game_thread = threading.Thread(target=self.current_game.run)
        self.current_game_thread.start()

    def stop(self):
        """@brief Stops the game.
        Stops the game and closes it's window if game wasn't initialized in headless mode.
        """
        if self.current_game is not None:
            self.current_game.running = False
            self.current_game = None
        if self.current_game_thread is not None:
            self.current_game_thread.join(5)

    def change_speed(self, speed):
        """@brief Changes speed of the game by altering it's fps.
        If game has been initialized changes speed of it by setting desired frames per second value.
        :param speed: desired frames per second
        """
        if self.current_game is not None:
            self.current_game.speed = float(speed)

    def change_lines(self):
        """@brief Toggles additional lines displaying.
        Toggles displaying of spaceship crosshair and additional lines connecting spaceship with obstacles.
        """
        if self.current_game is not None:
            self.current_game.lines = not self.current_game.lines

    def calculate_buttons(self, neural_network, input_vector):
        """@brief Calculates buttons that should be pressed based on neural network output.
        Feeds the neural network with input vector and interprets output to determine which buttons should be pressed.
        :param neural_network: neural network that will be used to calculate output.
        :param input_vector: current state of the game.
        :return: set of buttons that should be pressed based on output from neural network.
        """
        neural_network.feed_forward(input_vector)
        output_vector = neural_network.get_output()

        return output_vector, set([self._key_mappings[i]
                                   for i in range(len(output_vector))
                                   if output_vector[i] > self._key_threshold])

    def add_key_mapping(self, key):
        """@brief Adds additional key to current mapping.
        Allows to extend current mapping with additional key.
        :param key: key to be mapped.
        """
        self._key_mappings.append(key)
