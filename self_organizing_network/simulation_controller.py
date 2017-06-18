import threading
from self_organizing_network.simulation_window import SimulationWindow


class SimulationController:
    def __init__(self, stats_window, key_threshold=0.75):
        self.stats_window = stats_window
        self.current = None
        self.current_game_thread = None

    def start(self, headless):
        self.current = SimulationWindow(finish_listener=self.stats_window,
                                        tick_listener=self.stats_window,
                                        headless=headless)
        self.current_game_thread = threading.Thread(target=self.current.run)
        self.current_game_thread.start()

    def stop(self):
        if self.current is not None:
            self.current.running = False
            self.current = None
        if self.current_game_thread is not None:
            self.current_game_thread.join(5)

    def change_speed(self, speed):
        if self.current is not None:
            self.current.speed = float(speed)

    def change_view(self):
        if self.current is not None:
            self.current.display_connections = not self.current.display_connections

    def predict_power_change(self, neural_network, input_vector):
        neural_network.feed_forward(input_vector)
        output_vector = neural_network.get_output()

        return output_vector
