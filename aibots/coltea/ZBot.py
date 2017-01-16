from player import Bot
import random

class ZGameData(object):
    def __init__(self, myBotPlayerObj):
        self.isDebugEnabled = False
        self.myBot = myBotPlayerObj
        self.playersData = []
        self.successfulTeamOf3 = []
        self.lastSuccessfulTeam = []
        self.lastSabotagedTeam = []

    def getPlayerData(self, playerObj):
        for playerData in self.playersData:
            if playerData.playerObj == playerObj:
                return playerData

    def getResistanceMembers(self):
        resistanceMembers = []
        for player in self.playersData:
            if not player.isSpy:
                resistanceMembers.append(player.playerObj)

        return resistanceMembers

    def getSpies(self):
        spies = []
        for player in self.playersData:
            if player.isSpy:
                spies.append(player.playerObj)

        return spies

    def getMostProbableSpies(self):
        probableSpy = self.playersData[0].playerObj
        minProbability = self.playersData[0].probability
        lastProbableSpy = self.playersData[0].playerObj
        lastProbability =  self.playersData[0].probability
        for index in range(1, len(self.playersData)):
            tempData = self.playersData[index]

            if tempData.playerObj == self.myBot:
                continue

            if tempData.probability <= minProbability:
                lastProbableSpy = probableSpy
                probableSpy = tempData.playerObj
                lastProbability = minProbability
                minProbability = tempData.probability
            elif tempData.probability <= lastProbability or index == 1:
                lastProbableSpy = tempData.playerObj
                lastProbability = tempData.probability

        spies = self.getSpies()
        if len(spies) == 1:
            if spies[0] != probableSpy:
                return [spies[0], probableSpy]
            else:
                return [spies[0], lastProbableSpy]
        elif len(spies) == 2:
            return [spies[0], spies[1]]

        return [probableSpy, lastProbableSpy]

class ZPlayerData(object):
    def __init__(self, player):
        self.playerObj = player
        self.name = player.name
        self.index = player.index
        self.isSpy = False
        #self.isResist = False
        self.probability = 0.0      # -1.0 -> 1     (-1 means spy : 1 means resistance)
        self.totalMissions = 0
        self.onSuccessfulMissions = 0
        self.onSabotagedMissions = 0

    def __repr__(self):
        #output = str(self.index) + "-" + self.name + " " + str(self.isSpy) + " " + str(self.probability) + " " + str(self.resistProb)
        output = self.name + " " + str(self.onSuccessfulMissions) + " " + str(self.onSabotagedMissions) + " " + \
                 str(self.totalMissions) + " " + str(self.probability) + " " + str(self.isSpy)

        return output

