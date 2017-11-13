from genetic_algorithm import Population

initial_generation = 0  # J.Madge 05.11.2017 Number of the initial generation.
population_size = 20  # J.Madge 05.11.2017 Number of genotypes in the population.

initialise_lower_bound = 0.4  # J.Madge 05.11.2017 Lowest initial values a gene can be initialized to.
initialise_upper_bound = 0.6  # J.Madge 05.11.2017 Highest initial values a gene can be initialized to.

p = Population()

# J.Madge 05.11.2017 Set the population state (size of the population, number of the initial generation).
p.create_state()
p.set_size(population_size)
p.set_gen(initial_generation)

# J.Madge 05.11.2017 Create the initial generation and initialize the contained genotypes to the lower and upper bounds.
p.create(initial_generation)
p.create('Best')
p.initialise(initial_generation, initialise_lower_bound, initialise_upper_bound)
