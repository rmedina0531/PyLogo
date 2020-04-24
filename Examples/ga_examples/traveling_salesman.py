from core.ga import GA_World, Individual, Chromosome
from typing import Tuple

'''Solve using the greedy algorithm'''
'''solve using the min spanning tree algorithm'''


'''find the minimum spanning tree'''
'''find upper bound and lower bound for the route, '''
'''2-opt algorithm'''

class TSChromosome(Chromosome):
    def chromosome_fitness(self) -> float:
        '''for each entry in the chromosome, find the length'''
        pass


class Route(Individual):


    def mate_with(self, other) -> Tuple[Individual, Individual]:
        pass
    def mutate(self) -> Individual:
        pass


class TSWorld(GA_World):
    def __init__(self):
        pass