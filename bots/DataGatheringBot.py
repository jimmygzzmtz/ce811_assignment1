import logging
import logging.handlers

import core
import random

import csv

import os

from player import Bot

class DataGatheringBot(Bot):
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
        self.trainingData = []
        self.players = players

        for i in range(0, len(players)):
            #player, voted yes sabotaged, voted no sabotaged, votes yes succeeded, voted no succeeded, votes yes failed, voted no failed, spy
            playerTemplate = [str(players[i])[2:],0,0,0,0,0,0,0]
            self.trainingData.append(playerTemplate)
        
        #print(self.trainingData)

        pass

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
        return random.sample(self.game.players, count)

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
        return random.choice([True, False])

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
        return random.choice([True, False])

    def onMissionComplete(self, sabotaged):
        """Callback once the players have been chosen.
        @param sabotaged    Integer how many times the mission was sabotaged.
        """
        for i in range(0, len(self.players)):
            if(sabotaged == True):
                if(self.game.votes[i] == True):
                    self.trainingData[i][1] += 1
                else:
                    self.trainingData[i][2] += 1
            if(sabotaged == False):
                if(self.game.votes[i] == True):
                    self.trainingData[i][3] += 1
                else:
                    self.trainingData[i][4] += 1

        pass

    def onMissionFailed(self, leader, team):
        """Callback once a vote did not reach majority, failing the mission.
        @param leader       The player responsible for selection.
        @param team         The list of players chosen for the mission.
        """
        for i in range(0, len(self.players)):
            if(self.game.votes[i] == True):
                self.trainingData[i][5] += 1
            else:
                self.trainingData[i][6] += 1
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

        for spy in spies:
            for i in range(0, len(self.players)):
                if(str(spy)[2:] == self.trainingData[i][0]):
                    self.trainingData[i][7] = 1
        
        labels = [['player','sabotagedRatio','notSabotagedRatio','failedRatio','isSpy']]

        ratioData = []

        #print(self.trainingData)

        playerList = []

        with open("playerList.csv", "a") as csvfile:
            pass

        with open('playerList.csv', 'r') as csvfile:
            if(os.stat("playerList.csv").st_size != 0):
                playerList = list(csv.reader(csvfile))[0]
            #print('read playerlist')
            #print(list(csv.reader(csvfile)))
            pass


        for i in range(0, len(self.trainingData)):
            sabotagedRatio = 0
            notSabotagedRatio = 0
            failedRatio = 0
            nameInt = 0

            name = self.trainingData[i][0]
            if(name != 'DataGatheringBot'):
                if(name not in playerList):
                    playerList.append(name)
                nameInt = playerList.index(name)

            votedYesSabotaged = self.trainingData[i][1]
            votedNoSabotaged = self.trainingData[i][2]
            sabotagedTotal = votedYesSabotaged + votedNoSabotaged
            if(sabotagedTotal != 0):
                sabotagedRatio = (votedYesSabotaged / (sabotagedTotal))

            votedYesNotSabotaged = self.trainingData[i][3]
            votedNoNotSabotaged = self.trainingData[i][4]
            notSabotagedTotal = votedYesNotSabotaged + votedNoNotSabotaged
            if(notSabotagedTotal != 0):
                notSabotagedRatio = (votedYesNotSabotaged / (notSabotagedTotal))

            votedYesFailed = self.trainingData[i][5]
            votedNoFailed = self.trainingData[i][6]
            failedTotal = votedYesFailed + votedNoFailed
            if(failedTotal != 0):
                failedRatio = (votedYesFailed / (failedTotal))

            isSpy = self.trainingData[i][7]

            ratioPlayer = [nameInt,sabotagedRatio,notSabotagedRatio,failedRatio,isSpy]
            
            if(name != 'DataGatheringBot'):
                ratioData.append(ratioPlayer)

        with open("dataGatheringOutput.csv", "a", newline="") as f:
            if(os.stat("dataGatheringOutput.csv").st_size == 0):
                writableList = labels + ratioData
            else:   
                writableList = ratioData
            writer = csv.writer(f)
            writer.writerows(writableList)
        
        #print(playerList)
        with open("playerList.csv", "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(playerList)

        pass

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