import numpy as np
import math
import operator

class HypotesisTerm():
    def __init__(self, weight, stump_column, stump_function):
        self.weight = weight
        self.stump_column = stump_column
        self.stump_function = stump_function

        print "weight"
        print self.weight
        print self.stump_column

    def evaluate_term(self, evaluate_array):
        return self.weight * self.stump_function(evaluate_array[self.stump_column])

class AdaBoostClassifier():
    def __init__(self,maximum_iterations):
        self.maximum_iterations = maximum_iterations
        self.model_terms = []

    def fit(self, X, y):
        self.__generate_stump_combinations(X)
        self.__generate_value_weights(X)
        for iteration in xrange(self.maximum_iterations):
            self.__iterate_training(X, y)

    def __generate_stump_combinations(self, X):
        self.stump_combinations = [(column,column_value) for column in range(X.shape[1]) for column_value in range(3)]

    def __generate_value_weights(self, X):
        line, columns = X.shape
        self.value_weights = np.ones((line)) * 1/float(line)

    def __iterate_training(self, X, y):
        
        min_weighted_error = float("Inf")
        selected_function = None
        column_selected = None
        x_stump_column_selected = None

        for stump_column, stump_column_value in self.stump_combinations:
            stump_functions = self.__generate_stump_functions(stump_column_value)
            x_stump_column = X[:, stump_column]
            weighted_error, choosen_stump_function = self.__get_weighted_error(x_stump_column, y, stump_functions)
        
            if weighted_error < min_weighted_error:
                min_weighted_error = weighted_error
                selected_function = choosen_stump_function
                column_selected = stump_column
                x_stump_column_selected = x_stump_column

        self.__append_model_term(min_weighted_error, column_selected, selected_function)
        self.__update_value_weights(min_weighted_error, y, selected_function, x_stump_column_selected)

    def __generate_stump_functions(self, value_condiction):
        positive_stump = lambda x: 1 if x == value_condiction else 0
        negative_stump = lambda x: 0 if x == value_condiction else 1
        return(positive_stump, negative_stump)

    def __get_weighted_error(self, x_stump_column, y, stump_functions):
        min_weighted_error = float("Inf")
        choosen_stump_function = None
        
        for function_number, stump_function in enumerate(stump_functions):
            weighted_error = 0.0
            for index, x_value in enumerate(x_stump_column):
                if stump_function(x_value) == y[index]:
                    weighted_error += self.value_weights[index]
            weighted_error = weighted_error/sum(self.value_weights)
            if weighted_error < min_weighted_error:
                min_weighted_error = weighted_error
                choosen_stump_function = stump_function

        return min_weighted_error, choosen_stump_function
    
    def __append_model_term(self, weighted_error, column, stump_function):
        weight = (1.0/2.0) * math.log10((1.0 - weighted_error)/(weighted_error))
        self.model_terms.append(HypotesisTerm(weight, column, stump_function))

    def __update_value_weights(self, weighted_error, y, stump_function, x_column):

        self.__calculate_value_weights(weighted_error, y, stump_function, x_column)
        self.__normalize_value_weights()

    def __calculate_value_weights(self, weighted_error, y, stump_function, x_column):
        for index, value_weight in enumerate(self.value_weights):
            if stump_function(x_column[index]) == y[index]:
                self.value_weights[index] = value_weight * math.exp(-weighted_error)
            if stump_function(x_column[index]) != y[index]:
                self.value_weights[index] = value_weight * math.exp(weighted_error)

    def __normalize_value_weights(self):
        value_weights_sum = sum(self.value_weights)
        self.value_weights = map(lambda x: x/value_weights_sum, self.value_weights)

    def predict(self, X):
        X = np.array(list(X))
        
        predicts = []
        for x in X:
            predicts.append(reduce(operator.add, map(lambda y: y.evaluate_term(X), self.model_terms)))
        return np.asarray(predicts)

def parse_data(element):
    if element == 'b' or element == 'negative':
        return 0
    if element == 'x' or element == 'positive':
        return 1
    if element == 'o':
        return 2

def parse_matrix(data_array):
    return np.vectorize(parse_data)(data_array)

# Read dataset from txt
data = np.genfromtxt("../data/tic-tac-toe.data.txt", delimiter=",", dtype=None)

# Convert data
parsed_data = parse_matrix(data)

model = AdaBoostClassifier(50)

X = parsed_data[:, :-1]
y = parsed_data[:, -1]

model.fit(X, y)

print model.predict(parsed_data[626, :-1])