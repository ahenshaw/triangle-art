import random
import numpy
from numpy import sin, pi

from deap import base
from deap import creator
from deap import tools
from deap import algorithms

import strategy

N = 3
#~ def f(x, y):
    #~ return ((10*x*y*(1-x)*(1-y)*sin(N*pi*x)*sin(N*pi*y))**2)

    
def evaluate(individual):
    x, y = individual
    return (f(x, y),)
    
def run(evaluate_fn, population_size):
    def update(generation, population, fittest):
        x, y = fittest[0]
        #~ print('{:>3}. {} {} {}'.format(generation, x, y, f(x, y)))
        results.append(population.copy())
    creator.create("FitnessMax", base.Fitness, weights=(1.0,))
    creator.create("Individual", list, fitness=creator.FitnessMax)

    toolbox = base.Toolbox()
    toolbox.register("gene", random.random)
    toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.gene, n=2)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)
    toolbox.register("evaluate", evaluate_fn)
    toolbox.register("mate", tools.cxTwoPoint)
    toolbox.register("mutate", tools.mutGaussian, mu=0.0, sigma=0.1, indpb=0.5)
    toolbox.register("select", tools.selTournament, tournsize=3)

    population = toolbox.population(n=population_size)
    results = [population.copy()]
    crossover_prob = 0.5
    mutation_prob  = 0.2

    fittest = tools.HallOfFame(1)

    population = strategy.simple(population, 
                                 toolbox,
                                 cxpb       = crossover_prob,
                                 mutpb      = mutation_prob,
                                 ngen       = 1000,
                                 halloffame = fittest,
                                 report     = update)
    return results            
