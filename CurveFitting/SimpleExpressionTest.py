'''
Created on Jun 14, 2011

@author: crawfonw

References:
	http://www.ai-junkie.com/ga/intro/gat3.html
	http://lethain.com/genetic-algorithms-cool-name-damn-simple/
	http://stackoverflow.com/questions/326300/python-best-library-for-drawing
'''

import random

'''
    Constants, etc.
'''

RJUST = 30
VERBOSE = True

MAXPOP = 10000

NUMS = '0123456789'
OPS = '+-*/'

GENES = {
            '0' : '0000',
            '1' : '0001',
            '2' : '0010',
            '3' : '0011',
            '4' : '0100',
            '5' : '0101',
            '6' : '0110',
            '7' : '0111',
            '8' : '1000',
            '9' : '1001',
            '+' : '1010',
            '-' : '1011',
            '*' : '1100',
            '/' : '1101',
        }

KEYS = GENES.keys()
VALUES = GENES.values()

'''
    Encoding/decoding/evaluation methods.
'''
def encode(expr):
    ret = []
    for e in expr:
        ret.append(GENES[e])
    return ret

def decode(chrom):
    ret = ''
    last = '~'
    seq_val = None
    for seq in chrom:
        try:
            seq_val = KEYS[VALUES.index(seq)]
        except ValueError:
            seq_val = None #value not in dictionary
        if last and seq_val and ((last in NUMS and seq_val in NUMS) or (last in OPS and seq_val in OPS)):
            seq_val = None #garbage input
        if seq_val:
            last = seq_val
            ret += seq_val
    if ret != '': #if is empty string, we have invalid number/operators
        if ret[0] == '*' or ret[0] == '/': #remove invalid starting operators
            ret = ret[1:]
        if last in OPS: #remove any trailing operators
            ret = ret[:-1]
        if len(ret) == 1 and ret[0] in OPS: #completely broken solution (single operator)
            ret = ''
    return ret

def eval_expr(expr):
    f_expr = ''
    ret = None
    for e in expr:
        if e in NUMS:
            f_expr += str(float(e))
        else:
            f_expr += e
    try:
        ret = eval(f_expr)
    except ZeroDivisionError:
        ret = 'inf'
    except SyntaxError:
        ret = 'nil'
    return ret

'''
    Population/generation methods.
'''
def make_population(pop_size=20, chrom_length=20):
    pop = []
    for i in range(pop_size):
        new_chrom = []
        for j in range(chrom_length):
            new_chrom.append(VALUES[random.randrange(14)])
        pop.append(new_chrom)
    return pop

def find_fitness_score(chrom, target):
    ret = 0
    pheno = decode(chrom)
    e = eval_expr(pheno)
    if e == 'inf' or e == 'nil':
        ret = 0
    else:
        try:
            ret = 1 / abs((e - target))
        except ZeroDivisionError:
            ret = -1 #solution!
    if VERBOSE:
        print '%s = %s : %s' % (pheno.rjust(RJUST), str(e).rjust(RJUST), str(ret).rjust(RJUST))
    return ret

def sort_by_fitness_score(pop, target):
    no_solution = True
    tuple_list = []
    for chrom in pop:
        tuple_list.append((find_fitness_score(chrom, target), chrom))
    tuple_list.sort()
    tuple_list.reverse()
    if tuple_list[-1][0] == -1: #if the last has fitness of -1, we have a solution
        no_solution = False
    sorted_list = []
    for e in tuple_list:
        sorted_list.append(e[-1])
    return (no_solution, sorted_list)

def breed_population(pop):
    parents = pop[:len(pop)/4] #pull out the fittest
    weak = pop[len(pop)/4:] #and the weakest
    for i in weak: #sprinkle in a few weak individuals for diversity (helps to avoid sticking at local maximas)
        if random.random() <= 0.05:
            parents.append(i)
    new_pop = parents
    for i in range(len(pop)):
        new_pop.append(roulette_wheel(parents))
    '''
    Here we try to prune the population. 
    This turns out to cause frequent hangs if
    the max is too low for the desired number.
    '''
    if len(new_pop) >= MAXPOP:
        new_pop = new_pop[:MAXPOP]
    
    return new_pop

