import random
import itertools
import operator
import random

from player import Bot

class ds17348(Bot):
    intel = {}
    roundIntel = {}

    def onGameRevealed(self, players, spies):
        self.players = players
        self.spies = spies
        self.team = {}
        self.roundIntel = {}
        self.roundTrusties = {}

        num = len(self.players)
        cout = 0
        while cout < num:
            # Next 5 lines gets rid of those pesky numbers
            name = str(self.players[cout])
            rubbishNum, newName = name.split("-")
            checkForDot = newName.find(".")
            if (checkForDot != -1):
                uselessDot, newName = newName.split(".")

            # Check if player already has a profile, if not, create one
            if newName not in self.intel:
                self.intel[newName] = [0, 0]

            self.roundIntel[newName] = [0, 0]
            cout += 1

    def onTeamSelected(self, leader, team):
        self.team = team

    def select(self, players, count):
        # an error about Selecting will appear SOMETIMES, simply just run the program again
        self.count = count

        if self.spy:  # Picking those whom role not equal to spy
            others = ([p for p in players if p not in self.spies])
            return [self] + random.sample(self.others(), count - 1)
        else:
            decisionTime = {}
            cout = 0
            num = len(self.players)

            while cout < num:
                name = str(self.players[cout])
                rubbishNum, newName = name.split("-")
                checkForDot = newName.find(".")

                if (checkForDot != -1):
                    uselessDot, newName = newName.split(".")

                if newName.find("ds17348") != -1:  # Skips myself
                    pass
                else:
                    negPoints = self.intel[newName][0]
                    posPoints = self.intel[newName][1]

                    if (negPoints != 0 or posPoints != 0):  # The bot hasn't played enough games yet if false
                        totalGames = negPoints + posPoints
                        totalAffinity = posPoints - negPoints
                        decision = totalAffinity / totalGames
                        decisionTime[newName] = decision

                cout += 1

            sortedList = sorted(decisionTime.items(), key=operator.itemgetter(1))

            if not sortedList:
                return [self] + random.sample(self.others(), count - 1)

            length = len(sortedList)
            trusted1 = sortedList[(length - 2)][0]
            if self.count == 3:
                trusted2 = sortedList[(length - 1)][0]

            for p in self.players:
                name = str(p)
                rubbishNum, newName = name.split("-")
                checkForDot = newName.find(".")

                if (checkForDot != -1):
                    uselessDot, newName = newName.split(".")

                if newName == trusted1:
                    trusted1 = p
                    self.roundTrusties[0] = trusted1
                elif self.count == 3 and newName == trusted2:
                    trusted2 = p
                    self.roundTrusties[1] = trusted2

            if self.count == 3:
                return [self] + [trusted1] + [trusted2]
            else:
                return [self] + [trusted1]

    def vote(self, team):
        # Spy
        team = self.team
        spies = self.spies
        tries = self.game.tries
        wins = self.game.wins

        if self.spy:
            if tries < 3:
                for t in team:
                    if self == t:
                        return True

                for t in team:
                    for s in spies:
                        if s is t:
                            return True

                return False
            else:
                return False
        else:  # Resistance
            teamlength = len(team)
            if not self.roundTrusties:
                return True
            else:
                trust1 = self.roundTrusties.get(0)
                trust2 = self.roundTrusties.get(1)

            if trust1 is None or trust2 is None:
                return True

            if teamlength == 2:
                if trust1 not in team or trust2 not in team:
                    return False
                else:
                    return True
            elif teamlength == 3:
                if trust1 not in team and trust2 not in team:
                    return False
                else:
                    return True

    def onVoteComplete(self, votes):
        count = 0
        num = len(self.players)
        while count < num:

            result = votes[count]
            name = str(self.players[count])
            uselessNum, newName = name.split("-")
            checkForDot = newName.find(".")
            if (checkForDot != -1):
                uselessDot, newName = newName.split(".")

            key = newName

            currentNegative = self.roundIntel[key][0]
            currentPositive = self.roundIntel[key][1]

            if result is False:
                self.roundIntel[key][0] = currentNegative + 1
                for t in self.roundTrusties:
                    tname = str(t)
                    if t is key:
                        self.roundTrusties.pop(t)
            else:
                self.roundIntel[key][1] = currentPositive + 1

            count += 1

    def sabotage(self):
        tries = self.game.tries
        wins = self.game.wins

        if wins < 2:  # Attempt to only sabotage when it's least likely to look less suspicious
            return False
        elif tries >= 2:
            return True
        else:
            return True

    def onGameComplete(self, win, spies):

        for p in self.players:
            name = str(p)
            uselessNum, newName = name.split("-")
            checkForDot = newName.find(".")
            if (checkForDot != -1):
                uselessDot, newName = newName.split(".")

            key = newName
            currentNegative = self.intel[key][0]
            currentPositive = self.intel[key][1]
            self.intel[key][0] = currentNegative + self.roundIntel[key][0]

            if p not in spies:  # Only add positive points if the bot was not a spy
                self.intel[key][1] = currentPositive + self.roundIntel[key][1]