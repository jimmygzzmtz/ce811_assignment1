
import random
from player import Bot
from game import State

from Statistics import Statistics
from FileReadWriter import FileReadWriter
from Files import Files

# This class is used for collecting data from the resistance game.
class DataCollector(Bot):

    statistics = Statistics()
    trainingSet = []

    # Reset statistics.
    def onGameRevealed(self, players, spies):
        self.statistics.newGame(players)
        # Remember if this bot is a spy or not.
        self.iAmSpy = len(spies) != 0
        self.trainingSet = []

    # Returns this bots prefered team.
    def select(self, players, count):
        return [self] + random.sample(self.others(), count - 1)

    # Store selections.
    def onTeamSelected(self, leader, team):
        self.statistics.addSelects(team)

    # Vote decision.
    def vote(self, team):
        return True

    # Store votes.
    def onVoteComplete(self, votes):
        self.statistics.addVotes(votes)

    # Sabotage decision.
    def sabotage(self):
        return True

    # Store sabotages.
    def onMissionComplete(self, sabotaged):
        if sabotaged > 0:
            # A sabotage happend
            self.statistics.addSabotages(self.game.team, self.game.players, sabotaged, self)
        else:
            # No sabotage happend
            self.statistics.addSuccessMission(self.game.team)

        # Dont collect data the first round, this data is useless.
        if self.game.turn != 1:
            personArray = self.getNNInputs()
            self.trainingSet.append(personArray)

    def onMissionFailed(self, leader, team):
        self.statistics.addFailedMissions(team)

    # Write taining input and output to file.
    def onGameComplete(self, win, spies):
        self.addTargetsToTrainingSet(spies)
        FileReadWriter().writeToFile(self.trainingSet, Files().newTrainingSet_txt)


    # ***** GET FUNCTIONS *****


    # Get inputs for neural network.
    def getNNInputs(self):
        personArray = []
        for p in self.game.players:
            if p == self:
                continue
            inputs = self.statistics.getStatsFromPlayer(
                p,
                self.game.turn,
                self.game.tries
            )
            personArray.append([inputs])
        return personArray


    # ***** ADD FUNCTIONS *****


    # Add targets to training set for neural network.
    def addTargetsToTrainingSet(self, spies):
        for i in range(len(self.trainingSet)):
            players = self.game.players
            delta = 0
            for j in range(len(players)):
                if players[j] == self:
                    delta = 1
                    continue
                if players[j] in spies:
                    self.trainingSet[i][j - delta].append([1])
                else:
                    self.trainingSet[i][j - delta].append([0])
