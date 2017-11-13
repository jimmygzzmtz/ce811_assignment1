'''
    Alexandros Katsiamakas bot implementation for the resistance game
    This is my assignment for the CE811 Module for Essex University (November 2017)
'''
import random
import itertools
import threading
import multiprocessing
import csv
import numpy as np
import pandas as pd

from sklearn.cross_validation import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score
from sklearn import tree

from player import Bot 
from collections import defaultdict


lock = threading.Lock()
gcount = 0


class PlayerGame(object):
    '''
	 Class that store statistics per player during a game
     Main data for train & predict AI during game
	'''

    def __init__(self):
        self.leader = 0             # how many times player is leader during a game
        self.team = 0               # how many times a playes is selected in a team
        self.spy = 0                # if player is spy =1 or not = 0 during a game
        self.missionsvoted = 0      # how many times a mission is downvoted
        self.missionsdownvoted = 0  # how many times a mission was votes
        self.turn = 0               # how many turns was in a game
        self.wins = 0               # number of wins (either as resistance or spy)
        self.losses = 0             # number of losses (either as resistance or spy)



    def getlistfromdata(self):
        '''
            Returns a list of all field values, to be used for the AI algorithm as input data
        '''
        l = []
        l.append(self.leader)
        l.append(self.team)
        l.append(self.missionsvoted)
        l.append(self.missionsdownvoted)
        l.append(self.turn)
        l.append(self.wins)
        l.append(self.losses)
        l.append(self.spy)
        return l



class PlayerBlackboard(object):
    '''
    Blackboard class that keeps ALL information  on each player
    results from the mission statistic data.
    '''

    PLAYER_MIN_SAMPLE_SIZE = 40     #min size data sample size to start train AI
    PLAYER_REFRESH_RATE = 10        #run train ai tree decision every n=10 entries

    def __init__(self, name):
        self.name = name            # name of the player
        self.playdata = []          # list that stores all game data for this player
        self.gini = None            # sklearn tree decision cached algorithm object for performance


    def getnewmissiondata(self):
        '''
        Creates new mission data for the player
        Returns a new PlayerGame object
        '''
        d = PlayerGame()            #create new statistics
        self.playdata.append(d)     #append to the game data list
        return d                    # return it for processing


    def CanMakeDecisionforAI(self):
        '''
        Decides when there is enough data to kick in the AI
        Returns True is AI should be activated or False not to activate 
        '''
        if len(self.playdata) < PlayerBlackboard.PLAYER_MIN_SAMPLE_SIZE: 
            return False
        else:
            return True

    def IsPlayerResistanceByAI(self, dd):
        '''
            This is the main implementation of Tree Decision algorithm
            Uses the sklearn tree decision
        '''
        #get the playdata list without the last element (slice list), since this is the one to check
        ll = self.playdata[:-1]
        #if no Ai object ready or every new 20 items batch, refresh AI learning algorithm
        if self.gini is None or len(ll) % PlayerBlackboard.PLAYER_REFRESH_RATE == 0:
                self.TrainAI(ll)
        #manipulate current data to request AI to give a prediction
        dlist = dd.getlistfromdata()
        dtest = dlist[:-1]                      #remove spy column from list
        ppp = np.reshape(dtest, (1,-1))         #reshape list to array
        valpredict = self.gini.predict(ppp)     # get the prediction as an array from the TreeDecision AI algorithm
        if valpredict[0] < 1:                   #if 0 then is resistance else is a spy as predicts the algorithm
            return True
        else:
            return False
        

    def savedatatofile(self):
        '''
           Helper function to save statistics to csv file, for log or debup purposes
           Not to be used on final release
        '''
        with open('logs/ak' + self.name + '.csv', 'wb') as f:
            wf = csv.writer(f, 'excel')
            for pp in self.playdata:
                wf.writerow(pp.getlistfromdata());

    def TrainAI(self, ll):
        '''
            Creates the AI algorithm object to be used for AI prediction
        '''
        #Prepare data using Panda dataframes to train the AI
        ldata = []
        for l in ll:
            ldata.append(l.getlistfromdata())
        #Create a panda dataframe using the from_records methods and passing the column names
        df = pd.DataFrame.from_records(ldata, columns = ['leader','team',  'missionsvoted','missionsdownvoted', 'turn', 'wins', 'losses', 'spy'])
        #perform slicing on datataframe for the algorithm
        xdata = df.values[:, 0:7]           #all data except spy column (last on the list)
        ydata = df.values[:, -1]            #get only spy data column
        #train the algorithm using the dataframe data using a 30% train data 
        X_train, X_test, y_train, y_test = train_test_split( xdata, ydata, test_size = 0.3, random_state = 100)
        #Create a Decision tree object with the "gini" algorithm and max_depth =3 to keep tree in a logical depth
        clf_gini = DecisionTreeClassifier(criterion = "gini", random_state = 100, max_depth=3, min_samples_leaf=5)
        #perform train
        clf_gini.fit(X_train, y_train)
        #cache the algorithm object to be used later
        self.gini = clf_gini


        
    

class akBlackboard(object):
    '''
    Blackboard class that keeps information  for all players
    This is the main global object that is alive during all program run
    Add has all players and their data in memory
    '''

    def __init__(self):
        self.players = dict()       #dictionary to keep players


    def GetPlayer(self, name):
        '''
            Creates a PlayerBlackboard for each player and adds it to the dictionary
            If player exists, just returns the PlayerBlackboard object
        '''
        if name not in self.players:
            self.players[name] = PlayerBlackboard(name)
        return self.players[name]
            

    def GetPlayerMissionData(self, name):
        '''
        Creates Mission Data for the passed player by name
        '''
        pl = self.GetPlayer(p.name)
        return pl.getnewmissiondata()



