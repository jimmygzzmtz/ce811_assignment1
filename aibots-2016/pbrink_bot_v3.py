from player import Bot
import random

class pbrink3(Bot):
    """An AI bot that tends to vote everything down!"""

    def onGameRevealed(self, players, spies):
        isSpy = False
        self.spies = spies
        self.dataStores = []
        self.roundNum = 0
        self.lastSelectedTeam = []
        self.lastVote = []

        for player in players:
            if (player.index != self.index):
                tempPlayer = dataStore(player)
                for spy in spies:
                    if (tempPlayer.index == spy.index):
                        tempPlayer.isSpy = True
                self.dataStores.append(tempPlayer)
        pass

    def select(self, players, count):
        resultSelected = [self]
        countAlreadyAdded = 1
        if (self.spy):
            # finalReseltSelected = [self] + random.sample(self.others(), count - 1)
            self.dataStores.sort(key=lambda x: x.prob_Max(), reverse=False)
            self.dataStores.sort(key=lambda x: x.isSpy, reverse=False)
            for playerNum in range(0, count-1):
                resultSelected.append(self.dataStores[playerNum].playerObject)
            finalReseltSelected = tuple(resultSelected)
        else:
            knownResist = sorted(self.dataStores, key=lambda x: x.isResist, reverse=True)
            for playerNum in range(0, count-1):
                if (knownResist[playerNum].isResist):
                    countAlreadyAdded += 1
                    resultSelected.append(knownResist[playerNum].playerObject)

            self.dataStores.sort(key=lambda x: x.prob_Max(), reverse=False)
            self.dataStores.sort(key=lambda x: x.isResist, reverse=False)
            # self.dataStores.sort(key=lambda x: x.prob_Avg(), reverse=False)
            # self.dataStores.sort(key=lambda x: x.spyProb, reverse=False)
            for playerNum in range(0, count-countAlreadyAdded):
                resultSelected.append(self.dataStores[playerNum].playerObject)
            finalReseltSelected = tuple(resultSelected)
        return finalReseltSelected

    def vote(self, team):
        boolResult = False
        self.lastSelectedTeam = team

        if (self.game.leader == self):
            return True
        if (self.spy):
            if (self.roundNum >= 1):
                for player in team:
                    if player == self:
                        boolResult = True
                    for myplayerList in self.dataStores:
                        if myplayerList.playerObject == player:
                            if myplayerList.isSpy:
                                boolResult = True
            else:
                boolResult = True
        else:
            boolResult = True
            if (self.roundNum > 0) & (self.game.tries != 5):
                # self.dataStores.sort(key=lambda x: x.calcSort(), reverse=False)
                # self.dataStores.sort(key=lambda x: x.prob_Max(), reverse=False)
                self.dataStores.sort(key=lambda x: x.prob_Max(), reverse=True)
                self.dataStores.sort(key=lambda x: x.isResist, reverse=False)
                # self.dataStores.sort(key=lambda x: x.prob_Avg(), reverse=True)
                # numMostLikelySpy = (len(self.dataStores)) - len(team)
                numMostLikelySpy = 2
                mostLikelySpies = self.dataStores[:numMostLikelySpy]
                for player in team:
                    for isSpyList in self.dataStores:
                        if (player == isSpyList.playerObject):
                            if (isSpyList.isSpy):
                                boolResult = False
                    for myplayerList in mostLikelySpies:
                        if (myplayerList.playerObject == player) & (not myplayerList.isResist):
                            # if myplayerList.spyProb != 0:
                            # if myplayerList.prob_Avg() >= 0.25:
                            if (self.roundNum == 1):
                                if myplayerList.prob_Max() >= 0.5:
                                    boolResult = False
                            elif (myplayerList.prob_Max() >= 0.33): # & (myplayerList.timesSelected > 0):
                                boolResult = False

        return boolResult

    def onVoteComplete(self, votes):
        self.lastVote = votes
        pass

    def sabotage(self):
        # return (self.roundNum > 0)

        boolResult = (self.roundNum > 0)

        if (self.game.wins == 2) | (self.game.losses == 2):
            boolResult = True
        else:
            for selected in self.lastSelectedTeam:
                for player in self.dataStores:
                    if (selected == player.playerObject):
                        if (player.isSpy):
                            boolResult = False

        return boolResult

    def onMissionComplete(self, sabotaged):
        numSelectedOnTeam = len(self.lastSelectedTeam)

        if (not self.spy):
            for selected in self.lastSelectedTeam:
                if (selected == self):
                    numSelectedOnTeam -= 1

            for player in self.dataStores:
                for selected in self.lastSelectedTeam:
                    if (player.playerObject == selected):
                        player.AddSelected(sabotaged, numSelectedOnTeam)
                        if sabotaged == numSelectedOnTeam:
                            player.isSpy = True

            if (sabotaged > 0):
                isResistList = []
                for player, vote in zip(self.game.players, self.lastVote):
                    if (player in self.lastSelectedTeam):
                        for myPlayerList in self.dataStores:
                            if (player == myPlayerList.playerObject):
                                if (not vote):
                                    myPlayerList.isResist = True
                                if (myPlayerList.isResist):
                                    isResistList.append(myPlayerList.playerObject)

                if (numSelectedOnTeam - len(isResistList) == sabotaged):
                    for player in self.lastSelectedTeam:
                        if (player not in isResistList):
                            for myPlayerList in self.dataStores:
                                if (player == myPlayerList.playerObject):
                                    myPlayerList.isSpy = True

        self.roundNum += 1
        pass

class dataStore(object):

    def __init__(self, player):
        self.index = player.index
        self.isSpy = False
        self.isResist = False
        self.spyProb = 0.0
        self.spyProbList = []
        self.timesSelected = 0
        self.playerObject = player
        pass

    def AddSelected(self, numFails, numSelected):
        self.spyProb += numFails / numSelected
        self.timesSelected += 1
        self.spyProbList.append(numFails / numSelected)
        pass

    def calcSort(self):
        spyReductionValue = 0.25
        if (self.timesSelected > 0):
            spyReductionValue = self.spyProb
        return 1 - spyReductionValue

    def prob_Max(self):
        returnVal = 0.33
        if (len(self.spyProbList)):
            tempList = self.spyProbList.sort(key=float)
            returnVal = self.spyProbList[0]

        return returnVal

    def prob_Avg(self):
        returnVal = 0.0
        if (len(self.spyProbList) > 0):
            for val in range(0, len(self.spyProbList)):
                returnVal += val
            returnVal /= len(self.spyProbList)

        return returnVal