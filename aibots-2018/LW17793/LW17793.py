
import random
from player import Bot
from game import State
from pprint import pprint

from Statistics import Statistics
from NeuralNetworkMLP import NeuralNetworkMLP
from NNCreater import NNCreater

# Bot made by "Lars Christian Wiik" (LW17793).
class LW17793(Bot):
    # Variable that indicated if this bot is a spy or not.
    iAmSpy = False
    # List of spies (but empty if this bot is a resistance)
    spies = []
    # List of the resistances (but empty if this bot is resistance)
    resistances = []
    # Neural network to classifty players as spies.
    spyClassifierNN = NNCreater().initialTraining()
    trainingSet = []
    # Home made class for keeping statistics.
    statistics = Statistics()

    # Initilize class variables.
    def onGameRevealed(self, players, spies):
        # Reset statistics.
        self.statistics.newGame(players)
        # Reset training set.
        self.trainingSet = []
        # Remember if this bot is a spy or not.
        self.iAmSpy = len(spies) != 0
        # Remember other spies (only if I am spy).
        self.spies = spies
        # Remember resistances (only if I am spy).
        self.resistances = []
        if self.iAmSpy:
            for p in players:
                if p not in self.spies:
                    self.resistances.append(p)

    # Returns this bots prefered team.
    def select(self, players, count):
        # Allways pick your self on the team.
        myTeam = [self.getMe()]
        spyProbabilities = self.getSpyProbabilityOrder()

        if self.iAmSpy:
            if self.isOnFirstMission():
                # Pick spies on the team in the first mission.
                for p in self.spies:
                    if p not in myTeam:
                        myTeam.append(p)
                    if len(myTeam) >= count:
                        break
                if len(myTeam) >= count:
                    return myTeam

            if count < 3:
                # It is too risky to pick another spy when team size is 2.
                # Rather pick a resistance player with low spy-probability.
                for p in spyProbabilities:
                    if p not in myTeam and p in self.resistances:
                        myTeam.append(p)
                    if len(myTeam) >= count:
                        break

        if len(myTeam) < count:
            # Pick players with low spy-probability.
            for p in spyProbabilities:
                if p not in myTeam:
                    myTeam.append(p)
                if len(myTeam) >= count:
                    break

        return myTeam

    # Store selections.
    def onTeamSelected(self, leader, team):
        self.statistics.addSelects(team)

    # Vote decision.
    def vote(self, team):
        # Always vote yes when I am the team leader.
        if self.game.leader == self:
            return True

        if self.iAmSpy:
            # Spy tactic.

            if self.getSpyCountOnTeam() <= 0:
                # Vote down a team with no spies.
                return False

            # Vote up teams with at least one spy.
            return True
        else:
            # Resistance tactic.

            # Get list of spy probabilities.
            spyProbabilities = self.getSpyProbabilityOrder()

            if self.isLastTry():
                # Always vote yes if it is the last try.
                return True

            if self.isOnFirstMission() and self in team:
                # On the first mission, vote yes if I am in the team.
                return True

            if self not in team:
                # Vote no if I am not in the team.
                return False

            # Find my dream-team.
            myDreamTeam = [self.getMe()]
            lastProb = 0
            for i in range(len(self.game.players) - 1):
                if i < len(team) - 1:
                    myDreamTeam.append(spyProbabilities[i])
                    lastProb = spyProbabilities[i]
                elif spyProbabilities[i] == lastProb:
                    myDreamTeam.append(spyProbabilities[i])
                    lastProb = spyProbabilities[i]

            for p in team:
                if p not in myDreamTeam:
                    # Vote down a team, which is not my dream-team.
                    return False
            # Vote up my dream-team.
            return True

    # Store votes.
    def onVoteComplete(self, votes):
        self.statistics.addVotes(votes)

    # Sabotage decision.
    def sabotage(self):
        if not self.iAmSpy:
            # Return true,msince sabotage function gets called
            # even when this bot is a resistance.
            return False

        if self.isOnFirstMission():
            # Never sabotage the first mission.
            # There are only 2 players on the team.
            return False

        if self.game.losses == 2:
            # Sabotage if it leads to win.
            return True

        if self.game.wins == 2:
            # Sabotage if the spies have to sabotage the rest of the missions.
            return True

        if self.getSpyCountOnTeam() > 1:
            return False

        return True

    # Store information about people on failed mission.
    def onMissionFailed(self, leader, team):
        self.statistics.addFailedMissions(team)

    # Store sabotages.
    def onMissionComplete(self, sabotaged):
        if sabotaged > 0:
            # A sabotage happend.
            self.statistics.addSabotages(self.game.team, self.game.players, sabotaged, self)
        else:
            # No sabotage happend.
            self.statistics.addSuccessMission(self.game.team)

        # Dont collect data the first round, this data is useless.
        if self.game.turn != 1:
            personArray = self.getNNInputs()
            self.trainingSet.append(personArray)

    def onGameComplete(self, win, spies):
        self.addTargetsToTrainingSet(spies)
        n = 0.05
        # Adjust neural network according to the players we are playing with.
        for info in self.trainingSet:
            self.spyClassifierNN.train(info, n)


    # ***** BOOLEAN FUNCTIONS *****


    def isOnFirstMission(self):
        return self.game.turn == 1

    def isLastTry(self):
        return self.game.tries == 5


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

    # Get me and my index.
    def getMe(self):
        for p in self.game.players:
            if self == p:
                return p
        return None

    # Returns the number of spies on the current team.
    def getSpyCountOnTeam(self):
        team = self.game.team
        count = 0
        for p in team:
            if p in self.spies:
                count += 1
        return count

    # Get stats from statistics class.
    def getStatsFromPlayer(self, p):
        return self.statistics.getStatsFromPlayer(
            p,
            self.game.turn,
            self.game.tries
        )

    # Return an ordered ascending list of players according to their spy probabilities.
    def getSpyProbabilityOrder(self):
        probabilities = []
        for p in self.game.players:
            stats = self.getStatsFromPlayer(p)
            spyProb = self.spyClassifierNN.predict(stats)
            #spyProb = self.statistics.spyProb[p.index]
            if not self.iAmSpy and self.statistics.isSpies[p.index] == 1:
                # Set player to be spy.
                probabilities.append(1)
            else:
                probabilities.append(spyProb)
        # Set this bots probability to -1.
        probabilities[self.index] = -1

        playerOrdered = []
        for b in range(len(self.game.players) - 1):
            h = -10
            index = -1
            for i in range(len(probabilities)):
                if probabilities[i] > h:
                    h = probabilities[i]
                    index = i
            playerOrdered.append(self.game.players[index])
            probabilities[index] = -1

        return list(reversed(playerOrdered))


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
