from __future__ import division
import random
from player import Bot
from genetic_algorithm import Population, ResGenotype, SpyGenotype, Phenotype


class JM17290Bot(Bot):
    """ This not (jm17290_ea.JM17290Bot) is used during optimization and hence contains code to facilitate this. This
    bot should NOT be run during a competition. use jm17290.JM17290(Bot) instead, which has hard-coded weights for
    expert rules set through optimization. """

    def select(self, players, count):
        """ Select players on an individual basis using weighted expert rule phenotypes 'res_selection' and
        'spy_selection' for Resistance members and spies respectively. If weighted-expert selection rules cannot choose
        enough suitable players to go on the mission then the remaining slots are populated randomly."""

        maybe = []
        selection = [self]  # Resistance and Spy selecting self by default.

        for p in self.others():
            self.to_select = p
            if len(selection) < count:
                if not self.spy:
                    if self.res_select.run():
                        selection.append(p)
                    else:
                        maybe.append(p)
                else:
                    if self.spy_selection.run():
                        selection.append(p)
                    else:
                        maybe.append(p)

        while len(selection) < count:
            p = random.choice(maybe)
            selection.append(p)
            maybe.remove(p)

        return selection

    def sabotage(self):
        """ Resistance members cannot sabotage a mission. Spy sabotage is determined by 'spy_sabotage' weighted expert
        rules phenotype."""

        if not self.spy:
            return False
        else:
            return self.spy_sabotage.run()

    def vote(self, team):
        """ Vote for Resistance and Spies is determined by 'res_vote' and 'spy_vote' weighted expert rule phenotypes
         respectively. """

        if not self.spy:
            return self.res_vote.run()
        else:
            return self.spy_vote.run()

    def onGameRevealed(self, players, spies):
        """ Create phenotypes that will be used for this games by acquiring them randomly from persistent storage.
        Resistance play is made up of two phenotypes: Select and Vote. Spy play is made up of three phenotypes:
        Select, Vote and Sabotage. Phenotypes are executed and return a boolean decision based on the weights of the
        active expert rules at the current point in the game. """

        self.root = 'jm17290-src/'
        self.population = Population()
        self.gen = self.population.gen(self.root)
        self.population_size = self.population.size(self.root)

        self.perfect_record = set(self.others())
        self.unselected = set(self.others())
        self.failed_one_mission = set()
        self.failed_two_missions = set()

        if not self.spy:
            # RESISTANCE.

            self.res_genotype = self.population.genotype(random.randint(0, self.population_size - 1),
                                                         self.gen,
                                                         ResGenotype.Type,
                                                         self.root)
            # SELECT - Phenotype
            self.res_select = Phenotype(
                # Yes.
                # Select player with perfect record.
                # Select previously unselected player.
                # Forgive one mission fail.
                # Default up vote to avoid deadlock.
                [(lambda: self.to_select in self.perfect_record,
                  self.res_genotype[ResGenotype.PickYesPerfectRecord]),
                 (lambda: self.to_select in self.unselected,
                  self.res_genotype[ResGenotype.PickYesUntested]),
                 (lambda: self.to_select in self.failed_one_mission,
                  self.res_genotype[ResGenotype.PickYesFailed1Mission]),
                 (lambda: True,
                  self.res_genotype[ResGenotype.PickYesDefault])],
                # No.
                # Player failed one mission.
                # Player failed two missions.
                # Default up vote to avoid deadlock.
                [(lambda: self.to_select in self.failed_one_mission,
                  self.res_genotype[ResGenotype.PickNoFailed1Mission]),
                 (lambda: self.to_select in self.failed_two_missions,
                  self.res_genotype[ResGenotype.PickNoFailed2Missions]),
                 (lambda: True,
                  self.res_genotype[ResGenotype.PickNoDefault])])

            # VOTE - Phenotype.
            self.res_vote = Phenotype(
                # Yes.
                # Vote last attempt to save the mission.
                # Vote for the first mission.
                # Approve own mission.
                # Default vote up to avoid deadlock.
                [(lambda: self.game.tries == 5,
                  self.res_genotype[ResGenotype.VoteYesAttempt5]),
                 (lambda: self.game.turn == 1,
                  self.res_genotype[ResGenotype.VoteYesMission1]),
                 (lambda: self.game.leader == self,
                  self.res_genotype[ResGenotype.VoteYesLeader]),
                 (lambda: True,
                  self.res_genotype[ResGenotype.VoteYesDefault])],
                # No.
                # Reject if left out of team of three.
                # Reject if team member failed one mission.
                # Reject if team member failed two missions.
                # Default vote up to avoid deadlock.
                [(lambda: len(self.game.team) == 3 and not bool({self}.intersection(set(self.game.team))),
                  self.res_genotype[ResGenotype.VoteNoNotIncludedTeam3]),
                 (lambda: bool(set(self.game.team).intersection(self.failed_one_mission)),
                  self.res_genotype[ResGenotype.VoteNoFailed1Mission]),
                 (lambda: bool(set(self.game.team).intersection(self.failed_two_missions)),
                  self.res_genotype[ResGenotype.VoteNoFailed2Missions]),
                 (lambda: True,
                  self.res_genotype[ResGenotype.VoteNoDefault])])
        else:
            # SPY
            self.spies = spies
            self.spy_genotype = self.population.genotype(random.randint(0, self.population_size - 1),
                                                         self.gen,
                                                         SpyGenotype.Type,
                                                         self.root)

            # SELECT - Phenotype
            self.spy_selection = Phenotype(
                # Yes.
                # Select player with a perfect record.
                # Select previously unselected player.
                # Default vote up to avoid deadlock.
                # Picked self, don't pick another spy.
                # Don't pick VERY suspicious player.
                [(lambda: self.to_select in self.perfect_record,
                  self.spy_genotype[SpyGenotype.PickYesPerfectRecord]),
                 (lambda: self.to_select in self.unselected,
                  self.spy_genotype[SpyGenotype.PickYesUntested]),
                 (lambda: True,
                  self.spy_genotype[SpyGenotype.PickYesDefault])],
                # No.
                # Picked self, don't pick another spy.
                # Don't pick VERY suspicious player.
                # Default vote up to avoid deadlock.
                [(lambda: self.to_select in self.spies,
                 self.spy_genotype[SpyGenotype.PickNoAreSpy]),
                 (lambda: self.to_select in self.failed_two_missions,
                 self.spy_genotype[SpyGenotype.PickNoFailed2Missions]),
                 (lambda: True,
                 self.spy_genotype[SpyGenotype.PickNoDefault])])

            # VOTE - Phenotype.
            self.spy_vote = Phenotype(
                # Yes.
                # Vote for final try to avoid detection.
                # Vote for first mission, pretend nothing known.
                # Vote for own mission.
                # Support spy on mission.
                # Support the win.
                # Vote up to avoid deadlock.
                [(lambda: self.game.tries == 5,
                  self.spy_genotype[SpyGenotype.VoteYesAttempt5]),
                 (lambda: self.game.turn == 1,
                  self.spy_genotype[SpyGenotype.VoteYesMission1]),
                 (lambda: self.game.leader == self,
                  self.spy_genotype[SpyGenotype.VoteYesLeader]),
                 (lambda: bool(set(self.game.team).intersection(set(self.spies))),
                  self.spy_genotype[SpyGenotype.VoteYesAtLeastOneSpy]),
                 (lambda: bool(set(self.game.team).intersection(set(self.spies))) and self.game.losses == 2,
                  self.spy_genotype[SpyGenotype.VoteYesAtLeastOneSpyOneToWin]),
                 (lambda: True,
                  self.spy_genotype[SpyGenotype.VoteYesDefault])],
                # No.
                # Not included in team of three.
                # Vote against team with suspicious member to avoid detection.
                # Vote against team with VERY suspicious member to avoid detection.
                # Vote against a team with no spies.
                # Vote against a team of all spies.
                # Default vote against to avoid deadlock.
                [(lambda: len(self.game.team) == 3 and not bool({self}.intersection(set(self.game.team))),
                  self.spy_genotype[SpyGenotype.VoteNoNotIncludedTeam3]),
                 (lambda: bool(set(self.game.team).intersection(self.failed_one_mission)),
                  self.spy_genotype[SpyGenotype.VoteNoFailed1Mission]),
                 (lambda: bool(set(self.game.team).intersection(self.failed_two_missions)),
                  self.spy_genotype[SpyGenotype.VoteNoFailed2Missions]),
                 (lambda: not bool(set(self.game.team).intersection(set(self.spies))),
                  self.spy_genotype[SpyGenotype.VoteNoNoSpies]),
                 (lambda: set(self.game.team) == set(self.spies),
                  self.spy_genotype[SpyGenotype.VoteNoAllSpies]),
                 (lambda: True,
                  self.spy_genotype[SpyGenotype.VoteNoDefault])])

            # SABOTAGE - Phenotype.
            self.spy_sabotage = Phenotype(
                # Yes.
                # Sabotage to win the game.
                # Sabotage own mission.
                # Sabotage if only spy on the mission.
                # Default vote up to avoid deadlock.
                [(lambda: self.game.losses == 2,
                  self.spy_genotype[SpyGenotype.SabotageYesToWin]),
                 (lambda: self.game.leader == self,
                  self.spy_genotype[SpyGenotype.SabotageYesLeader]),
                 (lambda: {self} == ({self}.intersection(set(self.game.team))),
                  self.spy_genotype[SpyGenotype.SabotageYesOnlySpyOnMission]),
                 (lambda: True,
                  self.spy_genotype[SpyGenotype.SabotageYesDefault])],
                # No.
                # Do not sabotage a game with all spies.
                # Do not sabotage the first mission.
                # Default vote up to avoid deadlock.
                [(lambda: set(self.game.team) == set(self.spies),
                  self.spy_genotype[SpyGenotype.SabotageNoAllSpies]),
                 (lambda: self.game.turn == 1,
                  self.spy_genotype[SpyGenotype.SabotageNoMission1]),
                 (lambda: True,
                  self.spy_genotype[SpyGenotype.SabotageNoDefault])])

    def onTeamSelected(self, leader, team):
        """ Note players who have been on a mission. """

        for p in team:
            self.unselected.discard(p)

    def onMissionComplete(self, sabotaged):
        """ Note players who have lost a perfect record, failed 1 mission, or failed two missions. """

        if sabotaged:
            for p in self.game.team:
                self.perfect_record.discard(p)
                if p in self.failed_one_mission:  # Note players who've failed one mission.
                    self.failed_two_missions.add(p)  # Note players who've failed two missions.
                self.failed_one_mission.add(p)

    def onGameComplete(self, win, spies):
        """ Update the genotype with the outcome of the game and persist the result. """

        if not self.spy:
            self.res_genotype.update(win)
            self.population.update_genotype(self.res_genotype, self.gen, self.root)
        else:
            self.spy_genotype.update(win)
            self.population.update_genotype(self.spy_genotype, self.gen, self.root)