def roulette_wheel(pop):
    #pick two to cross
    parent1 = None
    parent2 = None
    while parent1 == parent2: #make sure they aren't the same
        parent1 = random.choice(pop)
        parent2 = random.choice(pop)
    
    #and breed them
    child1, child2 = crossover(parent1, parent2)
    child1 = mutate(child1)
    child2 = mutate(child2)
    return random.choice([child1, child2])

def crossover(chrom1, chrom2):
    breakpoint = random.randint(1, len(chrom1) - 1) #starting at 1 and len() - 1 prevents creating duplicates of parents. This is not cloning!
    return (chrom1[breakpoint:] + chrom2[:breakpoint], chrom2[breakpoint:] + chrom1[:breakpoint])

def mutate(chrom):
    new_chrom = []
    for hex in chrom:
        for bit in hex:
            temp = ''
            chance = float(random.randint(0, 1000)) / 10000
            if chance <= 0.001:
                if bit == '0':
                    temp += '1'
                else:
                    temp += '0'
                new_chrom.append(temp)
            else:
                new_chrom.append(hex)
    return chrom

def run(target, pop=20):
    population = make_population(pop)
    generations = 1
    not_done = True
    while not_done:
        if VERBOSE:
            print '\nGeneration: %s (%s individuals)' % (generations, len(population))
            print '%s%s%s' % ('Phenotype'.rjust(RJUST), 'Result'.rjust(RJUST), 'Fitness'.rjust(RJUST))
        not_done, population = sort_by_fitness_score(population, target)
        if not_done:
            population = breed_population(population)
        else:
            print 'Solution found for %s' % target
            return generations, decode(population[-1])
        generations += 1

def run_multiple(target, pop=20, num_trials=50):
    completed = 0
    gen_sol = []
    while completed < num_trials:
        population = make_population(pop)
        generations = 1
        not_done = True
        while not_done:
            not_done, population = sort_by_fitness_score(population, target)
            if not_done:
                population = breed_population(population)
            else:
                gen_sol.append((generations, decode(population[-1])))
            generations += 1
        if completed % 5 == 0:
            print '%s iterations complete' % completed
        completed += 1
            
    average = 0
    average_length = 0
    low = gen_sol[0][0]
    high = -1
    shortest = gen_sol[0][1]
    longest = ''
    print "\nExpressions of %s:\n%s%s" % (target, 'Generations'.center(RJUST), 'Phenotype'.center(RJUST))
    for e in gen_sol:
        n = e[0]
        ln = e[1]
        average += n
        if n > high:
            high = n
        if n < low:
            low = n
        
        average_length += len(ln)
        if len(ln) > len(longest):
            longest = ln
        if len(ln) < len(shortest):
            shortest = ln
            
        print '%s%s' % (str(n).center(RJUST), ln.center(RJUST))
    print 'Average # of Generations: %s\nLowest # of Generations: %s\nHighest # of Generation: %s' % (float(average) / num_trials, low, high)
    print 'Average Length of Solution: %s\nShortest Length of Solution: %s [%s]\nLongest Length of Solution: %s [%s]' % (float(average_length) / num_trials, len(shortest), shortest, len(longest), longest)
        

if __name__ == "__main__":
    multi_trial = False
    t_num = input('Enter target number\n')
    if multi_trial:
        VERBOSE = False
        run_multiple(target=t_num, pop=20, num_trials=1000)
    else:
        #VERBOSE = False
        generations, winner = run(target=t_num, pop=20)
        print 'Generations: %s\nPhenotype Solution: %s' % (generations, winner)
