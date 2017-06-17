import self_organizing_network.pyvolution as pv


class SONController:
    def __init__(self, stats_window):
        self.stats_window = stats_window
        self.input_size = 0
        self.neural_network = None
        self.ea = None

    def initialize_ea(self, parameters):
        p = pv.EvolutionaryAlgorithmParameters
        p.population_size = int(parameters[0])
        p.children_bred_per_generation = int(parameters[1])
        p.crossover_probability = float(parameters[2])
        p.mutation_probability = float(parameters[3])
        p.hidden_layers = int(parameters[4])
        p.input_size = 13
        p.output_size = 5
        p.weight_variance = float(parameters[5])
        self.ea = pv.EvolutionaryAlgorithm(p)
        self.input_size = p.input_size
        self.process()

    def get_current_network(self):
        return self.ea.get_current_network()

    def get_current_generation(self):
        return self.ea.get_current_generation()

    def process(self):
        self.neural_network = self.ea.get_next()

    def save(self, path):
        if self.ea:
            self.ea.save(path)
            return True
        else:
            return False

    def load(self, filename):
        self.ea = pv.EvolutionaryAlgorithm()
        self.ea.load(filename)
        parameters = [self.ea.get_population_size(), self.ea.get_children_bred_per_generation(),
                      self.ea.get_crossover_probability(), self.ea.get_mutation_probability(),
                      self.ea.get_hidden_layers(), self.ea.get_weight_variance()]
        self.process()
        return True, parameters
