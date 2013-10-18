#import numpy as np
#from matplotlib import pyplot
#from math import sin, pi
#
#t = np.arange(0.0, 2*pi, 0.01)
#
##pyplot.plot([1,2,3,4], [1,4,9,16], 'ro')
#
#colors = ['red', 'blue', 'green']
#
#for i in range(1,4):
#    pyplot.figure(1)
#    pyplot.subplot(111)
#    pyplot.plot(t, np.sin(i*t), 'k', color=colors[i-1])
#
#pyplot.show()

from SineFitter import *
from pylab import *
import math
import time

def run(targets, pop=20, chrom_length=20):    
    
    ion()
    
    x = arange(-0.5,2*pi+0.5,0.01)
    p = plot(x,sin(x))[0]
    lines = []
    funcs = []
    
    subplot(111).scatter([i[0] for i in targets], [i[1] for i in targets], s=40, c='r', marker='s', faceted=False)
    
    population = make_population(pop, chrom_length)
    generations = 1
    not_done = True
    force_quit = False
    while not_done:
        print '\nGeneration: %s (%s individuals)' % (generations, len(population))
        print '%s%s%s' % ('Chromosome'.rjust(RJUST), 'Result'.rjust(RJUST), 'Fitness'.rjust(RJUST))
        not_done, population = sort_by_fitness_score(population, targets)
        
        if generations > 500:
            force_quit = True
        
        if not_done and not force_quit:
            
            #x = arange(0,2*pi,0.01)
            #p = plot(x,sin(x))[0]
            
            lines = lines[:3]
            funcs = funcs[:3]
            
            lines.append(p)
            funcs.append(eval(decode(population[0])))
            lines[-1].set_ydata(funcs[-1])
            draw()
            #time.sleep(0.1)
            
            population = breed_population(population)
        else:
            where = -1
            if force_quit:
                where = 0
#            funcs.append(eval(decode(population[where])))
#            lines[where].set_ydata(funcs[where])
#            draw()
            
            print 'Solution found!'
            d = decode(population[where])
            print '%s = %s' % (d, eval_expr(d, targets))
            print 'is the best fit solution for the given data.' % targets
            return generations, d
            draw()
        generations += 1

t_nums = [(0,0), (3.14159265,0), (3.14159265/2,1), (1,0.8414709848), (0.5, math.sin(0.5)), (0.125, math.sin(0.125)), (2, math.sin(2)), (2.222, math.sin(2.222))]
#t_nums = [(0,5.656109524),(0.125,6.571246075),(0.5,6.579648727),(0.75,4.439270321),(1,1.631225069),(1.5,-1.07189572),(0.0,-0.866740149),(1.77,0.463706974),(2.005,2.961717229),(2.5111,7.061367317),(2.8,6.331452804),(2.999,4.558199698),(3.0,4.547581829),(3.14159265359,2.963513504),(3.201,2.286204254),(4.44,4.8923108),(5.123,5.858372014),(6,-1.101888451),(6.28318530718,0.400117144)]
generations, winner = run(targets=t_nums, chrom_length=12)
print 'Generations: %s, Winner: %s' % (generations, winner)
time.sleep(60)


#ion()
#
#lines = []
#funcs = []
#for i in range(5):
#    x = arange(0,2*pi,0.01)
#    b = [sin(x), sin(2*x), sin(3*x), sin(4*x), sin(5*x)]
#    p = plot(x,cos(x))[0]
#    
#    lines[:2]
#    funcs[:2]
#    
#    lines.append(p)
#    funcs.append(b[i])
#    lines[-1].set_ydata(funcs[-1])
#    draw()
#    time.sleep(1)
#time.sleep(3)
