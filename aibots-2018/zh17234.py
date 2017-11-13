from player import Bot
import random
from game import State
import random

class zh17234(Bot):

    def onGameRevealed(self, players, spies):

        self.spies=spies
        self.posibilities={}#posibility of  player is a spy in one mission
        self.suspicion={}#value to measure player if or not spy. larger are more prop be spy.
        self.spyNum=2
        self.isSpy=[]
        self.isRes=[]
        if not self.spy:
            for p in self.others():
                self.posibilities[p]=0
            for p in self.others():
                self.suspicion[p]=self.spyNum/len(self.others())

    def select(self, players, count):

        selectTeam=[self]
        resultList=[]
        if not self.spy:
            selectTeam.extend(self.isRes+self.GetLestSuspicion(count-1))
            i=0
            for p in selectTeam :
                if p not in resultList:
                    resultList.append(p)
                    i+=1
                if i==count:
                    break

            return resultList
        if self.spy:
            return[self] + random.sample(self.others(), count - 1)


    def vote(self, team):

        self.team = team
        myVote=False
        if self.game.turn==1:
            myVote = True
        else:
            if not self.spy:
                if self.game.leader==self:
                    myVote=True
                elif team==self.isRes+[self]:
                    myVote = True
                elif self.game.losses==2:
                    myVote=True
                for p in team:
                    if p in self.isSpy:
                        myVote=False
                    if p==sorted(self.suspicion,key=lambda x:self.suspicion[x])[-1]:
                        myVote=True

        if self.spy:
            if self in team:
                 myVote=True
            if self.game.losses==2 or self.game.wins==2:
                for p in self.spies:
                    if p in team:
                        myVote=True

        return myVote

    def onVoteComplete(self, votes):
        voteDict=dict(zip(self.game.players,votes))
        voteup=[p for p in self.game.players if voteDict[p]==True]
        if not self.spy:
            for p in voteup:
                if p in self.others():
                    if p  not in self.team:
                        if self.game.losses == 2 or self.game.wins == 2:
                            self.suspicion[p] += 2
                            self.isSpy.append(p)
                        else:
                            self.suspicion[p] += 0.5

    def sabotage(self):
        self.log.debug("never sabotage the missions with only two player.")
        if  len(self.game.team) < 3:
            return False
        return True

    def onMissionComplete(self, sabotaged):
        self.susTeam=[p for p in self.game.team if p in self.others()]
        self.notInTeam=[q for q in self.others() if q not in self.team]
        if not self.spy:
            if len(self.team)<3:

                if sabotaged==0:
                    if self not in self.team:
                        for p in self.susTeam:
                            self.posibilities[p]=6/10*1/2+1/10*1
                        for q in self.notInTeam:
                            self.posibilities[q]=3/10+6/10*1/2
                    if self  in self.team:
                        for p in self.susTeam:
                            self.posibilities[p]=6/10
                        for q in self.notInTeam:
                            self.posibilities[q]=3/10*2/3+6/10*1/3

                elif sabotaged==1:

                    if self not in self.team:
                        for p in self.susTeam:
                            self.posibilities[p]=6/7*1/2+1/7
                        for q in self.notInTeam:
                            self.posibilities[q]=6/7*1/2
                    elif self in self.team:
                        for p in self.susTeam:
                            self.posibilities[p]=1
                        for q in self.notInTeam:
                            self.posibilities[q]=1/3

                elif sabotaged==2:
                    for p in self.susTeam:
                        self.posibilities[p]=1
                    for q in self.notInTeam:
                        self.posibilities[q]=0

            elif len(self.team)==3:

                if sabotaged == 0:

                    for p in self.susTeam:
                        self.posibilities[p] =0
                    for q in self.notInTeam:
                        self.posibilities[q] =1

                elif sabotaged == 1:

                    if self not in self.team:
                        for p in self.susTeam:
                            self.posibilities[p] = 6/9 *1/3 +3/9*2/3
                        for q in self.notInTeam:
                            self.posibilities[q] =6/9*1/2
                    elif self in self.team:
                        for p in self.susTeam:
                            self.posibilities[p] =2/3*1/2+1/3
                        for q in self.notInTeam:
                            self.posibilities[q] = 2/3*1/2

                elif sabotaged==2:

                    for p in self.susTeam:
                        self.posibilities[p]=1
                    for q in self.notInTeam:
                        self.posibilities[q]=0

            for p in self.posibilities:
                self.suspicion[p] = self.suspicion[p] + self.posibilities[p]
                if self.posibilities[p]==0:
                    self.isRes.append(p)
                    self.suspicion[p]=0
                if self.posibilities[p]==1:
                    self.isSpy.append(p)


    def GetLestSuspicion(self,count):
        minSus=[]
        self.sortedSus=sorted(self.suspicion.items(),key=lambda k:k[1])
        for i in self.sortedSus[0:count]:
            minSus.append(i[0])
        return minSus