class ZBot(Bot):
    # Called at the start of the game
    def onGameRevealed(self, players, spies):
        self.gameData = ZGameData(players[self.index])

        for player in players:
            playerData = ZPlayerData(player)
            if player in spies:
                playerData.isSpy = True
            self.gameData.playersData.append(playerData)

    def select(self, players, count):
        selectedMissionPlayers = [players[self.index]]

        if self.spy:
            resistanceMembers = self.gameData.getResistanceMembers()

            if count == 2:
                # Select me and one random resistance member
                selectedMissionPlayers.append(random.sample(resistanceMembers, 1)[0])
            elif count == 3:
                # Select me, most successful resistance member and someone from the last successful team
                maxSuccessful = -1
                maxSuccessfulMember = None
                for player in resistanceMembers:
                    tempData = self.gameData.getPlayerData(player)
                    if tempData.onSuccessfulMissions > maxSuccessful:
                        maxSuccessfulMember = player
                        maxSuccessful = tempData.onSuccessfulMissions
                selectedMissionPlayers.append(maxSuccessfulMember)

                for p in self.gameData.lastSuccessfulTeam:
                    if len(selectedMissionPlayers) < count and not p in selectedMissionPlayers:
                        selectedMissionPlayers.append(p)

            # Fill team if necessary with random resistance members
            i = 0
            while len(selectedMissionPlayers) < count:
                selectedPlayer = resistanceMembers[i]
                if not selectedPlayer in selectedMissionPlayers:
                    selectedMissionPlayers.append(selectedPlayer)
                i += 1
        else:
            if count == 3 and len(self.gameData.successfulTeamOf3) != 0:
                return self.gameData.successfulTeamOf3

            probableSpies = self.gameData.getMostProbableSpies()
            for player in players:
                if len(selectedMissionPlayers) < count:
                    if not player in probableSpies and not player in selectedMissionPlayers:
                        selectedMissionPlayers.append(player)

            if self.gameData.isDebugEnabled:
                print("\n@@@@@@@@@@@@@@@@@@@@")
                print("Probable Spies:")
                print(self.gameData.getMostProbableSpies())
                print()
                print("Selected team:")
                print(selectedMissionPlayers)
                print()
                print(self.gameData.playersData[0])
                print(self.gameData.playersData[1])
                print(self.gameData.playersData[2])
                print(self.gameData.playersData[3])
                print(self.gameData.playersData[4])
                print("@@@@@@@@@@@@@@@@@@@@\n")

        return selectedMissionPlayers

    def vote(self, team):
        #print(team)
        # Vote yes when it comes to the last attempt
        if self.game.tries == 5:
            return True

        # Accept any team that is selected by me
        if self.game.leader == self:
            return True

        if self.spy:
            #resistanceMembers = self.gameData.getResistanceMembers()
            spies = self.gameData.getSpies()

            # Check if there is a spy in the team
            isSpySelected = False
            for player in team:
                if player in spies:
                    isSpySelected = True
                    break

            if isSpySelected:
                return True

            return False
        else:
            probableSpies = self.gameData.getMostProbableSpies()
            if self.game.turn > 1:
                for player in team:
                    if player in probableSpies:
                        return False

            return True

    def onVoteComplete(self, votes):
        if self.game.tries == 5:
            for i in range(0, len(votes)):
                tempData = self.gameData.getPlayerData(self.game.players[i])
                if not votes[i]:
                    tempData.probability -= 1
        elif self.game.team == self.gameData.lastSuccessfulTeam:
            for i in range(0, len(votes)):
                tempData = self.gameData.getPlayerData(self.game.players[i])
                if not votes[i]:
                    tempData.probability -= 0.4
        elif self.game.turn > 1:
            spy = self.gameData.getMostProbableSpies()[0]

            hasSpy = False
            if spy in self.game.team:
                hasSpy = True

            for i in range(0, len(votes)):
                tempData = self.gameData.getPlayerData(self.game.players[i])

                if hasSpy:
                    if votes[i]:
                        tempData.probability -= 0.125
                    else:
                        tempData.probability += 0.1
                else:
                    if votes[i]:
                        tempData.probability += 0.1
                    else:
                        tempData.probability -= 0.125

    def sabotage(self):
        if self.game.wins == 2 or self.game.losses == 2:
            return True

        if len(self.game.team) == 2 and self.game.turn == 1:
            return False

        return True

    def onMissionComplete(self, sabotaged):
        if self.gameData.isDebugEnabled:
            print("\n----------")
            print("Mission: " + str(self.game.turn) + " ; " + "Attempts: " + str(self.game.tries))
            print("Leader: " + str(self.game.leader))
            for player in self.game.team:
                print(self.gameData.getPlayerData(player))

        if sabotaged == 0:
            self.gameData.lastSuccessfulTeam = self.game.team
            if len(self.game.team) == 3:
                self.gameData.successfulTeamOf3 = self.game.team
        else:
            self.gameData.lastSabotagedTeam = self.game.team

        # Update player data
        for player in self.game.team:
            tempData = self.gameData.getPlayerData(player)
            tempData.totalMissions += 1

            if sabotaged == 0:
                tempData.onSuccessfulMissions += 1
                if self.game.turn == 1:
                    # Most spies usually fake the first round => don't give them too much credibility
                    tempData.probability += 1 / len(self.game.team) / 2
                else:
                    tempData.probability += 1 / len(self.game.team)
            elif sabotaged >= 1:
                if len(self.game.team) == 2:
                    tempData.wasOn2SabotagedMission = True

                tempData.onSabotagedMissions += 1
                tempData.probability -= 1 / len(self.game.team)

        # Only Resistance Data
        if self.game.players[self.index] in self.game.team and len(self.game.team) == 2 and sabotaged >= 1:
            for p in self.game.team:
                if p.index != self.index:
                    self.gameData.getPlayerData(p).isSpy = True

        if self.gameData.isDebugEnabled:
            print()
            for player in self.game.team:
                print(self.gameData.getPlayerData(player))
            print("----------")

    def onGameComplete(self, win, spies):
        if self.gameData.isDebugEnabled:
            print("\n\n####################")
            print("Game finished:")
            print(self.gameData.playersData[0])
            print(self.gameData.playersData[1])
            print(self.gameData.playersData[2])
            print(self.gameData.playersData[3])
            print(self.gameData.playersData[4])
            print("####################")