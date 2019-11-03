import logging
import logging.handlers

import core

from player import Bot

class JimmyBot(Bot):
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

    """Version 0.0.6"""

    players = []
    leaderSusp = 3
    teamMemberSusp = 2
    votedYesSusp = 1


    def onGameRevealed(self, players, spies):
        """This function will be called to list all the players, and if you're
        a spy, the spies too -- including others and yourself.
        @param players  List of all players in the game including you.
        @param spies    List of players that are spies, or an empty list.
        """
        #2 spies for 5 players, empty = not a spy
        self.players = players
        self.spies = spies
        #self.suspicionsArr = [0,0,0,0,0]

        #id, susp
        self.suspicionsBlackboard = [[0,0],[1,0],[2,0],[3,0],[4,0]]
        self.suspicionsBlackboardSort = [[0,0],[1,0],[2,0],[3,0],[4,0]]

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

        if(self.spy):
            #find resistance member with the most suspicion (to throw the blame), save id and suspicion value
            memberRes1 = -1
            memberRes2 = -1

            for i in range(len(players) - 1, -1, -1):
                if(players[self.suspicionsBlackboardSort[i][0]] not in self.spies):
                    memberRes1 = self.suspicionsBlackboardSort[i][0]
                    break
            
            for i in range(len(players) - 1, -1, -1):
                if(players[self.suspicionsBlackboardSort[i][0]] not in self.spies and memberRes1 != self.suspicionsBlackboardSort[i][0]):
                    memberRes2 = self.suspicionsBlackboardSort[i][0]
                    break

            if(count == 2):
                teamList = [self,players[memberRes1]]
            if(count == 3):
                teamList = [self,players[memberRes1],players[memberRes2]]
            
            """ duplicate debugging
            print(spyList)

            if(any(spyList.count(x) > 1 for x in spyList)):
                print(self.spies)
                print(self.suspicionsBlackboard)
                print(spyList)
                print(memberSpy)
            
            """

            return teamList
        
        else:
            #include players with least suspicion

            memberRes1 = -1
            memberRes2 = -1

            for i in range(0, len(players)):
                if(players[self.suspicionsBlackboardSort[i][0]] != self):
                    memberRes1 = self.suspicionsBlackboardSort[i][0]
                    break
            
            for i in range(0, len(players)):
                if(players[self.suspicionsBlackboardSort[i][0]] != self and memberRes1 != self.suspicionsBlackboardSort[i][0]):
                    memberRes2 = self.suspicionsBlackboardSort[i][0]
                    break

            if(count == 2):
                teamList = [self,players[memberRes1]]
            if(count == 3):
                teamList = [self,players[memberRes1],players[memberRes2]]

            #print(teamList)
            return teamList

            #return [self] + random.sample(self.others(), count - 1)

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
            #if a team member is in top 3 or 2 of suspicions, and is bigger than 0, vote no
            for i in range(0, len(team)):
                if(team[i] in self.suspicionsBlackboardSort[((len(self.players)) - (len(team))):((len(self.players)) - 1)] and self.suspicionsBlackboard[i][1] != 0):
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
        
        #print(self.game.votes)

        #there are spies on the mission
        if(sabotaged != 0):
            for i in range(0, len(self.game.team)):
                self.suspicionsBlackboard[self.players.index(self.game.team[i])][1] += self.teamMemberSusp
            self.suspicionsBlackboard[self.players.index(self.game.leader)][1] += self.leaderSusp

            for i in range(0, len(self.game.votes)):
                if(self.game.votes[i] == True):
                    self.suspicionsBlackboard[i][1] += self.votedYesSusp
            
        self.suspicionsBlackboardSort = sorted(self.suspicionsBlackboard, key=lambda player: player[1])

    def onMissionFailed(self, leader, team):
        """Callback once a vote did not reach majority, failing the mission.
        @param leader       The player responsible for selection.
        @param team         The list of players chosen for the mission.
        """
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