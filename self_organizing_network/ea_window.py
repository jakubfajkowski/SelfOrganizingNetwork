import math
import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib import style
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from self_organizing_network.ea_controller import EAController
from self_organizing_network.simulation_controller import SimulationController
import self_organizing_network.labels as labels
import self_organizing_network.utils as c


matplotlib.rcParams.update({'font.size': 8})
matplotlib.use('TkAgg')
style.use('dark_background')


class EAWindow(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.wm_title(labels.title)
        self.resizable(0, 0)
        self.son_controller = EAController(stats_window=self)
        self.sim_controller = SimulationController(stats_window=self)

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
        self.protocol("WM_DELETE_WINDOW", self._quit)
        self.mainloop()

    def start(self, headless):
        if self.son_controller.ea is not None:
            if self.sim_controller.current is not None:
                self.stop()
            self.sim_controller.start(headless=headless)
        else:
            messagebox.showwarning(labels.msgbox_title[0], labels.msgbox_msg[0])

    def stop(self):
        self.speed_slider.set(1)
        if self.sim_controller.current is not None:
            self.sim_controller.stop()

    def _add_controls(self):
        buttons_callbacks = [lambda: self.start(headless=True),
                             lambda: self.start(headless=False),
                             self.stop, self.sim_controller.change_view,
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
                                     from_=1, to=10, resolution=0.1, command=self.sim_controller.change_speed)
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
            command=lambda: [self.son_controller.initialize_ea(self._extract_str_from_entries(entries)),
                             self._update_ea_parameters(self._extract_str_from_entries(entries)),
                             self._reset_plots(),
                             param_frame.destroy()])
        create_button.grid(row=10, column=0, columnspan=2)

    @staticmethod
    def _extract_str_from_entries(entries):
        return [e.get() for e in entries]

    def _update_ea_parameters(self, parameters):
        for i in range(len(parameters)):
            self.eap_label_vars[i].set(labels.params[i] + str(parameters[i]))

    def _update_stats(self, current_gen_num, current_nn_num, current_score, current_output):
        current_probs = [(x, round(y, 2)) for x, y in zip(["+", "-"], current_output)]

        current_stats = [current_gen_num,
                         current_nn_num,
                         current_score,
                         self.best_score_overall,
                         current_probs]

        for i in range(len(self.stat_label_vars)):
            self.stat_label_vars[i].set(labels.stats[i] + str(current_stats[i]))

    def _quit(self):
        if self.sim_controller.current is not None:
            messagebox.showwarning(labels.msgbox_title[3], labels.msgbox_msg[5])
        else:
            self.stop()
            self.quit()
            self.destroy()

    def _set_path_and_save(self):
        path = filedialog.asksaveasfilename(filetypes=labels.mg_filetype, initialfile=labels.initialfilename)
        if len(path) is 0:  # dialog closed with "cancel".
            return
        if self.son_controller.save(path):
            messagebox.showinfo(labels.msgbox_title[1], labels.msgbox_msg[1])
        else:
            messagebox.showwarning(labels.msgbox_title[1], labels.msgbox_msg[2])

    def _set_path_and_load(self):
        path = filedialog.askopenfilename(filetypes=labels.mg_filetype)
        if len(path) is 0:  # dialog closed with "cancel".
            return
        success, parameters = self.son_controller.load(path)
        if success:
            self._update_ea_parameters(parameters)
            self._reset_plots()
            messagebox.showinfo(labels.msgbox_title[2], labels.msgbox_msg[3])
        else:
            messagebox.showwarning(labels.msgbox_title[2], labels.msgbox_msg[4])

    def on_finish(self):
        current_score = self.sim_controller.current.score
        self._update_scores(current_score)
        self.son_controller.neural_network.fitness = current_score
        self.son_controller.process()

    def on_tick(self, base_station, mobile_stations):
        neural_network = self.son_controller.neural_network
        if neural_network is None:
            return

        sim_state = []

        if base_station.is_on():
            sim_state.append(base_station.get_power())
        else:
            sim_state.append(0)

        for neighbour in base_station.get_neighbours():
            if neighbour.is_on():
                sim_state.append(base_station.get_power())
            else:
                sim_state.append(0)

        # for ms in mobile_stations:
        #     if ms.base_station is base_station:
        #         sim_state.append(ms.power)
        #     else:
        #         sim_state.append(0)

        self._fill_with_zeros(sim_state)

        output_vector = self.sim_controller.predict_power_change(neural_network=neural_network,
                                                                 input_vector=sim_state)

        # print("INPUT: ", sim_state)
        # print("OUTPUT: ", output_vector)

        if self.sim_controller.current is not None:
            self._update_stats(self.son_controller.get_current_generation(),
                               self.son_controller.get_current_network(),
                               self.sim_controller.current.score,
                               output_vector)

        POWER_RESOLUTION = 100
        predicted_power_change = (output_vector[0] - output_vector[1]) * POWER_RESOLUTION

        return predicted_power_change
    # Counts only networks from basic population - children get accounted only if they survive

    def _fill_with_zeros(self, input_vector):
        input_vector_size = len(input_vector)
        if input_vector_size < self.son_controller.input_size:
            input_vector += [0] * (self.son_controller.input_size - input_vector_size)

    def _update_scores(self, score):
        current_network_number = self.son_controller.get_current_network()
        current_generation_number = self.son_controller.get_current_generation()
        population_size = self.son_controller.ea.get_population_size()

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
        self.canvas.draw()

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


machine_gaming = EAWindow()


if __name__ == '__main__':
    machine_gaming.run()
