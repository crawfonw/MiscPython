'''
Created on Jun 15, 2011

@author: crawfonw
'''

from math import sin, pi
import random

'''
    Constants, etc.
'''

RJUST = 60
VERBOSE = True

MAXPOP = 100

DY = 0.01 #overall accuracy of fitting

NUMS = '0123456789'
OPS = '.'

EQFORM = '{0}*sin({1}*x+{2})+{3}'

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
            '.' : '1010',
        }

KEYS = GENES.keys()
VALUES = GENES.values()

'''
    Encoding/decoding/evaluation methods.
'''
def encode(lov): #list of numbers, formatted as strings
    if len(lov) > 4:
        raise ValueError
    ret = []
    for i in lov:
        temp = []
        for j in i:
            temp.append(GENES[j])
        ret.append(temp)
    return ret

def decode(chrom):
    arr = []
    for gene in chrom:
        arr.append(decode_number(gene))
    return EQFORM.format(arr[0], arr[1], arr[2], arr[3]) #TODO: find a cleaner way to do this
    

def decode_number(half_byte_array):
    num = ''
    HAS_DECIMAL = False
    for i in half_byte_array:
        try:
            next = KEYS[VALUES.index(i)]
        except ValueError:
            next = ''
        if next == '.':
            if not HAS_DECIMAL: #next is a decimal point and we're okay to add it
                num += next
                HAS_DECIMAL = True
        else:
            num += next
    if num == '.' or num == '': #everything was a decimal point...
        num = '0'
    return str(float(num))

def eval_expr(expr, lov):
    '''
        Evaluates the given expression at the given coordinates.
        expr - an expression is string format
        lov - list of tuples of decimal numbers representing coordinates in the Cartesian plane.
        
        Returns a list of f(x) float values.
    '''
    
    xs = [i[0] for i in lov] #just need the x values
    eval_y = []
    for i in xs:
        eval_y.append(eval(expr.replace('x', str(i))))
    return eval_y

'''
    Population/generation methods.
'''
def make_population(pop_size=20, chrom_length=20):
    pop = []
    for i in range(pop_size):
        pop.append(make_chromosome(chrom_length))
    return pop

def make_chromosome(length):
    ret = []
    n = length / 4 #length of each number, including decimal points
    for i in range(4):
        temp = []
        for j in range(n):
            temp.append(random.choice(VALUES))
        ret.append(temp)
    return ret

def find_fitness_score(chrom, targets, dy=DY, alg=1): #targets is a list of tuples of decimal numbers representing coordinates in the Cartesian plane
    if alg == 0:
        return fitness_by_total_sum(chrom, targets, dy)
    elif alg == 1:
        return fitness_point_by_point(chrom, targets, dy)
    else:
        raise ValueError

def fitness_by_total_sum(chrom, targets, dy):
    ret = 0
    pheno = decode(chrom)
    e = eval_expr(pheno, targets)
    
    sum_targets = sum(i[1] for i in targets)
    sum_eval = sum(e)
    diff = abs(sum_targets - sum_eval)
    
    if diff <= dy:
        ret = -1
    else:
        ret = 1 / diff
    
    if VERBOSE:
        #print '%s : %s %s' % (pheno.ljust(RJUST), str([(i[0],j) for i, j in map(None, targets, e)]).ljust(RJUST), str(ret).rjust(RJUST))
        print '%s : %s' % (pheno.ljust(RJUST), str(ret).rjust(RJUST))
    return ret

def fitness_point_by_point(chrom, targets, dy):
    ret = 0
    pheno = decode(chrom)
    e = eval_expr(pheno, targets)
    rets = []
    diff = 0
    diffs = [abs(i[1] - j) for i, j in map(None, targets, e)]
    for d in diffs:
        if d <= dy:
            rets.append(-1)
        diff += d
    if sum(rets) == -1*len(targets):
        ret = -1
    else:
        ret = 1 / diff
    
    if VERBOSE:
        #print '%s : %s %s' % (pheno.ljust(RJUST), str([(i[0],j) for i, j in map(None, targets, e)]).ljust(RJUST), str(ret).rjust(RJUST))
        print '%s : %s' % (pheno.ljust(RJUST), str(ret).rjust(RJUST))
    return ret

def sort_by_fitness_score(pop, targets):
    no_solution = True
    tuple_list = []
    for chrom in pop:
        tuple_list.append((find_fitness_score(chrom, targets), chrom))
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
    weak = pop[len(pop)/4:]
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
    
    c1_str = nested_list_to_string(chrom1)
    c2_str = nested_list_to_string(chrom2)
    breakpoint = random.randint(1, len(c1_str) - 1) #starting at 1 and len() - 1 prevents creating duplicates of parents. This is not cloning!
    
    swapped1 = string_to_nested_list(c1_str[breakpoint:] + c2_str[:breakpoint], len(chrom1[1]))
    swapped2 = string_to_nested_list(c2_str[breakpoint:] + c1_str[:breakpoint], len(chrom1[1]))
    
    return (swapped1, swapped2)

def nested_list_to_string(chromosome):
    ret = ''
    for i in chromosome:
        for j in i:
            ret += j
    return ret

def string_to_nested_list(string, length):
    l = []
    for i in range(0, len(string), length * 4):
        temp_str = string[i:i + length * 4]
        temp_lst = []
        for j in range(0, len(temp_str), 4):
            temp_lst.append(temp_str[j:j + 4])
        l.append(temp_lst)
    return l

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

def run(targets, pop=20, chrom_length=20):
    population = make_population(pop, chrom_length)
    generations = 1
    not_done = True
    while not_done:
        if VERBOSE:
            print '\nGeneration: %s (%s individuals)' % (generations, len(population))
            print '%s%s%s' % ('Chromosome'.rjust(RJUST), 'Result'.rjust(RJUST), 'Fitness'.rjust(RJUST))
        not_done, population = sort_by_fitness_score(population, targets)
        if not_done:
            population = breed_population(population)
        else:
            print 'Solution found!'
            print '%s = %s' % (decode(population[-1]), eval_expr(decode(population[-1]), targets))
            print 'is the fittest solution for %s!' % targets
            return generations, decode(population[-1])
        generations += 1

def run_multiple(targets, pop=20, chrom_length=20, num_trials=50):
    completed = 0
    gen_sol = []
    while completed < num_trials:
        population = make_population(pop, chrom_length)
        generations = 1
        not_done = True
        while not_done:
            not_done, population = sort_by_fitness_score(population, targets)
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
    print "\nExpressions of %s:\n%s%s" % (targets, 'Generations'.center(RJUST), 'Chromosome'.center(RJUST))
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
    t_nums = [(0,0), (pi,0), (pi/2,1)]
    multi_trial = False
    #t_num = input('Enter target number\n')
    if multi_trial:
        VERBOSE = False
        run_multiple(targets=t_nums)
    else:
        generations, winner = run(targets=t_nums, chrom_length=12)
        print 'Generations: %s, Winner: %s' % (generations, winner)
