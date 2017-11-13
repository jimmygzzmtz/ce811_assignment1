from player import Bot

# Each bot has access to the game state, stored in the self.game member
# variable.  See the State class in game.py for the full list of variables you
# have access to from your bot.
#
# The examples below purposefully use only self.game to emphasize its
# importance.  Advanced bots tend to only use the game State class to decide!
from game import State


# Many bots will use random decisions to break ties between two equally valid
# options.  The simple bots below rely on randomness heavily, and expert bots
# tend to use other statistics and criteria (e.g. who is winning) to avoid ties
# altogether!
import random

class yr17444(Bot):

    #An bot try to confuse others

    def onGameRevealed(self, players, spies):
        self.spyProbabilities = {}
        self.spyProbabilities.clear()
        self.mathCount={}
        self.mathCount.clear()
        self.mathCount1={}
        self.mathCount1.clear()
        self.voteF=0
        self.spies = spies
        self.tempUse = {}
        self.voteUp = {}
        self.voteDown={}
        self.playVotes={}
        self.playVotes = players

        for s in players:
            self.spyProbabilities[s] = 0.0

    def select(self, players, count):
        if not self.spy:
            if self.game.turn == 1:
                return [self] + random.sample(self.others(), count - 1)
            else:
                return self.tempTrust(count)
        else:
            if self.game.turn==1:
                return [self] + random.sample(self.others(), count - 1)
            else:
                #select two spies to confuse others
                return list(self.spies) + random.sample(set(self.game.players) - set(self.spies), count - 2)


    def vote(self, team):
        if self.game.leader:
            return True
        else:
            if not self.spy:
                if self.game.turn==1:
                    return random.choice([True, False])
                else:
                    #if high spyProbabilities player in the team,false
                    if (self.cantBelieve() in team):
                        return False
                    else:
                        return True
            else:
                if self in team:
                    return True
                else:
                    if len(team)>=3:
                        return True
                    else:
                        return False

    def onVoteComplete(self, votes):
        #players who vote up and down
        self.voteUp.clear()
        self.voteDown.clear()
        for x in range(0, len(self.game.team)):
            if votes[x] == True:
                voter = self.playVotes[x]
                self.voteUp[voter] = True
            if votes[x] == False:
                voter = self.playVotes[x]
                self.voteDown[voter] = False
        if not self.spy:
            #may konw something when they vote down
            for s in self.voteDown:
                self.spyProbabilities[s]=self.spyProbabilities[s]+0.1

    def sabotage(self):
        if self.game.wins==2:
            return True
        else:
            if len(self.game.team)==2:
                #cannot hide myself
                return False
            else:
                return True


    def onMissionComplete(self, sabotaged):
        self.voteF = self.game.sabotages
        if self.voteF > 0:
            for s in self.voteUp:
                #someone in theem maybe spy
                if self.voteF==1:
                    self.spyProbabilities[s] = self.spyProbabilities[s] + 0.2
                else:
                    if self.voteF==2:
                        self.spyProbabilities[s] = self.spyProbabilities[s] + 0.1

    def announce(self):
        if not self.spy and self.voteF>0:
            if self in self.game.team:
                for s in self.game.team:
                    self.mathCount = self.spyProbabilities.copy()
                    self.mathCount[s]=self.mathCount[s]*0.4
                    self.mathCount1[s] = self.voteF / (len(self.game.team) - 1)
                    self.spyProbabilities[s] = self.mathCount1[s]+self.mathCount[s]

            else:
                for s in self.game.team:
                    self.mathCount = self.spyProbabilities.copy()
                    self.mathCount[s] = self.mathCount[s] * 0.4
                    self.mathCount1[s] = self.voteF / (len(self.game.team))
                    self.spyProbabilities[s] = self.mathCount1[s] + self.mathCount[s]
            self.spyProbabilities[self] = 0.0
            self.mathCount.clear()
            self.mathCount1.clear()
        self.tempUse.clear()
        self.tempUse=self.spyProbabilities.copy()

    def cantBelieve(self):
        sorted(self.tempUse.items(), key=lambda item: item[1],reverse=True)
        kCant = list(self.tempUse)
        kCant1 = [kCant[0], kCant[1]]
        return kCant1

    def tempTrust(self, count):
        sorted(self.tempUse.items(), key=lambda item: item[1])
        kValue=list(self.tempUse)
        kValue2=[kValue[0],kValue[1]]
        kValue3=[kValue[0],kValue[1],kValue[2]]
        kValue4=[kValue[0],kValue[1],kValue[2],kValue[3]]
        kValue5=[kValue[0],kValue[1],kValue[2],kValue[3],kValue[4]]
        if count==2:
            return kValue2
        if count==3:
            return kValue3
        if count==4:
            return kValue4
        if count==5:
            return kValue5

