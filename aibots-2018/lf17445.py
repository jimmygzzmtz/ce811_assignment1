
import random
# General syntax to import a library but no functions:
##import (library) as (give the library a nickname/alias)
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import accuracy_score

from collections import defaultdict
from player import Bot


"""The bot will not run agasint itself, meaning if there are too many copies of a single bot"""
class lf17445(Bot):
    #The 'come on... trust me' bot.
    numTriesInMission = 0
    GameVariables = {}
    GaussianBot = {}
    def onGameRevealed(self, players, spies):
        self.numTriesInMission = 0
        self.spies = spies
        self.CurrentSpace = 0
        for p in players:
            self.GameVariables[p.name] = {'data':[],'target':[]}
        #NO idea why but this code below one breaks the dictionnary if I dont do this....
        for p in players:
            if p.name not in self.GaussianBot:
                self.GaussianBot[p.name] = {}
        #Partial GaussianNB for [try,turn,Vote, InMission, Leader]
    #Add team that has least probable stats of being a spy
    def select(self, players, count):
        turn = self.game.turn
        #SPY
        if self.spy:
            otherSpies = [ p for p in self.spies if p != self]
            if turn == 1:
                return random.sample(self.others(), count)

            if turn == 2 and turn == 3:
                return [self] + random.sample(self.others(), count - 1)

            if turn == 4 and self.game.losses == 1:
                sp = random.sample(otherSpies,1)
                return [self] + list(sp) + random.sample(set(self.game.players) - set(self.spies) - set(sp), count-2)
            if turn == 4 and self.game.losses == 2:
                return random.sample(self.others(), count)

            if (turn == 5):
                return list(self.spies) + random.sample(set(self.game.players) - set(self.spies), count-2)

            return [self] + random.sample(self.others(), count - 1)

        #RESISTANCE
        else:
            if(len(self.GameVariables['lf17445']['data']) > 0):
                RISK = 0.0
                counterP = count-1
                InTurn = []
                InTurn.append(self)
                for p in self.game.players:
                    if p != self:
                        if 'gnb' in self.GaussianBot[p.name]:
                            prob = self.GaussianBot[p.name]['gnb'].predict_proba(self.GameVariables[p.name]['data'])
                            aux = 0.0
                            for i in range(len(prob)):
                                aux = aux + prob[i][0]
                            RISK = aux/len(prob)
                            if counterP > 0 :
                                if RISK < 0.45:
                                    InTurn.append(p)
                                    counterP =  counterP-1
                        else:
                            [self] + random.sample(self.others(), count - 1)

                if counterP > 0:
                    return InTurn + random.sample(set(self.game.players)-set(InTurn),counterP)
                else:
                    return InTurn

            return [self] + random.sample(self.others(), count - 1)

    def vote(self, team):
        # There's at least one [other] spy there.
        if self.spy:
                #Would loose other wise
            if self.game.tries == 5:
                return False

            return len([p for p in self.game.team if p in self.spies]) >0
        #RESISTANCE
        #IS THE TEAM BELOW A 45% chance of having a spy on it?
        #There needs to be some variables from the current game
            #Would loose other wise
        if self.game.tries == 5:
            return True
        if(len(self.GameVariables['lf17445']['data']) > 0):
            RISK = 0.0
            for p in self.game.team:
                if p != self:
                    if 'gnb' in self.GaussianBot[p.name]:
                        prob = self.GaussianBot[p.name]['gnb'].predict_proba(self.GameVariables[p.name]['data'])
                        aux = 0.0
                        for i in range(len(prob)):
                            aux = aux + prob[i][0]
                        RISK = RISK + aux/len(prob)
                        if self in self.game.team:
                            RISK = RISK/ (len(self.game.team)-1)
                        else:
                            RISK = RISK/ len(self.game.team)
                            #print(RISK)
                            if RISK > 0.45:
                                return False
                            else:
                                return True

                    return True
        return True
    #Just to see if there are other spies in the current team
    def checkGameSpiesSab(self):
        inter = [i for i in self.game.team if i in self.spies]
        if len(inter) > 1:
            return False
        return True
    #Never risk thy self, even if its the last round
    def sabotage(self):
        # Shoot down only missions with more than another person.
        #priority if about to loose
        if self.game.wins == 2:
            return True
        #I dont want to risk myself
        if self.game.turn == 1:
            return self.checkGameSpiesSab()
        #No reason to risk myself if there's someone else
        #if we already won 1 we might as well go at it.
        if self.game.turn == 2 and self.game.losses == 1:
            return True
        #if self.game.turn == 2:
        #    return False
        if self.game.turn == 4 and self.game.losses == 1:
            return not self.checkGameSpiesSab()
        if self.game.turn == 4 and self.game.losses == 2:
            return False

        return self.checkGameSpiesSab()

    def onGameComplete(self, win, spies):
        for p in self.game.players:
            if p in spies:
                for i in range(self.numTriesInMission):
                    self.GameVariables[p.name]['target'].append(0)
            else:
                for i in range(self.numTriesInMission):
                    self.GameVariables[p.name]['target'].append(1)
        """Credits for how to use the GaussianNB() function
            Pretty sure I dont need that ' model' thing... since I believe the function calls
            to itself and I check the stats on the 'gnb' anyway.
            but never the less I did check how the function was called here
         https://www.digitalocean.com/community/tutorials/how-to-build-a-machine-learning-classifier-in-python-with-scikit-learn"""
        for p in self.game.players:
            data = self.GameVariables[p.name]
            # Organize our data
            if 'gnb' not in self.GaussianBot[p.name]:
                self.GaussianBot[p.name]['gnb'] = GaussianNB()

            self.GaussianBot[p.name]['model'] = self.GaussianBot[p.name]['gnb'].partial_fit(data['data'],data['target'],[0,1])

    def onVoteComplete(self, votes):
        """Callback once the whole team has voted.
        @param votes        Boolean votes for each player (ordered).
        """
        self.numTriesInMission += 1
        i = 0
        inMission = False
        leader = False
        for p in self.game.players:
            if p in self.game.team:
                inMission = True
            else:
                inMission = False
            if p == self.game.leader:
                leader = True
            else:
                leader = False
            vote = votes[i]
            self.GameVariables[p.name]['data'].append([self.game.turn,inMission,leader,votes[i]])
            i +=1
