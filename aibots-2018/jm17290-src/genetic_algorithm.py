from __future__ import division
from abc import ABCMeta
from collections import OrderedDict
import sqlite3
import random


class Genotype:
    """ Holds the weights of expert rules used to make decisions by JM17290(Bot). Each genotype represents a potential
    'solution' and is subject to the evolutionary optimization techniques of crossover and mutation. The Genotype class
    is the base class of ResGenotype and SpyGenotype, hence is hold data common to each such as the index, # of wins, #
    of evaluations and fitness."""

    __metaclass__ = ABCMeta

    Index = 'IDX'
    Evaluations = 'EVA'
    Win = 'WIN'
    Fitness = 'FIT'

    def __init__(self, data, genes, typ):
        self.data = data
        self.genes = genes
        self.typ = typ

    def __getitem__(self, item):
        return self.genes[item]

    def reset_data(self, idx):
        self.data[Genotype.Index] = idx
        self.data[Genotype.Evaluations] = 0
        self.data[Genotype.Win] = 0
        self.data[Genotype.Fitness] = 0.0

    def set_index(self, idx):
        self.data[Genotype.Index] = idx

    def update(self, result):
        self.data[Genotype.Evaluations] += 1
        self.data[Genotype.Win] += result
        self.data[Genotype.Fitness] = self.data[Genotype.Win] / self.data[Genotype.Evaluations]

    def crossover(self, partner, pos, typ):
        """ Crossover takes place at multiple points in the genotype as specified by the 'pos' list argument. """

        curr = 0
        cross_self = []
        cross_partner = []
        crossed_genes = []
        for i in pos:
            cross_self.append(list(self.genes.values())[curr: i])
            cross_partner.append(list(partner.genes.values())[curr: i])
            curr = i
        for i in range(len(pos)):
            # Select cross genes from alternating parents.
            if i % 2 == 0:
                crossed_genes += cross_self[i]
            else:
                crossed_genes += cross_partner[i]

        return Genotype(self.data, OrderedDict(zip(self.genes.keys(), crossed_genes)), typ)

    def mutate(self, num, lower_bound, upper_bound):
        "Mutate the genotype 'num' number of times at random position."

        for i in xrange(num):
            self.genes[random.choice(self.genes.keys())] *= random.uniform(lower_bound, upper_bound)


class ResGenotype(Genotype):
    """ Derived class of 'Genotype' holds names of database tables specific to the Resistance Genotype. """

    # Type.
    Type = 'Resistance'

    # SELECTION
    # Yes.
    PickYesPerfectRecord = 'PYPFR'
    PickYesUntested = 'PYUTD'
    PickYesFailed1Mission = 'PYF1M'
    PickYesDefault = 'PYDEF'
    # No.
    PickNoFailed1Mission = 'PNF1M'
    PickNoFailed2Missions = 'PNF2M'
    PickNoDefault = 'PNDEF'

    # VOTE.
    # Yes.
    VoteYesAttempt5 = 'VYAT5'
    VoteYesMission1 = 'VYMI1'
    VoteYesLeader = 'VYLDR'
    VoteYesDefault = 'VYDEF'
    # No.
    VoteNoNotIncludedTeam3 = 'VNNI3'
    VoteNoFailed1Mission = 'VNF1M'
    VoteNoFailed2Missions = 'VNF2M'
    VoteNoDefault = 'VNDEF'

    def __init__(self, data, genes):
        super(ResGenotype, self).__init__(data, genes, self.Type)


class SpyGenotype(Genotype):
    """ Derived class of 'Genotype' holds names of database tables specific to the Spy Genotype. """

    # Type.
    Type = 'Spy'

    # SELECTION.
    # Yes.
    PickYesPerfectRecord = 'PYPFR'
    PickYesUntested = 'PYUTD'
    PickYesDefault = 'PYDEF'
    # No.
    PickNoAreSpy = 'PNSPY'
    PickNoFailed2Missions = 'PNF2M'
    PickNoDefault = 'PNDEF'

    # VOTE.
    # Yes.
    VoteYesAttempt5 = 'VYAT5'
    VoteYesMission1 = 'VYMI1'
    VoteYesLeader = 'VYLDR'
    VoteYesAtLeastOneSpy = 'VY1SP'
    VoteYesAtLeastOneSpyOneToWin = 'VY1S1'
    VoteYesDefault = 'VYDEF'
    # No.
    VoteNoNotIncludedTeam3 = 'VNNI3'
    VoteNoFailed1Mission = 'VNF1M'
    VoteNoFailed2Missions = 'VNF2M'
    VoteNoNoSpies = 'VNNOS'
    VoteNoAllSpies = 'VNALS'
    VoteNoDefault = 'VNDEF'

    # SABOTAGE
    # Yes.
    SabotageYesToWin = 'SYTOW'
    SabotageYesLeader = 'SYLDR'
    SabotageYesOnlySpyOnMission = 'SYOWN'
    SabotageYesDefault = 'SYDEF'
    # No.
    SabotageNoAllSpies = 'SNALS'
    SabotageNoMission1 = 'SNMI1'
    SabotageNoDefault = 'SNDEF'

    def __init__(self, data, genes):
        super(SpyGenotype, self).__init__(data, genes, self.Type)


