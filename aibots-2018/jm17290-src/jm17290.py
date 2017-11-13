from __future__ import division
import random
from player import Bot
from genetic_algorithm import Phenotype


class JM17290Bot(Bot):
    """ This (jm17290.JM17290Bot) bot SHOULD be used for the purpose of competition, not jm17290_ea.JM17290Bot which
    is used during the optimization process. The weights of each expert rule have been hard coded in this bot from the
    results of the optimization process. """

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
        """ Create phenotypes for each of the functions performed by the bot - Selection, voting and sabotage (spy
        only). This values are the result of offline optimization and have been hard-coded into this bot. Phenotypes
        are run to return a boolean decision based on the weights of the expert rules."""

        self.perfect_record = set(self.others())
        self.unselected = set(self.others())
        self.failed_one_mission = set()
        self.failed_two_missions = set()

        if not self.spy:
            # RESISTANCE.

            # SELECT - Phenotype
            self.res_select = Phenotype(
                # Yes.
                # Select player with perfect record.
                # Select previously unselected player.
                # Forgive one mission fail.
                # Default up vote to avoid deadlock.
                [(lambda: self.to_select in self.perfect_record,
                  0.41031111191729),
                 (lambda: self.to_select in self.unselected,
                  0.810704837654553),
                 (lambda: self.to_select in self.failed_one_mission,
                  0.474840040694015),
                 (lambda: True,
                  0.504913723311206)],
                # No.
                # Player failed one mission.
                # Player failed two missions.
                # Default up vote to avoid deadlock.
                [(lambda: self.to_select in self.failed_one_mission,
                  0.597685887348422),
                 (lambda: self.to_select in self.failed_two_missions,
                  0.700203627857123),
                 (lambda: True,
                  0.19680430271345)])

            # VOTE - Phenotype.
            self.res_vote = Phenotype(
                # Yes.
                # Vote last attempt to save the mission.
                # Vote for the first mission.
                # Approve own mission.
                # Default vote up to avoid deadlock.
                [(lambda: self.game.tries == 5,
                  0.501056713172492),
                 (lambda: self.game.turn == 1,
                  0.427299008118781),
                 (lambda: self.game.leader == self,
                  0.600031738188556),
                 (lambda: True,
                  1.13744031828526)],
                # No.
                # Reject if left out of team of three.
                # Reject if team member failed one mission.
                # Reject if team member failed two missions.
                # Default vote up to avoid deadlock.
                [(lambda: len(self.game.team) == 3 and not bool({self}.intersection(set(self.game.team))),
                  0.640319560559956),
                 (lambda: bool(set(self.game.team).intersection(self.failed_one_mission)),
                  0.431370171233806),
                 (lambda: bool(set(self.game.team).intersection(self.failed_two_missions)),
                  0.403174965131434),
                 (lambda: True,
                  0.290316333016446)])
        else:
            # SPY
            self.spies = spies

            # SELECT - Phenotype
            self.spy_selection = Phenotype(
                # Yes.
                # Select player with a perfect record.
                # Select previously unselected player.
                # Default vote up to avoid deadlock.
                [(lambda: self.to_select in self.perfect_record,
                  0.489024372889951),
                 (lambda: self.to_select in self.unselected,
                  0.510615719894065),
                 (lambda: True,
                  0.771726947747221)],
                # No.
                # Picked self, don't pick another spy.
                # Don't pick VERY suspicious player.
                # Default vote up to avoid deadlock.
                [(lambda: self.to_select in self.spies,
                  0.222090167727367),
                 (lambda: self.to_select in self.failed_two_missions,
                  0.495011888873639),
                 (lambda: True,
                  0.417658784557995)])

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
                  0.334915321750891),
                 (lambda: self.game.turn == 1,
                  0.517161991732565),
                 (lambda: self.game.leader == self,
                  0.300158590014646),
                 (lambda: bool(set(self.game.team).intersection(set(self.spies))),
                  0.584157504635239),
                 (lambda: bool(set(self.game.team).intersection(set(self.spies))) and self.game.losses == 2,
                  0.152770707589673),
                 (lambda: True,
                  0.248524564627197)],
                # No.
                # Not included in team of three.
                # Vote against team with suspicious member to avoid detection.
                # Vote against team with VERY suspicious member to avoid detection.
                # Vote against a team with no spies.
                # Vote against a team of all spies.
                # Default vote against to avoid deadlock.
                [(lambda: len(self.game.team) == 3 and not bool({self}.intersection(set(self.game.team))),
                  0.544632134112408),
                 (lambda: bool(set(self.game.team).intersection(self.failed_one_mission)),
                  0.532148087453266),
                 (lambda: bool(set(self.game.team).intersection(self.failed_two_missions)),
                  0.677482389993213),
                 (lambda: not bool(set(self.game.team).intersection(set(self.spies))),
                  0.48931296791924),
                 (lambda: set(self.game.team) == set(self.spies),
                  0.749656915089866),
                 (lambda: True,
                  1.09220018078465)])

            # SABOTAGE - Phenotype.
            self.spy_sabotage = Phenotype(
                # Yes.
                # Sabotage to win the game.
                # Sabotage own mission.
                # Sabotage if only spy on the mission.
                # Default vote up to avoid deadlock.
                [(lambda: self.game.losses == 2,
                  0.522465249683372),
                 (lambda: self.game.leader == self,
                  0.484299026192786),
                 (lambda: {self} == ({self}.intersection(set(self.game.team))),
                  0.276346752429635),
                 (lambda: True,
                  0.704610263859575)],
                # No.
                # Do not sabotage a game with all spies.
                # Do not sabotage the first mission.
                # Default vote up to avoid deadlock.
                [(lambda: set(self.game.team) == set(self.spies),
                  0.147403499928082),
                 (lambda: self.game.turn == 1,
                  0.290752533323706),
                 (lambda: True,
                  0.43702446482557)])

    def onTeamSelected(self, leader, team):
        """ Note players who have been on a mission. """

        for p in team:
            self.unselected.discard(p)  # Note players who've been on mission.

    def onMissionComplete(self, sabotaged):
        """ Note players who have lost a perfect record, failed 1 mission, or failed two missions. """

        if sabotaged:
            for p in self.game.team:
                self.perfect_record.discard(p)
                if p in self.failed_one_mission:  # Note players who've failed one mission.
                    self.failed_two_missions.add(p)  # Note players who've failed two missions.
                self.failed_one_mission.add(p)

