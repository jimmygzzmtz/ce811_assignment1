import logging
import logging.handlers

import core

from player import Bot

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
    """This is the base class for your AI in THE RESISTANCE.  To get started:
         1) Derive this class from a new file that will contain your AI.  See
            bots.py for simple stock AI examples.

         2) Implement mandatory API functions below; you must re-implement
            those that raise exceptions (i.e. vote, select, sabotage).

         3) If you need any of the optional callback API functions, implement
            them (i.e. all functions named on*() are callbacks).

       Aside from parameters passed as arguments to the functions below, you 
       can also access the game state via the self.game variable, which contains
       a State class defined in game.py.

       For debugging, it's recommended you use the self.log variable, which
       contains a python logging object on which you can call .info() .debug()
       or warn() for instance.  The output is stored in a file in the #/logs/
       folder, named according to your bot. 
    """

    __metaclass__ = core.Observable

    """Version 0.0.1"""

    def onGameRevealed(self, players, spies):
        """This function will be called to list all the players, and if you're
        a spy, the spies too -- including others and yourself.
        @param players  List of all players in the game including you.
        @param spies    List of players that are spies, or an empty list.
        """
        #2 spies for 5 players, empty = not a spy
        self.players = players
        self.spies = spies

        # load the unpickle object into a variable
        self.rfc = pickle.load(open('rfc_pickle.pkl', 'rb'))
        self.sc = pickle.load(open('sc_pickle.pkl', 'rb'))

        self.blackboard = []
        self.predictionList = []

        playerList = []

        with open('playerList.csv', 'r') as csvfile:
            if(os.stat("playerList.csv").st_size != 0):
                playerList = list(csv.reader(csvfile))[0]

        for i in range(0, len(players)):
            nameInt = -1
            if(str(players[i])[2:] != 'JimmyBotSciKitLearn'):
                nameInt = playerList.index(str(players[i])[2:])
            #player, voted yes sabotaged, voted no sabotaged, votes yes succeeded, voted no succeeded, votes yes failed, voted no failed, in team succeeded, in team sabotaged, leader succeeded, leader sabotaged
            playerTemplate = [nameInt,0,0,0,0,0,0,0,0,0,0]
            self.blackboard.append(playerTemplate)

    def onMissionAttempt(self, mission, tries, leader):
        """Callback function when a new turn begins, before the
        players are selected.
        @param mission  Integer representing the mission number (1..5).
        @param tries    Integer count for its number of tries (1..5).
        @param leader   A Player representing who's in charge.
        """
        pass

    def select(self, players, count):
        """Pick a sub-group of players to go on the next mission.
        @param players  The list of all players in the game to pick from.
        @param count    The number of players you must now select.
        @return list    The players selected for the upcoming mission.
        """

        
        
         #id, susp

        memberRes1 = -1
        memberRes2 = -1
        teamList = []

        #print(players[0])

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
            #include players that are not predicted to be spies

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
            
        #print(rfc.predict)

        #print(teamList)
        return teamList

        #return random.sample(self.game.players, count)



    def onTeamSelected(self, leader, team):
        """Called immediately after the team is selected to go on a mission,
        and before the voting happens.
        @param leader   The leader in charge for this mission.
        @param team     The team that was selected by the current leader.
        """
        pass

    def vote(self, team):
        """Given a selected team, decide whether the mission should proceed.
        @param team      List of players with index and name. 
        @return bool     Answer Yes/No.
        """ 

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
        """Callback once the whole team has voted.
        @param votes        Boolean votes for each player (ordered).
        """
        pass

    def sabotage(self):
        """Decide what to do on the mission once it has been approved.  This
        function is only called if you're a spy, otherwise you have no choice.
        @return bool        Yes to shoot down a mission.
        """
        if(self.game.team == 2):
            return False

        return True 

    def onMissionComplete(self, sabotaged):
        """Callback once the players have been chosen.
        @param sabotaged    Integer how many times the mission was sabotaged.
        """

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
        
        #self.updatePredictionList(self)

    def onMissionFailed(self, leader, team):
        """Callback once a vote did not reach majority, failing the mission.
        @param leader       The player responsible for selection.
        @param team         The list of players chosen for the mission.
        """
        
        for i in range(0, len(self.players)):
            if(self.game.votes[i] == True):
                self.blackboard[i][5] += 1
            else:
                self.blackboard[i][6] += 1
        
        #self.updatePredictionList(self)

        pass

    def announce(self):
        """Publicly state beliefs about the game's state by announcing spy
        probabilities for any combination of players in the game.  This is
        done after each mission completes, and takes the form of a mapping from
        player to float.  Not all players must be specified, and of course this
        can be innacurate!

        @return dict[Player, float]     Mapping of player to spy probability.
        """
        return {}

    def onAnnouncement(self, source, announcement):
        """Callback if another player decides to announce beliefs about the
        game.  This is passed as a potentially incomplete mapping from player
        to spy probability.

        @param source        Player making the announcement.
        @param announcement  Dictionnary mapping players to spy probabilities.
        """
        pass

    def say(self, message):
        """Helper function to print a message in the global game chat, visible
        by all the other players.

        @param message       String containing free-form text.
        """
        self.log.info(message)

    def onMessage(self, source, message):
        """Callback if another player sends a general free-form message to the
        channel.  This is passed in as a generic string that needs to be parsed.

        @param source        Player sending the message.
        @param announcement  Arbitrary string for the message sent.
        """
        pass

    def onGameComplete(self, win, spies):
        """Callback once the game is complete, and everything is revealed.
        @param win          Boolean true if the Resistance won.
        @param spies        List of only the spies in the game.
        """
        #print(self.predictionList)
        """
        if(self.predictRFC(self,0) == 1):
            print("0 IS A SPY")
        else:
            print('0 is not a spy... :(')
        """
        pass
    
    def updatePredictionList(event, self):
        ratioData = []

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
        
        self.predictionList = ratioData
    
    def predictRFC(event, self, i):
        sc = StandardScaler()
        self.updatePredictionList(self)
        Xnew = [self.predictionList[i]]
        Xnew = self.sc.transform(Xnew)
        ynew = self.rfc.predict(Xnew)
        return ynew[0]


    def others(self):
        """Helper function to list players in the game that are not your bot."""
        return [p for p in self.game.players if p != self]

    def __init__(self, game, index, spy):
        """Constructor called before a game starts.  It's recommended you don't
        override this function and instead use onGameRevealed() to perform
        setup for your AI.
        @param game     the current game state
        @param index    Your own index in the player list.
        @param spy      Are you supposed to play as a spy?
        """
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
        """Built-in function to support pretty-printing."""
        type = {True: "SPY", False: "RST"}
        return "<%s #%i %s>" % (self.name, self.index, type[self.spy])