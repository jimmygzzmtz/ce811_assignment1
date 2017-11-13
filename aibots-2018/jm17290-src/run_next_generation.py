from genetic_algorithm import Population, ResGenotype, SpyGenotype

# J.Madge 05.11.2017 'promote' and 'tournament_num' must add up to the population size.
promote = 3  # J.Madge 05.11.2017 Number of genes to automatically advance to the next generation.
tournament_num = 17  # J.Madge 05.11.2017 Number of tournaments to select remaining member of the population.
tournament_size = 4  # J.Madge 05.11.2017 Number of genes to be randomly selected for each tournament.

# J.Madge 05.11.2017 Cross at points to share selection/vote/sabotage strategies.
res_cross_pos = [7, 15]
spy_cross_pos = [6, 18, 25]

res_mutations = 3  # J.Madge 05.11.2017 Number of mutations in child Resistance genes.
spy_mutations = 5  # J.Madge 05.11.2017 Number of mutations in child Spy genes.
mutation_lower = 0.8  # J.Madge 05.11.2017 Lower limit of the mutation operator.
mutation_upper = 1.2  # J.Madge 05.11.2017 Upper limit of the mutation operator.

p = Population()
current_gen = p.gen()
next_gen = current_gen + 1

# J.Madge 06.11.2017 Select the best Resistance and best Spy to represent this generation.
best_res = p.top(1, current_gen, ResGenotype.Type)[0]
best_res.set_index(current_gen)
p.insert(best_res, 'Best')
best_spy = p.top(1, current_gen, SpyGenotype.Type)[0]
best_spy.set_index(current_gen)
p.insert(best_spy, 'Best')

# J.Madge 05.11.2017 Create database for the next generation.
p.create(next_gen)

# J.Madge 05.11.2017 RESISTANCE: Create the next generation.
res_next_gen_genes = []
res_next_gen_genes += p.top(promote, current_gen, ResGenotype.Type)
for i in xrange(tournament_num):
    parent1 = p.tournament(tournament_size, current_gen, ResGenotype.Type)
    parent2 = p.tournament(tournament_size, current_gen, ResGenotype.Type)
    child = parent1.crossover(parent2, res_cross_pos, ResGenotype.Type)
    child.mutate(res_mutations, mutation_lower, mutation_upper)
    res_next_gen_genes.append(child)

for i, g in enumerate(res_next_gen_genes):
    g.reset_data(i)
    p.insert(g, next_gen)

# # J.Madge 05.11.2017 SPY: Create the next generation.
spy_next_gen_genes = []
spy_next_gen_genes += p.top(promote, current_gen, SpyGenotype.Type)
for i in xrange(tournament_num):
    parent1 = p.tournament(tournament_size, current_gen, SpyGenotype.Type)
    parent2 = p.tournament(tournament_size, current_gen, SpyGenotype.Type)
    child = parent1.crossover(parent2, spy_cross_pos, SpyGenotype.Type)
    child.mutate(spy_mutations, mutation_lower, mutation_upper)
    spy_next_gen_genes.append(child)

for i, g in enumerate(spy_next_gen_genes):
    g.reset_data(i)
    p.insert(g, next_gen)

p.set_gen(next_gen)
