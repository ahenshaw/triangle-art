import random
from operator import attrgetter
import time

def simple(population, 
           toolbox,
           report     = None,
           interval   = 0.0,
           cxpb       = 0.0, 
           mutpb      = 0.0, 
           ngen       = 300, 
           halloffame = None, 
           verbose    = False):
               
    fittest     = None
    next_report_time = time.time()

    # Begin the evolution
    for generation in range(ngen):
        # Select the next generation individuals
        offspring = toolbox.select(population, len(population))
        
        # Clone the selected individuals
        offspring = list(map(toolbox.clone, offspring))
        
        # Apply crossover and mutation on the offspring
        for child1, child2 in zip(offspring[::2], offspring[1::2]):
            if random.random() < cxpb:
                toolbox.mate(child1, child2)
                del child1.fitness.values
                del child2.fitness.values

        for individual in offspring:
            if random.random() < mutpb:
                toolbox.mutate(individual)
                del individual.fitness.values
                
        # Evaluate the individuals with an invalid fitness
        invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
        fitnesses = map(toolbox.evaluate, invalid_ind)
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit
        population[:] = offspring

        if report is not None:
            if time.time() >= next_report_time:
                next_report_time += interval
                # Identify the most fit individual
                #~ fittest = sorted(population, key=attrgetter('fitness.values'))[0]
                halloffame.update(population)
                if report(generation+1, population, halloffame):
                    break
    
    halloffame.update(population)
    return population
