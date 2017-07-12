import random

from string   import ascii_uppercase, ascii_lowercase

from deap import base
from deap import creator
from deap import tools
from deap import algorithms

import strategy

TARGET = 'Explicit is better than implicit.'

VALID  = ascii_uppercase + ascii_lowercase + ' .'

def random_letter():
    return random.choice(VALID)
    
def update(generation, population, fittest):
    fittest = ''.join(fittest[0])
    print('{:>3}.{}'.format(generation, fittest))
    return fittest == TARGET
    
def evaluate(individual):
    return (sum([individual[i] != TARGET[i] for i in range(len(TARGET))]),)
    
def mutate(individual, gene_mutation_chance):
    for i in range(len(individual)):
        if random.random() < gene_mutation_chance:
            individual[i] = random_letter()
    return individual,


creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
creator.create("Individual", list, fitness=creator.FitnessMin)

toolbox = base.Toolbox()
toolbox.register("gene", random_letter)
toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.gene, n=len(TARGET))
toolbox.register("population", tools.initRepeat, list, toolbox.individual)
toolbox.register("evaluate", evaluate)
toolbox.register("mate", tools.cxTwoPoint)
toolbox.register("mutate", mutate, gene_mutation_chance=0.05)
toolbox.register("select", tools.selTournament, tournsize=3)

population = toolbox.population(n=300)
crossover_prob = 0.5
mutation_prob  = 0.2

fittest = tools.HallOfFame(1)

population = strategy.simple(population, 
                             toolbox,
                             cxpb       = crossover_prob,
                             mutpb      = mutation_prob,
                             ngen       = 500,
                             halloffame = fittest,
                             report     = update,
                             interval   = 0.1)
                

