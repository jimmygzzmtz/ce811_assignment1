from player import Bot
import random

class Jm17913(Bot):
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

    #__metaclass__ = core.Observable
    spys = []
    notspys = []
    spycutof = None


    def onGameRevealed(self, players, spies):
        """This function will be called to list all the players, and if you're
        a spy, the spies too -- including others and yourself.
        @param players  List of all players in the game including you.
        @param spies    List of players that are spies, or an empty list.
        """
        self.spypercent = []                                             # list of players with their chance of being a spy
        global spys                                                     # list of spies if bot is a spy else it's empty
        global notspys                                                  # list of not spies if not is a spy else it's empty
        global spycutof                                                 # the cutoff that the bot thinks players are spies

        spys = []
        notspys = []
        indx = -1
        spycutof = 0.2
        for each in players:
            indx += 1
            if each == self:
                self.index = indx
            if each not in spies:
                self.spypercent.append([indx, each, 0])                      # add to spypercent [index, player, chance]
            else:
                self.spypercent.append([indx, each, 1])
        if self.spy:
            for each in spies:
                spys.append(each)                                       # add spy to list

            for each in players:
                if each not in spys:
                    if each != self:
                        notspys.append(each)                            # add not spy to list
        return True

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
        global notspys

        onteam = []                                                     # holds who will be on team

        if self.game.turn == 1:                                         # if it's the first turn
            onteam.append(self.game.leader)                             # adds self to team
            if not self.spy:
                for each in random.sample(self.others(), count - 1):    # if bot not spy adds random others to team
                    onteam.append(each)
            else:
                tempindex = -1
                for i in range(1, count):                               # will find 1 or 2 other players
                    steamindex = random.randint(0, len(notspys)-1)
                    while steamindex == tempindex:                      # stops returning duplicates
                        steamindex = random.randint(0, len(notspys)-1)
                    onteam.append(notspys[steamindex])                  # if bot is spy adds random not spies to team
                    tempindex = steamindex
        else:
             onteam = (self.getLowSpyChanceForTeam(count, self.spypercent))  # adds bots that have lowest chance of being a spy
        return onteam

    def getLowSpyChanceForTeam(self, count, spypercen, spies = None):
        tempspypercent = spypercen                                      # sets temp list of spy chance
        inteam = []
        inteam.append(self.game.leader)                                 # adds self to team
        tempspypercent[self.index][2] += 100                            # sets self temp spychance much higher
        for each in range(1, count):                                    # finds 1 or 2 other players for team
            spyperloc = self.getMinLoc(tempspypercent)                  # gets index of min spychance
            name = tempspypercent[spyperloc][1]                         # gets name of lowest spychance
            while name in inteam:                                       # checks for duplicate
                spyperloc = self.getMinLoc(tempspypercent)
                name = tempspypercent[spyperloc][1]
                tempspypercent[spyperloc][2] += 100                     # sets temp spychance much higher
            inteam.append(name)                                         # adds lowest spychance to team
            tempspypercent[spyperloc][2] += 100
        return inteam

    def getMinLoc(self, tempspypercent):                                # gets the index of player with the lowest spychance, random if tie
        minlocations = []
        minloc = 0
        for i in range(0, 4):
            if tempspypercent[i][2] < tempspypercent[minloc][2]:
                minloc = i
        minlocations.append(minloc)                                     # finds index of min spychance
        for i in range(0, 4):
            if tempspypercent[i][2] == tempspypercent[minloc][2]:       # finds all lowest spychance
                if minloc != i:
                    minlocations.append(i)
        randomloc = random.randint(0, len(minlocations)-1)              # chooses random player with lowest spychance
        spyperloc = minlocations[randomloc]
        return spyperloc

    def getSpyChanceOfTeam(self, team):                                 # returns total chance that is a spy on the team
        totalspychance = 0
        for each in team:
            totalspychance += self.spypercent[each.index][2]
        return totalspychance

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
        global spycutof
        if self.game.leader:                                            # if bot is the leader
            return True
        elif self.spy:                                                  # spy votes
            if self.game.tries == 5:                                    # if its the last try
                return True
            elif self.game.turn == 1:                                   # if its the 1st turn
                return True
            elif self.getSpyChanceOfTeam(team) > spycutof:              # if think there is a spy on team
                return False
            elif self.IsSpyInTeam(team):                                # if there is actually a spy on team
                return True
            else:
                return False
        else:                                                           # not spy votes
            if self.game.tries == 5:                                    # if its last try
                return True
            elif self.game.turn == 1:                                   # if its turn 1
                return True
            elif self.getSpyChanceOfTeam(team) < spycutof:              # if low chance of spy
                return True
            else:
                return False
        return True

    def IsSpyInTeam(self, team):                                        # returns if a spy is in a team
        spys = self.spys
        for each in spys:
            if each in team:
                return True
        return False

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
        for each in self.spys:
            if each in self.game.team:
                return False
        for each in self.game.team:
            if self.spypercent[each.index] >= self.spypercent[self.index]:
                return True



        return False                                                     # votes true on turn 1 as winning a turn is more important than being found out for small player sets


    def onMissionComplete(self, sabotaged):
        """Callback once the players have been chosen.
        @param selected     List of players that participated in the mission.
        @param sabotaged    Integer how many times the mission was sabotaged.
        """


        if sabotaged >= 1:                                              # if there is 1 or more sabatages
            if (self in self.game.team) & (not self.spy):               # if the bot is in team and if bot not spy
                for each in self.game.team:
                    addperc = sabotaged/(len(self.game.team)-1)         # for each in team add percentage chance of being a spy
                    if addperc == 1:                                    # if the other is definitely a spy
                        addperc *= 10000                                # make spypercent big
                        self.spypercent[each.index][2] += addperc                # add chance
            else:
                for each in self.game.team:                             # if spy or not in team
                    addperc = (sabotaged / len(self.game.team))         # add equal chance for each in team
                    self.spypercent[each.index][2] += addperc
        else:
            for each in self.game.team:                                 # if no sabotages
                addperc = -(100/len(self.game.team))                      # removes spychance of players
                self.spypercent[each.index][2] += addperc
        return True

    def onMissionFailed(self, leader, team):
        """Callback once a vote did not reach majority, failing the mission.
        @param leader       The player responsible for selection.
        @param team         The list of players chosen for the mission.
        """
        global spycutof
        if self.getSpyChanceOfTeam(team) <= spycutof:                   # if high chance of a spy on the team
            for each in self.game.players:
                if not self.game.votes[each.index]:
                    self.spypercent[each.index][2] += 1                      # if vote fail then prob not spy so lower chance
                else:
                    self.spypercent[each.index][2] -= 1                      # if vote go then prob a spy so raise chance
        return True

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
        @param name     The public name of your bot.
        @param index    Your own index in the player list.
        @param spy      Are you supposed to play as a spy?
        """
        super(Bot, self).__init__(self.__class__.__name__, index)

        self.game = game
        self.spy = spy

    def __repr__(self):
        """Built-in function to support pretty-printing."""
        type = {True: "SPY", False: "RST"}
        return "<%s #%i %s>" % (self.name, self.index, type[self.spy])
