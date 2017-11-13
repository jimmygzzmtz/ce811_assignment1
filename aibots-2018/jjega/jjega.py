import collections
import random

from player import Bot
import pickle
from stats import GameData
import numpy as np


DTree_pk=open("./aibots-2018/jjega/DTreemodel.pkl",'rb')
nn_pk=open("./aibots-2018/jjega/NNModel.pkl","rb")
DTree=pickle.load(DTree_pk)
nn=pickle.load(nn_pk)


class JJEGABOT(Bot):
    def __init__(self, game,index,role):
        super().__init__(game,index,role)

    def onGameRevealed(self, players, spies):
        self.players=players
        self.spies=spies
        self.GamePrediction=[]
        self.GameStats=collections.defaultdict(GameData)

    def onMissionAttempt(self, mission, tries, leader):
        self.missionPrediction={"selection":collections.defaultdict(bool),"voting":collections.defaultdict(bool)}

    def select(self,players,count):
        if self.game.turn<2 or self.spy:
            res=list(filter(lambda x: x not in self.spies,self.others()))
            return [self]+list(random.sample(res,count-1))
        spies = []
        for p in self.players:
            prediction=self._predict(self._getData(p.name))
            self.missionPrediction["selection"][p.name]=prediction
            if prediction : spies.append(p)
        res=self.others()
        if len(spies)>1 and len(spies)<3:res=filter(lambda x: x not in spies,self.others())
        return [self] + random.sample(list(res),count-1)

    def vote(self,team):
        if self.spy:
            spies=[p for p in team if p in self.spies]
            return len(spies)>0

        if (self.game.turn==1 or self.game.turn==2 or self.game.turn==3) and self.game.tries<4:
            return (self in self.game.team)
        if self.game.tries>3 : return True


        spies=[]
        for p in team:
            prediction=self._predict(self._getData(p.name))
            self.missionPrediction["voting"][p.name]=prediction
            if prediction:spies.append(p)
        return len(spies)<1


    def sabotage(self):
        if self.spy:
            return True
        return False

    def onGameComplete(self, win, spies):
        for p in self.game.players:
            self.GameStats[p.name].Label = bool(p in spies)


    def onMissionComplete(self, sabotaged):
        self.GameStats[self.game.leader.name].leadSucMission.sample(1)
        for p in self.game.team:
            self.GameStats[p.name].sabotages.sample(int(sabotaged))
            self.GameStats[p.name].passeds.sample(len(self.game.team) - sabotaged)
            self.GameStats[p.name].selectedPass.sample(1)

        for c, p in enumerate(self.game.team):
            self.GameStats[p.name].votedNoPass.sample(int(self.game.votes[c]))
            self.GameStats[p.name].votedYesPass.sample(int(self.game.votes[c]))
        self.GamePrediction.append(self.missionPrediction)

    def onMissionFailed(self, leader, team):
        # recording votedYesFail and votedNoFail
        self.GameStats[self.game.leader.name].leadFailMission.sample(1)
        for p in team:
            self.GameStats[p.name].selectedFail.sample(1)
        for c, p in enumerate(self.game.players):
            self.GameStats[p.name].votedNoFail.sample(int(self.game.votes[c]))
            self.GameStats[p.name].votedYesFail.sample(int(self.game.votes[c]))
        self.GamePrediction.append(self.missionPrediction)

    def onVoteComplete(self, votes):
        # recording leadTeam, voted, votedYes and VotedNO
        if sum(votes)>2:
            self.GameStats[self.game.leader.name].leadTeam.sample(1)
            for p in self.game.team:
                self.GameStats[p.name].selected.sample(1)
        for c, p in enumerate(self.game.players):
            self.GameStats[p.name].voted.sample(1)
            self.GameStats[p.name].votedNo.sample(int(not votes[c]))
            self.GameStats[p.name].votedYes.sample(int(votes[c]))

    def _getData(self,player):
        data=self.GameStats[player]
        attributes=data.attributes()
        attributes.remove("Label")
        values=np.array([data.__dict__[a].total for a in attributes])
        values=np.delete(values,[0,3],axis=0) #droping the columns leadTeam and voted
        values=values.reshape((1,-1))
        return values

    def _predict(self,data):
        return nn.predict(data)




