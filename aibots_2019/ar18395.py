'''
Agent created by Andres Rodriguez as a bot for The Resistance game
This is the first assignment for the CE811 Module: Game Artificial Intelligence
'''

import numpy
import random
import logging
import logging.handlers
from player import Bot

class ar18395(Bot):

    def onGameRevealed(self, players, spies):
        """This function will be called to list all the players, and if you're
        a spy, the spies too -- including others and yourself.
        @param players  List of all players in the game including you.
        @param spies    List of players that are spies, or an empty list.
        """
        #Data used if I'm a Spy
        self.allSpies = spies
        self.otherSpies = [x for x in spies if x.index != self.index]   #List of all spies except me
        self.resistance = [x for x in players if x not in spies]   #List of Resistance members
        #Data used if I'm Resistance
        self.players = players
        self.voteStatus = numpy.zeros(len(players), dtype=bool)   #Initialize everyone's votes in False

    def select(self, players, count):
        """Pick a sub-group of players to go on the next mission.
        @param players  The list of all players in the game to pick from.
        @param count    The number of players you must now select.
        @return list    The players selected for the upcoming mission.
        """
        #SPY
        if self.spy:
            if self.game.turn == 1:
                return random.sample(self.otherSpies, 1) + random.sample(self.resistance, count - 1)   #Let other spy sabotage first mission if he wants
            elif self.game.turn < 5:
                return random.sample(self.allSpies, 1) + random.sample(self.resistance, count - 1)   #Choose only one spy
            else:
                return [self] + random.sample(self.resistance, count - 1)   #I want to sabotage the last mission
        #RESISTANCE
        else:
            if self.game.turn == 1:
                return random.sample(players, count)   #First mission team doesn't matter
            else:
                team = []
                if self.game.turn == 5:
                    team.append(self)   #I want the last mission to succeed so I choose myself
                for i in range(0, len(self.voteStatus)):
                    if self.voteStatus[i] == True and len(team) < count and i != self.index:
                        team.append(self.players[i])   #I add the players I think are not spies to the team
                for x in players:
                    if x not in team and len(team) < count:
                        team.append(x)   #If the team is not complete, I add more players
                return team

    def onTeamSelected(self, leader, team):
        """Called immediately after the team is selected to go on a mission,
        and before the voting happens.
        @param leader   The leader in charge for this mission.
        @param team     The team that was selected by the current leader.
        """
        self.say("Mission %d team: %s" % (self.game.turn, team))
        self.leader = leader
        self.team = team

    def vote(self, team):
        """Given a selected team, decide whether the mission should proceed.
        @param team      List of players with index and name.
        @return bool     Answer Yes/No.
        """
        if self in team or self == self.game.leader:
            return True   #I want myself or my team to go on the mission
        elif self.game.turn == 1:
            return True   #I don't want to raise suspicions in the first mission
        else:
            #SPY
            if self.spy:
                if self.game.tries == 5:
                    return False   #Spies win the game if last attempt fails
                else:
                    for x in team:
                        if x.index in self.allSpies:
                            return True   #There's at least one spy who can sabotage the mission in the team
                    return False   #There are no spies so I don't want that team to go
            #RESISTANCE
            else:
                if self.game.tries == 5:
                    return True   #Spies win the game if last attempt fails
                else:
                    return bool(self.voteStatus[self.game.leader.index])   #Current status I have of the leader: True = Resistance and False = Spy


    def onVoteComplete(self, votes):
        """Callback once the whole team has voted.
        @param votes        Boolean votes for each player (ordered).
        """
        #Voting False each time will make the player status False
        #Voting False after voting True means the player believes there is a spy in the team, so his status remains True
        #Voting True after voting False means the player believes there is no spy in the team, so his status remains True
        #Voting True two times in a row is suspicious and will make the player status False
        self.voteStatus = numpy.logical_xor(self.voteStatus, votes)

    def sabotage(self):
        """Decide what to do on the mission once it has been approved.  This
        function is only called if you're a spy, otherwise you have no choice.
        @return bool        Yes to shoot down a mission.
        """
        if self.game.turn == 1:
            return False   #I never sabotage the first mission
        elif self.game.turn < 5:
            for x in self.otherSpies:
                if x in self.game.team:
                    return False   #I let other spies sabotage instead of me
            return True   #I'm the only spy in the team so I sabotage
        else:
            return True   #I always sabotage the last mission

    def onMissionComplete(self, sabotaged):
        """Callback once the players have been chosen.
        @param selected     List of players that participated in the mission.
        @param sabotaged    Integer how many times the mission was sabotaged.
        """
        self.say("Number of sabotages in mission: %d" % (sabotaged))
        if sabotaged > 0 and self.leader in self.team:
            self.voteStatus[self.leader.index] = False   #Leader probably sabotaged the mission himself

    def onGameComplete(self, win, spies):
        """Callback once the game is complete, and everything is revealed.
        @param win          Boolean true if the Resistance won.
        @param spies        List of only the spies in the game.
        """
        self.say("Resistance win: %s, Spies: %s" % (win, spies))

    def others(self):
        """Helper function to list players in the game that are not your bot."""
        return [p for p in self.game.players if p != self]

    def __init__(self, game, index, spy):
        """Constructor called before a game starts.  It's recommended you don't
        override this function and instead use onGameRevealed() to perform
        setup for your AI.
        @param name     The public name of your bot.
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
