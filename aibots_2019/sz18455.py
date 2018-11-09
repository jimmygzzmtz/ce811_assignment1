import logging
import logging.handlers
import random

from player import Bot


class SuBot(Bot):
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

    def onGameRevealed(self, players, spies):
        """This function will be called to list all the players, and if you're
        a spy, the spies too -- including others and yourself.
        @param players  List of all players in the game including you.
        @param spies    List of players that are spies, or an empty list.
        """
        self.spies = spies
        # Calculate suspect level
        self.Suspectlist=[0 ,0 ,0 ,0 ,0 ]


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
        # If I am spy, select players with me who are not spies
        if self.spy:
            others = [p for p in players if p not in self.spies]
            return [self] + random.sample(others, count-1)
        # team of mission
        t = []
        # store value of suspect level temporarily
        temp = [0, 0, 0, 0, 0]
        # select the smallest suspect level players
        for i in range(0, count):
            t.append(players[self.Suspectlist.index(min(self.Suspectlist))])
            temp[self.Suspectlist.index(min(self.Suspectlist))] = min(self.Suspectlist)
            self.Suspectlist[self.Suspectlist.index(min(self.Suspectlist))] = 9999
        for j in range(0, 5):
            if self.Suspectlist[j] == 9999:
                self.Suspectlist[j] = temp[j]
        return t

    def onTeamSelected(self, leader, team):
        """Called immediately after the team is selected to go on a mission,
        and before the voting happens.
        @param leader   The leader in charge for this mission.
        @param team     The team that was selected by the current leader.
        """
        self.say("You selected %s for mission %d"%(team,self.game.turn))

    def vote(self, team):
        """Given a selected team, decide whether the mission should proceed.
        @param team      List of players with index and name. 
        @return bool     Answer Yes/No.
        """
        # If it is the 5th try
        if self.game.tries == 5:
            return True
        # If I am spy, vote every mission with spy
        if self.spy:
            return len([p for p in team if p in self.spies]) > 0
        # Same as selection, I vote the lowest suspect level
        t = []
        # store value of suspect level temporarily
        temp = [0, 0, 0, 0, 0]
        # select the smallest suspect level players
        for i in range(0, len(team)):
            t.append(self.game.players[self.Suspectlist.index(min(self.Suspectlist))])
            temp[self.Suspectlist.index(min(self.Suspectlist))] = min(self.Suspectlist)
            self.Suspectlist[self.Suspectlist.index(min(self.Suspectlist))] = 9999
        for j in range(0, 5):
            if self.Suspectlist[j] == 9999:
                self.Suspectlist[j] = temp[j]
        return len([p for p in self.game.team if p in t]) == len(team)



    def onVoteComplete(self, votes):
        """Callback once the whole team has voted.
        @param votes        Boolean votes for each player (ordered).
        """
        # Increase suspect level who do not select as me
        if votes[self.index]:
            for player in self.game.players:
                if not votes[player.index]:
                    self.Suspectlist[player.index] += 1
        else:
            for player in self.game.players:
                if votes[player.index]:
                    self.Suspectlist[player.index] += 1
        self.say("My Suspectlist %s" % (self.Suspectlist, ))



    def sabotage(self):
        """Decide what to do on the mission once it has been approved.  This
        function is only called if you're a spy, otherwise you have no choice.
        @return bool        Yes to shoot down a mission.
        """
        # We are close to win !
        #if self.game.losses == 2:
            #return True
        # Shoot down only missions with more than another person.
        #return len(self.game.team) > 2
        return True

    def onMissionComplete(self, sabotaged):
        """Callback once the players have been chosen.
        @param sabotaged    Integer how many times the mission was sabotaged.
        """
        self.say("Mission was sabotaged %d times" % (sabotaged, ) )
        # If mission failed, everyone in mission team increase suspect level
        if sabotaged > 0:
            for player in self.game.team:
                self.Suspectlist[player.index] += 1
            if sabotaged == len(self.game.team): # The players in team definitely all are spies
                for i in range(0, len(self.game.team)):
                    self.Suspectlist[self.game.team[i].index] = 8888
        # If no sabotage happened, trust them more
        if sabotaged == 0:
            for player in self.game.team:
                self.Suspectlist[player.index] -= 1
        self.Suspectlist[self.index] = 0
        self.say("My Suspectlist %s" % (self.Suspectlist, ))


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
        self.say("Game is over, win: %s, %s were spies" % (win, spies))

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