class Phenotype:
    """ Expression of a solution derived through optimization by a GA. Holds a list of expert rules which support or
    reject a particular decision and their associated weights. """

    def __init__(self, actions_for, actions_against):
        self.actions_for = actions_for
        self.actions_against = actions_against

    def run(self):
        """ All expert rules for and against a particular action are run on the current state of the game. The
        associated weights are added to the associated total if the expert rule return true. If the total of the 'for'
        weights is greater than that of the 'against' weights, true is returned. """

        t_for = 0
        t_against = 0

        for a in self.actions_for:
            t_for += a[0]() * a[1]  # True/False (1/0) mult. weight.
        for a in self.actions_against:
            t_against += a[0]() * a[1]

        return t_for > t_against


class Population:
    """ Contains functions for managing generations and handling interactions with the database. """

    State = 'State'
    Size = 'SZE'
    Generation = 'GEN'

    def __init__(self):
        pass

    def create(self, gen):
        # Resistance genes.
        conn = sqlite3.connect(self.genotype_db_name(gen))
        c = conn.cursor()
        c.execute('CREATE TABLE ' + ResGenotype.Type + '(' +
                  # --- DATA
                  '`' + Genotype.Index + '` int,' +
                  '`' + Genotype.Evaluations + '` int,' +
                  '`' + Genotype.Win + '` int,' +
                  '`' + Genotype.Fitness + '` real,'
                  # --- SELECTION
                  # Yes.
                  '`' + ResGenotype.PickYesPerfectRecord + '` real,'
                  '`' + ResGenotype.PickYesUntested + '` real,'
                  '`' + ResGenotype.PickYesFailed1Mission + '` real,'
                  '`' + ResGenotype.PickYesDefault + '` real,'
                  # No.
                  '`' + ResGenotype.PickNoFailed1Mission + '` real,'
                  '`' + ResGenotype.PickNoFailed2Missions + '` real,'
                  '`' + ResGenotype.PickNoDefault + '` real,'
                  # --- VOTE.
                  # Yes.
                  '`' + ResGenotype.VoteYesAttempt5 + '` real,' +
                  '`' + ResGenotype.VoteYesMission1 + '` real,' +
                  '`' + ResGenotype.VoteYesLeader + '` real,' +
                  '`' + ResGenotype.VoteYesDefault + '` real,' +
                  # No.
                  '`' + ResGenotype.VoteNoNotIncludedTeam3 + '` real,' +
                  '`' + ResGenotype.VoteNoFailed1Mission + '` real,' +
                  '`' + ResGenotype.VoteNoFailed2Missions + '` real,' +
                  '`' + ResGenotype.VoteNoDefault + '` real)')

        c.execute('CREATE TABLE ' + SpyGenotype.Type + '(' +
                  # --- DATA
                  '`' + Genotype.Index + '` int,' +
                  '`' + Genotype.Evaluations + '` int,' +
                  '`' + Genotype.Win + '` int,' +
                  '`' + Genotype.Fitness + '` real,'
                  # --- SELECTION
                  # Yes.
                  '`' + SpyGenotype.PickYesPerfectRecord + '` real,'
                  '`' + SpyGenotype.PickYesUntested + '` real,'
                  '`' + SpyGenotype.PickYesDefault + '` real,'
                  # No.
                  '`' + SpyGenotype.PickNoAreSpy + '` real,'
                  '`' + SpyGenotype.PickNoFailed2Missions + '` real,'
                  '`' + SpyGenotype.PickNoDefault + '` real,'
                  # --- VOTE.
                  # Yes.
                  '`' + SpyGenotype.VoteYesAttempt5 + '` real,' +
                  '`' + SpyGenotype.VoteYesMission1 + '` real,' +
                  '`' + SpyGenotype.VoteYesLeader + '` real,' +
                  '`' + SpyGenotype.VoteYesAtLeastOneSpy + '` real,' +
                  '`' + SpyGenotype.VoteYesAtLeastOneSpyOneToWin + '` real,' +
                  '`' + SpyGenotype.VoteYesDefault + '` real,' +
                  # No.
                  '`' + SpyGenotype.VoteNoNotIncludedTeam3 + '` real,' +
                  '`' + SpyGenotype.VoteNoFailed1Mission + '` real,' +
                  '`' + SpyGenotype.VoteNoFailed2Missions + '` real,' +
                  '`' + SpyGenotype.VoteNoNoSpies + '` real,' +
                  '`' + SpyGenotype.VoteNoAllSpies + '` real,' +
                  '`' + SpyGenotype.VoteNoDefault + '` real,' +
                  # --- SABOTAGE.
                  # Yes.
                  '`' + SpyGenotype.SabotageYesToWin + '` real,' +
                  '`' + SpyGenotype.SabotageYesLeader + '` real,' +
                  '`' + SpyGenotype.SabotageYesOnlySpyOnMission + '` real,' +
                  '`' + SpyGenotype.SabotageYesDefault + '` real,' +
                  # No.
                  '`' + SpyGenotype.SabotageNoAllSpies + '` real,' +
                  '`' + SpyGenotype.SabotageNoMission1 + '` real,' +
                  '`' + SpyGenotype.SabotageNoDefault + '` real)')

        conn.commit()
        conn.close()

    def initialise(self, gen, lower, upper):
        size = self.size()
        conn = sqlite3.connect(self.genotype_db_name(gen))
        c = conn.cursor()

        for i in xrange(size):
            # Resistance genes.
            res_genes = tuple([i, 0, 0, 0.0] + [random.uniform(lower, upper) for j in xrange(15)])
            c.execute('INSERT INTO ' + ResGenotype.Type + ' VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)', res_genes)
            # Spy genes.
            spy_genes = tuple([i, 0, 0, 0.0] + [random.uniform(lower, upper) for j in xrange(25)])
            c.execute('INSERT INTO ' + SpyGenotype.Type + ' VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)', spy_genes)
        conn.commit()
        conn.close()

    def insert(self, genotype, gen):
        conn = sqlite3.connect(self.genotype_db_name(gen))
        c = conn.cursor()
        t = tuple(genotype.data.values() + genotype.genes.values())
        params = ','.join('?' for i in range(len(t)))
        c.execute('INSERT INTO ' + genotype.typ + ' VALUES(' + params + ')', t)

        conn.commit()
        conn.close()

    def top(self, num, gen, typ):
        top = []
        conn = sqlite3.connect(self.genotype_db_name(gen))
        c = conn.cursor()
        for row in c.execute('SELECT ' + Genotype.Index + ' FROM ' + typ +
                             ' ORDER BY ' + Genotype.Fitness + ' DESC LIMIT ' + repr(num)):
            top.append(self.genotype(list(row)[0], gen, typ))
        conn.commit()
        conn.close()
        return top

    def tournament(self, num, gen, typ):
        champion = None
        max_fitness = -1.0
        contenders = []
        for i in random.sample(xrange(self.size()), num):
            contenders.append(self.genotype(i, gen, typ))
        for c in contenders:
            contender_fitness = c.data[Genotype.Fitness]
            if contender_fitness > max_fitness:
                champion = c
                max_fitness = contender_fitness
        return champion

    def genotype(self, index, gen, typ, root=''):
        conn = sqlite3.connect(root + self.genotype_db_name(gen))
        c = conn.cursor()

        t = (index,)
        c.execute('SELECT * FROM ' + typ + ' WHERE ' + Genotype.Index + '=?', t)

        values = list(c.fetchone())
        ids = [desc[0] for desc in c.description]

        # Separate data from genes.
        # 4 is num of 'data' values.
        data = OrderedDict(zip(ids[:4], values[:4]))
        genes = OrderedDict(zip(ids[4:], values[4:]))
        genotype = Genotype(data, genes, typ)

        conn.commit()
        conn.close()

        return genotype

    def update_genotype(self, genotype, gen, root=''):
        conn = sqlite3.connect(root + self.genotype_db_name(gen))
        c = conn.cursor()
        t = (genotype.data[Genotype.Evaluations],
             genotype.data[Genotype.Win],
             genotype.data[Genotype.Fitness],
             genotype.data[Genotype.Index])

        c.execute('UPDATE ' + genotype.typ + ' SET ' +
                  Genotype.Evaluations + '=?,' +
                  Genotype.Win + '=?,' +
                  Genotype.Fitness + '=?' +
                  ' WHERE ' + Genotype.Index + '=?', t)

        conn.commit()
        conn.close()

    def create_state(self):
        conn = sqlite3.connect(self.state_db_name())
        c = conn.cursor()
        c.execute('CREATE TABLE ' + self.State + '(' +
                  '`' + self.Generation + '` int,'
                  '`' + self.Size + '` int)')
        t = (0, 0)
        c.execute('INSERT INTO ' + self.State + ' VALUES(?,?)', t)
        conn.commit()
        conn.close()

    def size(self, root=''):
        conn = sqlite3.connect(root + self.state_db_name())
        c = conn.cursor()
        c.execute('SELECT ' + self.Size + ' FROM ' + self.State)
        size = c.fetchone()[0]
        conn.commit()
        conn.close()
        return size

    def set_size(self, size):
        conn = sqlite3.connect(self.state_db_name())
        c = conn.cursor()
        t = (size,)
        c.execute('UPDATE ' + self.State + ' SET ' + self.Size + '=?', t)
        conn.commit()
        conn.close()

    def gen(self, root=''):
        conn = sqlite3.connect(root + self.state_db_name())
        c = conn.cursor()
        c.execute('SELECT ' + self.Generation + ' FROM ' + self.State)
        generation = c.fetchone()[0]
        conn.commit()
        conn.close()
        return generation

    def set_gen(self, gen):
        conn = sqlite3.connect(self.state_db_name())
        c = conn.cursor()
        t = (gen,)
        c.execute('UPDATE ' + self.State + ' SET ' + self.Generation + '=?', t)
        conn.commit()
        conn.close()

    def genotype_db_name(self, gen):
        return 'Population (Gen ' + repr(gen) + ').db'

    def state_db_name(self):
        return 'Population State.db'