#global blackboard instance alive during all the program lifetime
bk = akBlackboard()


class ak17623(Bot):
    '''
        Bot using my implementation for resistance game using AI
    '''
   
    def onGameRevealed(self, players, spies):
        '''
            This is when a new game starts, so new data should be initialized and assigned to each player
        '''
        self.spies = spies                  #keep spies during game
        self.teamdata = dict()              #create dictiorary for statistical data for each player during a game

        global bk                           #use global blackboard object
        for p in players:
            pl = bk.GetPlayer(p.name)       #create or use player data

            #create statistic data for each player
            self.teamdata[p.name] = pl.getnewmissiondata()
            if p in spies:
                self.teamdata[p.name].spy = 1   #if spy keep this info

        self.log.debug("Revealed players=%s spies = %s spy=%s" % (players, spies, self.spy))
        #keep a counter to know how many times this bot is participated in a game        
        global gcount 
        gcount += 1

    def onGameComplete(self, win, spies):
        '''
            Game has just finished, spies are revealed.
            Time to store all this information to train the AI
        '''
        self.log.debug("Game complete win=%s spies=%s spy=%s total wins=%d losses=%d" % (win, spies, self.spy, self.game.wins,  self.game.losses))

        #time to assign all statistic data for each player
        global bk

        for p in self.game.players:
             pp = self.teamdata[p.name]
             for sp in spies:
                 if p.index == sp.index:
                     pp.spy = 1
                 else:
                     pp.spy = 0
             pp.wins = self.game.wins if pp.spy == 0 else self.game.losses
             pp.losses = self.game.losses if pp.spy == 0 else self.game.wins
             pp.turn = self.game.turn

             #for debug purposes save data - on release this is commented out
             pl = bk.GetPlayer(p.name)
             #if len(pl.playdata) % 10 == 0:
             #   pl.savedatatofile()


    def select(self, players, count):
        '''
            When team leader must a select a team
        '''
        #if spy select a team without the other spy in it, no need for AI
        if self.spy:
            others = [p for p in players if p not in self.spies]
            return [self] + random.sample(others, count-1)

        #if I am here, means I am resistance so 
        #must try to select players that are not spies, if possible for the mission to succeed
        global bk
        ll = []
        for p in self.others():
              pp = self.teamdata[p.name]
              pl = bk.GetPlayer(p.name)
              if pl.CanMakeDecisionforAI() == True:         #are enough data to use AI ?
                  #self.log.debug("calling AI %s" % (bval))
                  if pl.IsPlayerResistanceByAI(pp):         # AI predicts if a player is resistance or not  
                    ll.append(p)                            # if is predicted as resistance add player to the team
                    if len(ll) == count -1:                 # stop when the team is completed
                        break

        if len(ll) > 0 and len(ll) == count - 1:            # return me and the predicted players 
            return [self] + ll
        #if AI did't activated in any case select random from other players
        return [self] + random.sample(self.others(), count - 1)

    def vote(self, team):
        '''
            Vote a mission, but first must do some checking
        '''
        # no matter what if tries = 5 must vote or else game over 
        if self.game.tries == 5:
            return not self.spy
        #if I am a leader select the team
        if self.game.leader == self:
            return True
         # Spies select any mission with only one spy on it.
        if self.spy:
            return len([p for p in self.game.team if p in self.spies]) == 1
        global bk
        #must check if team is resistance, since I am resistance and not me
        #If i suspect that there is a spy in a team, shoot down the mission
        for p in team:
            if p.index != self.index: 
                pp = self.teamdata[p.name]
                pl = bk.GetPlayer(p.name)
                if pl.CanMakeDecisionforAI() == False:
                    break
                if pl.IsPlayerResistanceByAI(pp) == False:
                    return False
        #finally all is OK, so mission is a go!
        return True


    def sabotage(self):
        '''
            I am a spy, so must do the best for my purpose
            Sabotage mission without possible exposing myself
        '''
        #in a team of 2 and first turn, don't sabotage (not to expose myself)
        if len(self.game.team) == 2 and self.game.turn == 1:
            return False

        #sabotage only mission with one spy in team, not to expose all spies
        spies = [s for s in self.game.team if s in self.spies]
        if len(spies) > 1:
            return False
        #finally sabotage mission, I am spy after all!
        return True


    def onMissionFailed(self, leader, team):
        '''
            When a mission has failed, time to keep some statistics
        '''
        #keep statistics for team leader
        if leader.index != self.index:
            self.teamdata[leader.name].missionsdownvoted += 1
            self.teamdata[leader.name].leader += 1
        #keep statistics for the team members
        for p in team:
            if p.index != self.index:
                self.teamdata[p.name].missionsdownvoted += 1
                self.teamdata[p.name].team += 1
        
    def onMissionComplete(self, sabotaged):
        '''
            When a mission has completed, time to keep some statistics
        '''
        #keep statistics for team leader
        if self.game.leader != self:
            self.teamdata[self.game.leader.name].missionsvoted += 1
            self.teamdata[self.game.leader.name].leader += 1
        #keep statistics for the team members
        for p in self.game.team:
            if p.index != self.index:
                self.teamdata[p.name].missionsvoted += 1
                self.teamdata[p.name].team += 1




