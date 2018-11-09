from player import Bot
from player import Player
from game import State

import itertools
from itertools import product
from itertools import chain

from operator import itemgetter
from dataclasses import dataclass
import random


# A lot of the code that has been used to debug this code has been commented out due to the amount of
# space taken up by each game in the log file for this bot. It can be uncommented but there shouldn't
# be any need to uncomment them as all functionality seems to be working as intended.

@dataclass
class GameData(object):
    _players = {}
    safe_players = {}
    spy_chance = {}
    votes = {}

    l_safe_players = []
    l_unsafe_players = []
    resistance = []

    last_team = {}
    team_selection = []
    sabotage_count = 0

    spy_threshold = 0

class rj18801(Bot):

    gameData = GameData()

    

    def onGameRevealed(self, players, spies):
        """This function will be called to list all the players, and if you're
        a spy, the spies too -- including others and yourself.
        @param players  List of all players in the game including you.
        @param spies    List of players that are spies, or an empty list.
        """
        self.log.debug(
            "============================Let's Play!============================")
        
        self.players = players
        self.spies = spies          
        
        self.gameData.spy_threshold = 0.2
        
        self.gameData._players = self.players
        self.gameData.unsafe_players = self.gameData._players.copy()
        self.gameData.spy_chance = self.gameData._players.copy()
        self.gameData.votes = self.gameData._players.copy()
        
        key = 0
        while key < len(self.gameData._players):
            self.gameData.unsafe_players[key] = False#fuzzy, chance a player marked as dangerous might be safe.
            self.gameData.spy_chance[key] = 0.0
            self.gameData.votes[key] = False
            #self.log.debug("key: %s , Name: %s, Dangerous: %s, Spy Chance: %s, Vote: %s" % (key, self.gameData._players[key], self.gameData.unsafe_players[key], self.gameData.spy_chance[key], self.gameData.votes[key]))
            key += 1

        if self.spy:
            for i in range(0, len(self.players)):
                if self.players[i] not in self.spies:
                    self.gameData.resistance.append(self.game.players[i])   
            #self.log.debug("Spies are: %s" % self.spies)  
            #self.log.debug("Resistance is: %s" % self.gameData.resistance)                        
        
        if self.spy:
            self.log.debug("I am a Spy!")

        if not self.spy:
            self.log.debug("I am a Resistance!")

    def onMissionAttempt(self, mission, tries, leader):
        """Callback function when a new turn begins, before the
        players are selected.
        @param mission  Integer representing the mission number (1..5).
        @param tries    Integer count for its number of tries (1..5).
        @param leader   A Player representing who's in charge.+
        """
        self.log.debug("Mission number: %s," % mission)
        self.log.debug("it's been tried %s times." % tries)
    
    # We pick the players we believe to be safe, once we have exhuasted those
    # we pick the first person that isn't in the team already. We don't care if they
    # are a spy or not as we have to pick someone.
    def select(self, players, count):
        """Pick a sub-group of players to go on the next mission.
        @param players  The list of all players in the game to pick from.
        @param count    The number of players you must now select.
        @return list    The players selected for the upcoming mission.
        """
        self.gameData.team_selection.clear()
        self.gameData.safe_players.clear()

        if not self.spy:
            if self.game.turn > 1:
                t = 0
                for t in range(len(self.players)):
                    if self.gameData.spy_chance[t] < self.gameData.spy_threshold:
                        if not players[t] in self.gameData.l_safe_players:
                            self.gameData.l_safe_players.append(self.players[t])
                    t += 1
                self.log.debug("I think safe players are: %s" % self.gameData.l_safe_players)

                _sizeofSafePlayers = len(self.gameData.l_safe_players)
                self.log.debug("are %s safe players" % _sizeofSafePlayers)
                
                tm = 0
                for tm in range(0, len(self.gameData.l_safe_players)):
                    self.gameData.team_selection.append(self.gameData.l_safe_players[tm])
                    tm += 1

                if len(self.gameData.team_selection) < count:
                    self.log.debug("We need more for this team.")
                    x = 0
                    while len(self.gameData.team_selection) < count:
                        if count > len(self.gameData.team_selection):
                            _p = self.players[x]
                            self.log.debug("logging _p %s" % _p)
                            if not _p in self.gameData.team_selection:
                                self.log.debug("Adding %s to team" % _p)
                                self.gameData.team_selection.append(_p)
                        x += 1
                
                self.log.debug("Count is %s" % count)
                while len(self.gameData.team_selection) > count:
                    del self.gameData.team_selection[-1]
                    
                self.log.debug("Team Selected %s" % self.gameData.team_selection)

        self.gameData.safe_players.clear()

        #Two Players    
        # Isn't much choice here. We have no information at this point in the game except
        # that about ourself. Might as well pick self and randomly fill the other slot.
        if self.game.turn == 1:
            if self.spy:
                 return [self] + random.sample(self.others(), count - 1)#this line is from the paranoid bot, unsure of who has written it.
            if not self.spy:
                return [self] + random.sample(self.others(), count - 1)#this line is from the paranoid bot, unsure of who has written it.
        
        #Three Players
        #We have a little more information now. Let's try and make an informed(?) choice.
        if self.game.turn == 2:
            if self.spy:
                return [self] + random.sample(self.others(), count - 1)
            if not self.spy:
                return self.gameData.team_selection
   

        #Two Players
        if self.game.turn == 3:
            if self.spy:
                return [self] + random.sample(self.others(), count - 1)
            if not self.spy:
                return self.gameData.team_selection

        #Three Players
        if self.game.turn == 4:
            if self.spy:
                return  [self] + random.sample(self.others(), count - 1)
            if not self.spy: 
                return self.gameData.team_selection
        
        #Three Players
        if self.game.turn == 5:
            if self.spy:
                return [self] + random.sample(self.others(), count - 1)
            if not self.spy: 
                return self.gameData.team_selection

    def onTeamSelected(self, leader, team):
        """Called immediately after the team is selected to go on a mission,
        and before the voting happens.
        @param leader   The leader in charge for this mission.
        @param team     The team that was selected by the current leader.
        """
        pass
        # self.log.debug(team)
        # self.log.debug(leader)

    def vote(self, team):
        """Given a selected team, decide whether the mission should proceed.
        @param team      List of players with index and name.
        @return bool     Answer Yes/No.
        """
        # we have no information on the first one really, best just to support. Unlikely spy will sabotage here anyway.
        if self.game.turn == 1:
            return True
        # there are two paths we need to take here. Resistance and spies will vote differently.
        if self.spy:
            # I should support my missions and other spy selections
            if self.game.leader in self.spies:
                self.log.debug("Leader is a spy, I support this mission")
                return True
            if self.game.tries == 4:
                return False
            if self.game.turn == 1:
                return True
            if self.game.turn is 2 or 3 or 4 or 5 and self.spies not in self.game.team:
                return False
            else: return False

        
        if not self.spy:
            self.gameData.l_unsafe_players.clear()        
            
            t = 0
            for t in range(len(self.players)):
                if self.gameData.spy_chance[t] > self.gameData.spy_threshold:
                    self.gameData.l_unsafe_players.append(self.players[t])
                t += 1

            # I should always vote for my own selection.
            if self == self.game.leader:
                self.log.debug("I always vote for my own missions")
                return True
            # if we are on 4 attampts at this mission we need to approve it as 5 is default spy win.
            if self.game.tries == 4:
                return True

            #if there are unsafe people in the team we don't want to go on the mission
            r = 0
            for r in range(0,len(self.players)):
                _p = self.players[r]
                if _p in self.game.team:
                    if not _p in self.gameData.l_unsafe_players:
                        self.log.debug("Unsafe players")
                        return False
                r += 1

            else: return True

    def onVoteComplete(self, votes):
        """Callback once the whole team has voted.
        @param votes        Boolean votes for each player (ordered).
        """
        #self.log.debug(self.players)
        #self.log.debug(votes)

    def sabotage(self):
        """Decide what to do on the mission once it has been approved.  This
        function is only called if you're a spy, otherwise you have no choice.
        @return bool        Yes to shoot down a mission.
        """
        if self.spy:
            if self.game.turn == 1:
                # self.log.debug("Round %s" % (self.game.turn))
                # self.log.debug("Don't want to give my self away this early")
                return False
            elif self.game.turn == 3 and self.game.losses < 2:
                # self.log.debug("Round %s" % (self.game.turn))
                # self.log.debug("Not sabotaging as we haven't won the two previous rounds.")
                return False
            elif self.game.turn == 3 and self.game.losses == 2:
                # self.log.debug("Round %s" % (self.game.turn))
                # self.log.debug("Sabotaging as we have won the two previous rounds.")
                return True
            else:
                return True
        else: return False

    def onMissionComplete(self, sabotaged):
        """Callback once the players have been chosen.
        @param sabotaged    Integer how many times the mission was sabotaged.
        """
        # clear list of last team before refilling it
        self.gameData.last_team.clear()
        self.gameData.last_team = self.game.team
        #self.log.debug("last team was: %s" % self.gameData.last_team)
        #self.log.debug("Sabotaged %s times" % sabotaged)
        #self.gameData.sabotage_count = sabotaged
       

        #this lot should probably go into  methods by itself onSabotaged() and onNotSabotaged()
        if sabotaged > 0:
            #for t in range(0, len(self.game.team)):
            for t in range(0, len(self.players)):
                # Anyone voting for a mission that was Sabotaged
                # has a higher chance of being a spy. Using a dictionary
                # that follows the same order as _players we can store a spy_chance
                # in the same key as in _players
                if self.game.votes[t] == True: 
                    #_p = Player(self.game.team[t].name, self.game.team[t].index) 
                    _p = Player(self.gameData._players[t], self.game.players[t].index)

                    if self.gameData.spy_chance[t] < float(1.0):
                        self.gameData.spy_chance[_p.index] += float(0.4)
                        if self.gameData.spy_chance[t] >float(1.0):
                            self.gameData.spy_chance[_p.index] = float(1.0)
                    #self.log.debug("Player Index %s: increasing spy chance" % _p.index)

                # If a mission is sabotaged, anyone that voted to reject the mission
                # has less chance of being a spy.
                if self.game.votes[t] == False: #less chance of being a spy
                    _p = Player(self.gameData._players[t], self.game.players[t].index)

                    if self.gameData.spy_chance[t] > float(0):
                        self.gameData.spy_chance[_p.index] -= float(0.2)
                        if self.gameData.spy_chance[t] < float(0):
                            self.gameData.spy_chance[t] = float(0)
                        #self.log.debug("Player Index %s: decreasing spychance spy chance" % _p.index)
                t += 1
        
        # if the mission isn't sabotaged the people that supported it probably
        # aren't spies. In addition the people on the team probably aren't spies either.
        # Unless it's round 1 or 3. But we aren't distinguishing that here. 
        if sabotaged == 0:
           for t in range(0, len(self.players)):

                # voting to go on a mission that then isn't sabotaged, probably not a spy
                if self.game.votes[t] == True: 
                    _p = Player(self.gameData._players[t], self.game.players[t].index)

                    if self.gameData.spy_chance[t] > 0:
                        self.gameData.spy_chance[_p.index] -= float(0.2)
                        if self.gameData.spy_chance[t] <0:
                            self.gameData.spy_chance[_p.index] = float(0)
                        #self.log.debug("Player Index %s: decreasing spy chance" % _p.index)

                #Trying to reject a mission that wasn't sabotaged, probably a spy
                if self.game.votes[t] == False:
                    _p = Player(self.gameData._players[t], self.game.players[t].index)

                    if self.gameData.spy_chance[t] < 1:
                        self.gameData.spy_chance[_p.index] += float(0.4)
                        if self.gameData.spy_chance[t] > 1:
                            self.gameData.spy_chance[_p.index] = float(1.0)
                        #self.log.debug("Player Index %s: increasing spychance spy chance" % _p.index)
                t += 1
            
        if self.gameData.spy_chance[self.index] > 0:
            #self.log.debug("I am not a spy silly, although I might be. I don't actually know")
            self.gameData.spy_chance[self.index] = 0


        # self.log.debug(self.gameData._players)
        # self.log.debug(self.gameData.spy_chance)


    def onMissionFailed(self, leader, team):
        """Callback once a vote did not reach majority, failing the mission.
        @param leader       The player responsible for selection.
        @param team         The list of players chosen for the mission.
        """
        # clear list of last team before refilling it
        self.gameData.last_team.clear()
        self.gameData.last_team = self.game.team
        #self.log.debug("last team was: %s" % self.gameData.last_team)

        # self.log.debug("Team shot down!")

    def announce(self):
        """Publicly state beliefs about the game's state by announcing spy
        probabilities for any combination of players in the game.  This is
        done after each mission completes, and takes the form of a mapping from
        player to float.  Not all players must be specified, and of course this
        can be innacurate!

        @return dict[Player, float]     Mapping of player to spy probability.
        """
        pass
    
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
        #self.log.debug(spies)

        self.gameData.last_team.clear()
        self.gameData._players.clear()
        self.gameData.l_unsafe_players.clear()
        self.gameData.safe_players.clear()
        self.gameData.l_safe_players.clear()
        self.gameData.spy_chance.clear()
        self.gameData.votes.clear()
        self.gameData.resistance.clear()
        self.gameData.team_selection.clear()

        if win:
            self.log.debug("Resistance Won")
        if not win:
            self.log.debug("Spies won")

    def others(self):
        """Helper function to list players in the game that are not your bot."""
        return [p for p in self.game.players if p != self]
