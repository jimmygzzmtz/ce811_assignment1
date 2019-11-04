import logging
import logging.handlers

import core

from player import Bot

#Used for the SciKitLearn Model
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix, classification_report
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
import pickle
import os
import csv
import random

class JimmyBotSciKitLearn(Bot):

    __metaclass__ = core.Observable

    def onGameRevealed(self, players, spies):
        self.players = players
        self.spies = spies

        #load the rfc and sc from pickle
        self.rfc = pickle.load(open('rfc_pickle.pkl', 'rb'))
        self.sc = pickle.load(open('sc_pickle.pkl', 'rb'))

        #initialize the lists used to keep track and make predictions of players
        self.blackboard = []
        self.predictionList = []
        
        #read the list of players to be able to assign scalar values to them
        playerList = []
        with open('playerList.csv', 'r') as csvfile:
            if(os.stat("playerList.csv").st_size != 0):
                playerList = list(csv.reader(csvfile))[0]

        #Assign ints to the players for the blackboard, based on the playerList.csv
        for i in range(0, len(players)):
            nameInt = -1
            if(str(players[i])[2:] != 'JimmyBotSciKitLearn'):
                nameInt = playerList.index(str(players[i])[2:])
            
            #player, voted yes sabotaged, voted no sabotaged, votes yes succeeded, voted no succeeded, votes yes failed, voted no failed, in team succeeded, in team sabotaged, leader succeeded, leader sabotaged
            playerTemplate = [nameInt,0,0,0,0,0,0,0,0,0,0]
            self.blackboard.append(playerTemplate)

    def onMissionAttempt(self, mission, tries, leader):
        pass

    def select(self, players, count):
        #Values used to assign team members
        memberRes1 = -1
        memberRes2 = -1
        teamList = []

        if(self.spy):
            #find resistance members that predicts to be spy to fool people, if not choose the first that are not chosen yet
            memberRes1 = self
            memberRes2 = self

            for i in range(0, len(players)):
                if(self.predictRFC(self,i) == 1 and players[i] not in self.spies):
                    memberRes1 = players[i]
                    break
            
            for i in range(0, len(players)):
                if(self.predictRFC(self,i) == 1 and players[i] not in self.spies and memberRes1 != players[i]):
                    memberRes2 = players[i]
                    break
            
            if(memberRes1 == self):
                for i in range(0, len(players)):
                    if(players[i] not in self.spies):
                         memberRes1 = players[i]
                         break
            
            if(memberRes2 == self):
                for i in range(0, len(players)):
                    if(players[i] not in self.spies and memberRes1 != players[i]):
                         memberRes2 = players[i]
                         break

            if(count == 2):
                teamList = [self,memberRes1]
            if(count == 3):
                teamList = [self,memberRes1,memberRes2]
        
        else:
            #include players that are not predicted to be spies, if not choose players that aren't the player

            memberRes1 = self
            memberRes2 = self

            for i in range(0, len(players)):
                if(self.predictRFC(self,i) == 0 and self != players[i]):
                    memberRes1 = players[i]
                    break
            
            for i in range(0, len(players)):
                if(self.predictRFC(self,i) == 0 and self != players[i] and memberRes1 != players[i]):
                    memberRes2 = players[i]
                    break
            
            if(memberRes1 == self):
                for i in range(0, len(players)):
                    if(self != players[i]):
                        memberRes1 = players[i]
                        break
            
            if(memberRes2 == self):
                for i in range(0, len(players)):
                    if(memberRes1 != players[i] and self != players[i]):
                         memberRes2 = players[i]
                         break

            if(count == 2):
                teamList = [self,memberRes1]
            if(count == 3):
                teamList = [self,memberRes1,memberRes2]
            
        return teamList


    def onTeamSelected(self, leader, team):
        pass

    def vote(self, team):

        #always vote yes on the first turn
        if(self.game.turn == 1 and self.game.tries == 1):
            return True

        #always vote yes when leader
        if(self == self.game.leader):
            return True
        
        #if on last try and spy, return false, otherwise true
        if self.game.tries == 5:
            return self.spy

        #if there is a spy in the team, vote yes
        if(self.spy):
            for i in range(0, len(team)):
                if(team[i] in self.spies):
                    return True
            return False
        else:
            #if a team member is predicted to be a spy, vote no
            for i in range(0, len(team)):
                if(self.predictRFC(self,self.players.index(team[i])) == 1):
                    return False
            return True

    def onVoteComplete(self, votes):
        pass

    def sabotage(self):
        #don't sabotage if only 2 in team, since it drastically increases supicion, otherwise do sabotage
        if(self.game.team == 2):
            return False

        return True 

    def onMissionComplete(self, sabotaged):
        #add respective values to blackboard
        for i in range(0, len(self.players)):
            if(sabotaged == True):
                if(self.game.votes[i] == True):
                    self.blackboard[i][1] += 1
                else:
                    self.blackboard[i][2] += 1
                if(self.players[i] in self.game.team):
                    self.blackboard[i][8] += 1
                if(self.players[i] == self.game.leader):
                    self.blackboard[i][10] += 1
            if(sabotaged == False):
                if(self.game.votes[i] == True):
                    self.blackboard[i][3] += 1
                else:
                    self.blackboard[i][4] += 1
                if(self.players[i] in self.game.team):
                    self.blackboard[i][7] += 1
                if(self.players[i] == self.game.leader):
                    self.blackboard[i][9] += 1
        

    def onMissionFailed(self, leader, team):
        #add respective values to blackboard
        for i in range(0, len(self.players)):
            if(self.game.votes[i] == True):
                self.blackboard[i][5] += 1
            else:
                self.blackboard[i][6] += 1

        pass

    def announce(self):
        return {}

    def onAnnouncement(self, source, announcement):
        pass

    def say(self, message):
        self.log.info(message)

    def onMessage(self, source, message):
        pass

    def onGameComplete(self, win, spies):
        pass
    
    def updatePredictionList(event, self):
        #variable used to create the new list composed of data that is ratioed
        ratioData = []

        #for each player in the blackboard, get each ratio and nameInt, and add it to radioData
        for i in range(0, len(self.blackboard)):
            sabotagedRatio = -1
            notSabotagedRatio = -1
            failedRatio = -1
            inTeamSabotagedRatio = -1
            leaderSabotagedRatio = -1
            nameInt = self.blackboard[i][0]

            votedYesSabotaged = self.blackboard[i][1]
            votedNoSabotaged = self.blackboard[i][2]
            sabotagedTotal = votedYesSabotaged + votedNoSabotaged
            if(sabotagedTotal != 0):
                sabotagedRatio = (votedYesSabotaged / (sabotagedTotal))

            votedYesNotSabotaged = self.blackboard[i][3]
            votedNoNotSabotaged = self.blackboard[i][4]
            notSabotagedTotal = votedYesNotSabotaged + votedNoNotSabotaged
            if(notSabotagedTotal != 0):
                notSabotagedRatio = (votedYesNotSabotaged / (notSabotagedTotal))

            votedYesFailed = self.blackboard[i][5]
            votedNoFailed = self.blackboard[i][6]
            failedTotal = votedYesFailed + votedNoFailed
            if(failedTotal != 0):
                failedRatio = (votedYesFailed / (failedTotal))

            inTeamSucceeded = self.blackboard[i][7]
            inTeamSabotaged = self.blackboard[i][8]
            inTeamTotal = inTeamSucceeded + inTeamSabotaged
            if(inTeamTotal != 0):
                inTeamSabotagedRatio = (inTeamSucceeded / (inTeamTotal))

            leaderSucceeded = self.blackboard[i][9]
            leaderSabotaged = self.blackboard[i][10]
            leaderTotal = leaderSucceeded + leaderSabotaged
            if(leaderTotal != 0):
                leaderSabotagedRatio = (leaderSucceeded / (leaderTotal))

            ratioPlayer = [nameInt,sabotagedRatio,notSabotagedRatio,failedRatio,inTeamSabotagedRatio,leaderSabotagedRatio]
            
            ratioData.append(ratioPlayer)
        
        #update predictionList using the newly generated ratioData
        self.predictionList = ratioData
    
    def predictRFC(event, self, i):
        #use the rfc, while scaling the data using sc, to predict if the given player is a spy
        sc = StandardScaler()
        self.updatePredictionList(self)
        Xnew = [self.predictionList[i]]
        Xnew = self.sc.transform(Xnew)
        ynew = self.rfc.predict(Xnew)
        return ynew[0]


    def others(self):
        return [p for p in self.game.players if p != self]

    def __init__(self, game, index, spy):
        super(Bot, self).__init__(self.__class__.__name__, index)

        self.game = game
        self.spy = spy

        self.log = logging.getLogger(self.name)
        if not self.log.handlers:
            try:
                output = logging.FileHandler(filename='logs/'+self.name+'.log')
                self.log.addHandler(output)
                self.log.setLevel(logging.DEBUG)
            except IOError:
                pass

    def __repr__(self):
        type = {True: "SPY", False: "RST"}
        return "<%s #%i %s>" % (self.name, self.index, type[self.spy])