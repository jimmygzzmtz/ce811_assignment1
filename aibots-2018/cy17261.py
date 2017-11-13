from player import Bot
import random
class Cy17261(Bot):
    def onGameRevealed(self, players, spies):
        # to calculater spy probability for resistances
        self.spyProbabilities = {}           # create a dict to record spyProbabilities
        self.spyProbabilities.clear        # clean the dict every new game
        for s in players:                   # set deveryone spyProbabilities is 0.0 initial
            self.spyProbabilities[s] = 0.0

        self.playVotes={}                   # create a dict to record every player's vote state, Up or Down
        self.playVotes.clear             # clean the dict every new game
        self.playVotes = players            # add name into the dict

        self.playerWhoVoteUp={}             # create a dict to record players who vote up
        self.playerWhoVoteUp.clear        # clean the dict every new game

        self.playerWhoVoteDown = {}         # create a dict to record players who vote down
        self.playerWhoVoteDown.clear      # clean the dict every new game

        self.lastGameSab = 0                # create a variable to record the number of sabtaged last turn

        self.playerLength = len(players)    # get player length
        self.HighRisk = False               # create a bool to deteming current situation

        #for spy only
        if self.spy == True:                        # if im a spy
            self.spyTeam = {}                        # create a dict to record spy players
            self.spyTeam.clear                     # clean the dict every new game
            self.spyTeam = spies                     # add name into the dict from self.game.spies
            self.spyTeamList = list(self.spyTeam )   # translate dict to list

            self.resTeam = []           # create a list to record resistance player
            del self.resTeam[:]        # clean the dict every new game

            # get the name of spy in player list
            if self.playerLength == 5 or self.playerLength == 6:
                n1, n2 = self.spyTeamList
            if self.playerLength == 7 or self.playerLength == 8 or self.playerLength == 9:
                n1, n2, n3 = self.spyTeamList
            if self.playerLength == 10:
                n1, n2, n3 ,n4 = self.spyTeamList
            # add player into resTeam if he is not a spy
            for s in players:
                if self.playerLength == 5 or self.playerLength == 6:
                    if n1 == s:continue
                    if n2 == s:continue
                if self.playerLength == 7 or self.playerLength == 8 or self.playerLength == 9:
                    if n1 == s:continue
                    if n2 == s:continue
                    if n3 == s:continue
                if self.playerLength == 10:
                    if n1 == s:continue
                    if n2 == s:continue
                    if n3 == s:continue
                    if n4 == s:continue
                self.resTeam.append(s)              # add player into resTeam if he is not a spy

    def select(self, players, count):
        if not self.spy:                                            # if im not a spy
            if self.game.turn == 1:                                 # if this is the first turn
                return [self] + random.sample(self.others(), 1)     # select random for no information
            else:                                                   #if no the fisrt turn
                list = self.SelectTeamNotSpy(count)                 # get low spyProbabilities players
                return list                                         #select low spyProbabilities players
        else:
            return random.sample(self.spyTeamList, 1)+ random.sample(self.resTeam, count - 1)

    def vote(self, team):

        if not self.spy:
            if self.game.turn == 1:
                return False

            Top1 = self.getListName(0)
            Top1Value = self.getListValue(0)
            if Top1 in team:
                if (Top1Value > 0.5):
                    return False

            Top2 = self.getListName(1)
            Top2Value = self.getListValue(1)
            if Top2 in team:
                if (0.6 >Top2Value > 0.4):
                    self.HighRisk = True
                    return random.choice([True,False, False])
                if Top2Value > 0.6:
                    self.HighRisk = True
                    return False
                else:
                    self.HighRisk = False
                    return True
            else:
                return True

        else:# if im a spy
            return len(self.spyTeam) > len([p for p in self.game.team if p in self.spyTeam]) > 0

    def onVoteComplete(self, votes):

        self.playerWhoVoteUp.clear
        self.playerWhoVoteDown.clear

        for x in range(0, self.playerLength):
            if votes[x] == True:
                voter = self.playVotes[x]
                self.playerWhoVoteUp[voter] = True
            if votes[x] == False:
                voter = self.playVotes[x]
                self.playerWhoVoteDown[voter] = False

    def sabotage(self):
        if self.spy:
            if self.game.turn == 1:
                return random.choice([True, True, False])
            else:
                otherSpyInside = len([p for p in self.game.team if p in self.spyTeam])> 1
                if otherSpyInside: return ([True, False, False])
                return True
        else:
            return False

    def onMissionComplete(self, sabotaged):
        self.lastGameSab = sabotaged

        if not self.spy:
            if (self in self.game.team):  # im in the team, so take me out when calculate spyProbability
                if (len(self.game.team) == 2):
                    for s in self.game.team:
                        self.spyProbabilities[s] = 3.3
                else:
                    for s in self.game.team:
                        storePreviousSpyProbility = self.spyProbabilities[s]
                        self.spyProbabilities[s] = self.lastGameSab / (len(self.game.team) - 1)

                        if (self.spyProbabilities[s] < storePreviousSpyProbility):
                            self.spyProbabilities[s] = storePreviousSpyProbility
                        else:
                            self.spyProbabilities[s] = self.lastGameSab / (len(self.game.team) - 1)
                        self.spyProbabilities[self] = 0.0
                        break

            else:  # if im not in the team
                for s in self.game.team:
                    storePreviousSpyProbility = self.spyProbabilities[s]
                    self.spyProbabilities[s] = self.lastGameSab / len(self.game.team)

                    if (self.spyProbabilities[s] < storePreviousSpyProbility):
                        self.spyProbabilities[s] = storePreviousSpyProbility
                    else:
                        self.spyProbabilities[s] = self.lastGameSab / len(self.game.team)
                    self.spyProbabilities[self] = 0.0
                    break

    def announce(self):

        if self.lastGameSab>0:
            # if this mission lose, then the player who vote up has probability as a spy, because his mate in the team
            for voter in self.playVotes:
                if voter in self.playerWhoVoteUp:
                    self.spyProbabilities[voter] += 0.2
                if voter in self.playerWhoVoteDown:
                    self.spyProbabilities[voter] -= 0.1
                    # if this mission win, then the player who vote down has probability as a spy, because he or his mate not in the team

        if self.lastGameSab == 0:
            for voter in self.playVotes:
                if voter in self.playerWhoVoteDown:
                    self.spyProbabilities[voter] += 0.2
                if voter in self.playerWhoVoteUp:
                    self.spyProbabilities[voter] -= 0.1

    def SelectTeamNotSpy(self,n):
        last1 = self.getListName(self.playerLength - 1)
        last2 = self.getListName(self.playerLength - 2)
        last3 = self.getListName(self.playerLength - 3)
        last4 = self.getListName(self.playerLength - 4)

        lowRiskList2 = [last1, last2]
        lowRiskList3 = [last1, last2, last3]
        lowRiskList4 = [last1, last2, last3, last4]

        if n == 2:
            return lowRiskList2
        if n == 3:
            return lowRiskList3
        if n == 4:
            return lowRiskList4

    def getListName (self,n): # sort dictionary by value so that can take out the pot 1 highest spyprobablity, and when it in the team, always vote down
        sortByValue = sorted(self.spyProbabilities.items(), key=lambda t: t[1], reverse=True)
        n2 = list(sortByValue)[n]
        k, v = n2
        return k

    def getListValue (self,n): # sort dictionary by value so that can take out the pot 1 highest spyprobablity, and when it in the team, always vote down
        sortByValue = sorted(self.spyProbabilities.items(), key=lambda t: t[1], reverse=True)
        n2 = list(sortByValue)[n]
        k, v = n2
        return v