import math
import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib import style
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from son_controller import MachineGamingController
from simulation_controller import GameController
import labels
import utils as c

matplotlib.rcParams.update({'font.size': 8})
matplotlib.use('TkAgg')
style.use('dark_background')


class MachineGamingWindow(tk.Tk):
    ## @brief Main class of the application - provides user interface.
    ## Class is responsible for creating user interface and connecting it with proper controllers.
    ## Allows user to manage and supervise learning process.
    ## @authors Piotr Truszczynski, Jakub Fajkowski

    def __init__(self):
        """@brief Constructor for main frame and controllers.
        Constructor responsible for creating main frame and all controllers. Sets up all GUI elements.
        """
        tk.Tk.__init__(self)
        self.wm_title(labels.title)
        self.resizable(0, 0)
        self.machine_gaming_controller = MachineGamingController(stats_window=self)
        self.game_controller = GameController(stats_window=self)

        self.mean_gen_score_x = []
        self.mean_gen_score_y = []
        self.best_gen_score_x = []
        self.best_gen_score_y = []
        self.best_score_overall = 0
        self.curr_gen_best = 0
        self.curr_gen_total_score = 0

        self.eap_label_vars = []
        self.stat_label_vars = []

        self.canvas = None
        self.fig = Figure(figsize=(5, 4), dpi=100, tight_layout={'h_pad': 3})
        self.best_gen_score = self.fig.add_subplot(2, 1, 1)
        self.mean_gen_score = self.fig.add_subplot(2, 1, 2)

        frame = tk.Frame(self)
        frame.pack(side=tk.TOP, anchor='w')

        self.controls_frame = tk.Frame(frame)
        self.controls_frame.pack(side=tk.LEFT)
        self.infos_frame = tk.Frame(frame)
        self.infos_frame.pack(side=tk.TOP, anchor='e')
        self.speed_slider = None
        self.sliders_frame = tk.Frame(frame)
        self.sliders_frame.pack(side=tk.BOTTOM)

        self._add_controls()
        self._add_infos()
        self._add_sliders()
        self._add_plot()

    def run(self):
        """@brief Starts the main loop of the interface.
        Method used to initiate user interface and start it's main loop.
        """
        self.protocol("WM_DELETE_WINDOW", self._quit)
        self.mainloop()

    def start(self, headless):
        """@brief Starts the simulation
        Method that starts the simulation if parameters of Evolutionary Algorithm have been defined.
        Allows to initialize game in normal and headless mode by calling method from GameController class.
        If user did not define or load algorithm from file, proper message will be displayed.
        :param headless: if true game will start in headless mode.
        """
        if self.machine_gaming_controller.ea is not None:
            if self.game_controller.current_game is not None:
                self.stop()
            self.game_controller.start(headless=headless)
        else:
            messagebox.showwarning(labels.msgbox_title[0], labels.msgbox_msg[0])

    def stop(self):
        """@brief Stops the simulation if it's running.
        If the simulation is running calls stop() method on GameController class. Also moves simulation speed
        slider to the initial position.
        """
        self.speed_slider.set(1)
        if self.game_controller.current_game is not None:
            self.game_controller.stop()

    def _add_controls(self):
        buttons_callbacks = [lambda: self.start(headless=True),
                             lambda: self.start(headless=False),
                             self.stop, self.game_controller.change_lines,
                             self._enter_parameters, self._set_path_and_save,
                             self._set_path_and_load, self._quit]

        for i in range(len(labels.buttons)):
            button = tk.Button(self.controls_frame, text=labels.buttons[i],
                               padx=8, pady=6, width=6, height=1, command=buttons_callbacks[i])
            button.pack(side=tk.TOP)

    def _add_infos(self):
        stats_frame = tk.LabelFrame(self.infos_frame, text=labels.frames[0])
        stats_frame.pack(side=tk.TOP, anchor='e')
        stats_labels = []

        for i in range(len(labels.stats)):
            self.stat_label_vars.append(tk.StringVar())
            self.stat_label_vars[i].set(labels.stats[i])

        for i in range(len(labels.stats)):
            stats_labels.append(tk.Label(stats_frame, textvariable=self.stat_label_vars[i],
                                         width=53, anchor="w"))
            stats_labels[i].pack(side=tk.TOP, anchor='w')

        params_frame = tk.LabelFrame(self.infos_frame, text=labels.frames[1])
        params_frame.pack(side=tk.TOP, anchor='e')

        for i in range(len(labels.params)):
            self.eap_label_vars.append(tk.StringVar())
            self.eap_label_vars[i].set(labels.params[i])

        param_labels = []
        for i in range(len(labels.params)):
            param_labels.append(tk.Label(params_frame, textvariable=self.eap_label_vars[i],
                                         width=53, anchor="w"))
            param_labels[i].pack(anchor='nw')

    def _add_sliders(self):
        speed_slider_frame = tk.Frame(self.sliders_frame)
        speed_slider_frame.pack(side=tk.LEFT)
        speed_label = tk.Label(speed_slider_frame, text=labels.slider)
        speed_label.pack(side=tk.BOTTOM)
        self.speed_slider = tk.Scale(speed_slider_frame, orient='horizontal', length=350, width=10,
                                     from_=1, to=10, resolution=0.1, command=self.game_controller.change_speed)
        self.speed_slider.pack(side=tk.BOTTOM)

    def _add_plot(self):
        self.canvas = FigureCanvasTkAgg(self.fig, self)
        self.canvas.show()
        self.canvas.get_tk_widget().pack(side=tk.BOTTOM)
        self._update_plots()

    def _enter_parameters(self):
        param_frame = tk.Toplevel()
        default_values = [10, 4,
                          1, 0.5,
                          3, 10.0]
        entries = []

        for i in range(len(labels.params)):
            label = tk.Label(param_frame, text=labels.params[i])
            entries.append(tk.Entry(param_frame))
            label.grid(row=i, column=0)
            entries[i].insert(0, default_values[i])
            entries[i].grid(row=i, column=1)

        create_button = tk.Button(
            param_frame, text=labels.create_button,
            command=lambda: [self.machine_gaming_controller.initialize_ea(self._extract_str_from_entries(entries)),
                             self._update_ea_parameters(self._extract_str_from_entries(entries)),
                             self._reset_plots(),
                             param_frame.destroy()])
        create_button.grid(row=10, column=0, columnspan=2)

    def _extract_str_from_entries(self, entries):
        return [e.get() for e in entries]

    def _update_ea_parameters(self, parameters):
        for i in range(len(parameters)):
            self.eap_label_vars[i].set(labels.params[i] + str(parameters[i]))

    def _update_stats(self, current_gen_num, current_nn_num, current_score, current_output):
        current_probs = [(x, round(y, 2)) for x, y in zip(["W", "S", "A", "D", "ENT"], current_output)]

        current_stats = [current_gen_num,
                         current_nn_num,
                         current_score,
                         self.best_score_overall,
                         current_probs]

        for i in range(len(self.stat_label_vars)):
            self.stat_label_vars[i].set(labels.stats[i] + str(current_stats[i]))

    def _quit(self):
        if self.game_controller.current_game is not None:
            messagebox.showwarning(labels.msgbox_title[3], labels.msgbox_msg[5])
        else:
            self.stop()
            self.quit()
            self.destroy()

    def _set_path_and_save(self):
        path = filedialog.asksaveasfilename(filetypes=labels.mg_filetype, initialfile=labels.initialfilename)
        if len(path) is 0:  # dialog closed with "cancel".
            return
        if self.machine_gaming_controller.save(path):
            messagebox.showinfo(labels.msgbox_title[1], labels.msgbox_msg[1])
        else:
            messagebox.showwarning(labels.msgbox_title[1], labels.msgbox_msg[2])

    def _set_path_and_load(self):
        path = filedialog.askopenfilename(filetypes=labels.mg_filetype)
        if len(path) is 0:  # dialog closed with "cancel".
            return
        success, parameters = self.machine_gaming_controller.load(path)
        if success:
            self._update_ea_parameters(parameters)
            self._reset_plots()
            messagebox.showinfo(labels.msgbox_title[2], labels.msgbox_msg[3])
        else:
            messagebox.showwarning(labels.msgbox_title[2], labels.msgbox_msg[4])

    def _on_game_over(self):  # listener for spaceship crashes
        current_game_score = self.game_controller.current_game.score
        self._update_scores(current_game_score)
        self.machine_gaming_controller.neural_network.fitness = current_game_score
        self.machine_gaming_controller.process()

    def _on_screen_update(self, player, obstacles):
        neural_network = self.machine_gaming_controller.neural_network
        if neural_network is None:
            return

        screen_state = [(player.coordinates.x - c.CENTER_POINT.x)/c.WINDOW_SIZE*2,
                        (player.coordinates.y - c.CENTER_POINT.y)/c.WINDOW_SIZE*2,
                        (player.direction - 180)/180]

        for obstacle in obstacles:
            delta_x = obstacle.coordinates.x - player.coordinates.x
            delta_y = - (obstacle.coordinates.y - player.coordinates.y)  # because cartesian but upside down

            obstacle_direction = self._direction_degrees(delta_y, delta_x)
            delta_direction = self._direction_delta(obstacle_direction, player.direction)

            distance_to_obstacle = player.coordinates.calculate_distance(obstacle.coordinates)

            screen_state.append(distance_to_obstacle/c.WINDOW_SIZE*2)
            screen_state.append(delta_direction/180)

        screen_state_size = len(screen_state)
        if screen_state_size < self.machine_gaming_controller.input_size:
            screen_state += [0] * (self.machine_gaming_controller.input_size - screen_state_size)

        output_vector, buttons = self.game_controller.calculate_buttons(neural_network=neural_network,
                                                                        input_vector=screen_state)

        if self.game_controller.current_game is not None:
            self._update_stats(self.machine_gaming_controller.get_current_generation(),
                               self.machine_gaming_controller.get_current_network(),
                               self.game_controller.current_game.score,
                               output_vector)

        return buttons
    #  Counts only networks from basic population - children get accounted only if they survive
    def _update_scores(self, score):
        current_network_number = self.machine_gaming_controller.get_current_network()
        current_generation_number = self.machine_gaming_controller.get_current_generation()
        population_size = self.machine_gaming_controller.ea.get_population_size()

        if current_network_number < population_size:
            self._compare_scores(score)
        elif current_network_number == population_size:
            self._compare_scores(score)
            self._update_plot_stats(generation=current_generation_number,
                                    gen_best=self.curr_gen_best,
                                    gen_avg=self.curr_gen_total_score/population_size)
            self._update_plots()
            self.curr_gen_total_score = 0
            self.curr_gen_best = 0

    def _compare_scores(self, score):
        if score > self.curr_gen_best:
            self.curr_gen_best = score
        if score > self.best_score_overall:
            self.best_score_overall = score
        self.curr_gen_total_score += score

    def _update_plot_stats(self, generation, gen_best, gen_avg):
        self.best_gen_score_y.append(gen_best)
        self.best_gen_score_x.append(generation)
        self.mean_gen_score_y.append(gen_avg)
        self.mean_gen_score_x.append(generation)

    def _update_plots(self):
        self._clear_plots()
        self.best_gen_score.plot(self.best_gen_score_x, self.best_gen_score_y)
        self.mean_gen_score.plot(self.mean_gen_score_x, self.mean_gen_score_y)
        self.best_gen_score.set_title(labels.plot_title[0])
        self.best_gen_score.set_xlabel(labels.plot_xlabel)
        self.mean_gen_score.set_title(labels.plot_title[1])
        self.mean_gen_score.set_xlabel(labels.plot_xlabel)
        self.canvas._draw_range()

    def _reset_plots(self):
        self._clear_plots()
        self.best_gen_score_x = []
        self.mean_gen_score_x = []
        self.best_gen_score_y = []
        self.mean_gen_score_y = []
        self._update_plots()

    def _clear_plots(self):
        self.mean_gen_score.clear()
        self.best_gen_score.clear()

    @staticmethod
    def _direction_degrees(y, x):
        direction_rad = math.atan2(y, x)
        if direction_rad >= 0:
            return math.degrees(direction_rad)
        else:
            return math.degrees(2*math.pi + direction_rad)

    @staticmethod
    def _direction_delta(x, y):
        return -((x-y) % 360 + 180) % 360 - 180


machine_gaming = MachineGamingWindow()


if __name__ == '__main__':
    machine_gaming.run()
