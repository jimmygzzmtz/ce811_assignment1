from player import Bot
import random
import copy

class acwebb_bot(Bot):
    # Required
    def select(self, players, count):
        selectForMission = []

        # Add yourself to the team if leader
        selectForMission.append(self.player)
        # Remove yourself from the list so you don't pick yourself again
        self.playersTemp.remove(self.player)
        # Pick players with the least probability of being a spy if you are not a spy
        if not self.spy:
            # Clone the dictionary
            items = copy.deepcopy(list(self.spyProbability.items())[:])
            lowKeys = []

            # For the remaining number of members
            for y in range(0, count - 1):
                # Find the lowest suspicion level
                min = 10
                index = None
                for x in range(0, len(items)):
                    if items[x][1] < min:
                        min = items[x][1]
                        index = x
                # Add their index to a list and remove the item from the temp dictionary
                lowKeys.append(items[index][0])
                items.remove(items[index])

            # For the lowest suspicion members found
            for x in range(0, len(lowKeys)):
                # Look through all the players and if their index matches, add them to the mission team
                for y in range(0, len(self.playersTemp)):
                    if self.playersTemp[y].index == lowKeys[x]:
                        selectForMission.append(self.playersTemp[y])

        # Otherwise pick random people
        else:
            for x in range(0, count - 1):
                randomNum = random.randrange(0, len(self.playersTemp))
                selectForMission.append(self.playersTemp[randomNum])
                self.playersTemp.remove(self.playersTemp[randomNum])

        return selectForMission

    def vote(self, team):
        if not self.spy:
            for x in range(0, len(self.selectedTeam)):
                if self.selectedTeam[x].index != self.player.index:
                    if self.spyProbability[self.selectedTeam[x].index] > 0.5:
                        # Vote against if there is a high chance of a spy being in the team
                        return False
                    else:
                        return True
        if self.spy:
            self.spiesTemp.remove(self)
            if self in team:
                # Vote for if you are in the team
                return True
            else:
                if self.game.turn > 1:
                    for x in range(0, len(self.spiesTemp)):
                        # Vote yes if there are spies in the team
                        if self.spiesTemp[x] in self.selectedTeam:
                            return True
                return False

    def sabotage(self):
        # If the Resistance or Spies are 1 win from winning, sabotage.
        if self.game.wins == 2 | self.game.losses == 2:
            return True

        # Do not sabotage if you are not the only spy
        if self.spiesInTeam(self.selectedTeam):
            return False
        else:
            return True

        pass

    # Helper Functions
    def onGameRevealed(self, players, spies):
        self.spies = copy.deepcopy(list(spies)[:])  # Spies in game
        self.spy = self in spies  # Am I a spy?
        self.players = copy.deepcopy(players)  # Players in game
        self.playersTemp = copy.deepcopy(players) #  Copy of the Players to edit later
        self.spiesTemp = copy.deepcopy(list(spies)[:]) # Copy of the Spies to edit later
        self.selectedTeam = []  # Currently selected team
        self.spyProbability = {}  # Dictionary containing values dictating the probability of a player being a spy
        self.player = None
        # Locate the player object
        for x in range(0, len(players)):
            if (self.index == players[x].index):
                self.player = players[x]
        # Assign a dictionary of values for suspicion levels
        for x in range(0, len(players)):
            if self.players[x] != self:
                self.spyProbability[self.players[x].index] = 0
        pass

    def onMissionAttempt(self, mission, tries, leader):
        # Make a copy of the players and spies to edit for other uses
        self.playersTemp = copy.deepcopy(self.players)
        self.spiesTemp = copy.deepcopy(self.spies[:])
        pass

    def onTeamSelected(self, leader, team):
        # Make a copy of the players and spies to edit for other uses
        self.selectedTeam = copy.deepcopy(team[:])
        pass

    def onMissionComplete(self, sabotaged):

        if sabotaged > 0:
            # If the player isn't a spy and the team size is 2, the other person must be a spy.
            if self.player in self.players and not self.spy:
                if (len(self.selectedTeam)-1 if self.game.leader == self.player else len(self.selectedTeam)) == sabotaged:
                    for x in range(0, sabotaged):
                        if self.selectedTeam[x] != self.player:
                            self.spyProbability[self.players[x].index] = 1
            # Else, add spy suspicion values depending on the remaining size of the team
            if not self.spy:
                for x in range(0, len(self.players)):
                    if (self.players[x] in self.selectedTeam and self.players[x] != self.player):
                        if (self.player in self.selectedTeam):
                            self.spyProbability[self.players[x].index] += (sabotaged / len(self.selectedTeam) - 1)
                        else:
                            self.spyProbability[self.players[x].index] += (sabotaged / len(self.selectedTeam))
        if self.player.index in self.spyProbability:
            del(self.spyProbability[self.player.index])
        pass

    def spiesInTeam(self, team):
        for x in range(0, len(self.spies)):
            if self != self.spies[x]:
                if self.spies[x] in team:
                    return True
        return False
