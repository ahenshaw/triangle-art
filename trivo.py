#!/usr/bin/python3
# standard library
import random
import time
import sys
import argparse

# third-party libraries
import wx
import numpy
import arrow
from deap import base
from deap import creator
from deap import tools
from deap import algorithms

# custom modules
import strategy
import database
from arena import Arena


DEFAULT_NUM_TRIANGLES = 100
DB_FILE = 'data/results.db'


class Trivolution:
    def __init__(self, 
                 image_fn, 
                 description     = None, 
                 num_triangles   = DEFAULT_NUM_TRIANGLES,
                 population_size = 100):
        
        # to use some of the wx drawing capabilities, must declare the wx.App first
        self.app = wx.App(redirect=False)
        
        ref_image            = wx.Image(image_fn)
        description          = description or image_fn
        self.num_triangles   = num_triangles
        self.population_size = population_size
        self.best_fitness    = 1e100 # exceeding large number

        # insert problem description into database
        self.db         = database.Database(DB_FILE)
        image           = ref_image.GetData()
        width, height   = ref_image.GetSize()
        self.info_id    = self.db.writeInfo(self.num_triangles, 3, width, height, description, image)
        
        # create the wxImage "arena" where individuals are evaluated for fitness
        self.arena = Arena(ref_image)
        
        self.start_time = time.time()
        print()
        print('Generation  Elapsed      Fitness')
        print('----------  -----------  -------------')
    
    def phenotype(self, individual):
        return numpy.array(individual).reshape(-1, 10)
    
    def evaluate(self, individual):
        fitness = self.arena.getFitness(self.phenotype(individual))
        return (fitness,)
        
    def update(self, generation, population, fittest):
        elapsed = time.time() - self.start_time
        fitness, = fittest[0].fitness.values
        if fitness >= self.best_fitness:
            # stuck on previous best result
            return
            
        self.best_fitness = fitness
        sys.stdout.write('\r{:10}  {}  {}'.format(generation, 
                                             arrow.get(elapsed).format('HH:mm:ss.SS'), 
                                             fitness))
        
        image = self.arena.render(self.phenotype(fittest[0]))
        image.SaveFile('output/last.png', wx.BITMAP_TYPE_PNG)

        bytes = numpy.array(fittest[0]).tostring()
        self.db.writeResults(self.info_id, generation, elapsed, fitness, bytes)
        
    def mutate(self, individual):
        individual[random.randint(0, len(individual)-1)] = random.random()
                
    def start(self):
        num_floats = self.num_triangles * 10 # 2 for each vertex of triangle, plus 4 for RGBA
        
        creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
        creator.create("Individual", list, fitness=creator.FitnessMin)

        toolbox = base.Toolbox()
        toolbox.register("gene",       random.random)
        toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.gene, n=num_floats)
        toolbox.register("population", tools.initRepeat, list, toolbox.individual)
        toolbox.register("evaluate",   self.evaluate)
        toolbox.register("mate",       tools.cxTwoPoint)
        toolbox.register("mutate",     self.mutate)
        toolbox.register("select",     tools.selTournament, tournsize=3)

        self.population = toolbox.population(n=self.population_size)
        crossover_prob  = 0.5
        mutation_prob   = 0.3

        self.fittest = tools.HallOfFame(1)

        self.population = strategy.simple(self.population, 
                                          toolbox,
                                          cxpb       = crossover_prob,
                                          mutpb      = mutation_prob,
                                          ngen       = 100000,
                                          halloffame = self.fittest,
                                          report     = self.update,
                                          interval   = 1)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('filename', help='file path to reference image')
    parser.add_argument('-d', default=None, help='helpful description of image')
    parser.add_argument('-n', default=100, type=int, help='number of triangles to use')
    parser.add_argument('-p', default=100, type=int, help='population size')
    args = parser.parse_args()
    
    ga = Trivolution(args.filename, description=args.d, num_triangles=args.n, population_size=args.p)
    ga.start()
    