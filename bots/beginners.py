# All of the example bots in this file derive from the base Bot class.  See
# how this is implemented by looking at player.py.  The API is very well
# documented there.
from player import Bot 

# Each bot has access to the game state, stored in the self.game member
# variable.  See the State class in game.py for the full list of variables you
# have access to from your bot.
# 
# The examples below purposefully use only self.game to emphasize its
# importance.  Advanced bots tend to only use the game State class to decide!
from game import State


# Many bots will use random decisions to break ties between two equally valid
# options.  The simple bots below rely on randomness heavily, and expert bots
# tend to use other statistics and criteria (e.g. who is winning) to avoid ties
# altogether!
import random

class JimmyBot(Bot):
    """Version 0.0.2"""

    suspicionsArr = []
    players = []

    def onGameRevealed(self, players, spies):
        #2 spies for 5 players, empty = not a spy
        self.players = players
        self.spies = spies
        #self.suspicionsArr = [0,0,0,0,0]

        #id, susp
        self.suspicionsBlackboard = [[0,0],[1,0],[2,0],[3,0],[4,0]]

    def select(self, players, count):
        #id, susp

        memberSpy = -1
        memberRes1 = -1
        memberRes2 = -1

        if(self.spy):
            #find spy with the least suspicion, save id and suspicion value
            #find resistance member with the most suspicion (to throw the blame), save id and suspicion value

            for i in range(0, len(players)):
                if(players[self.suspicionsBlackboard[i][0]] in self.spies):
                    memberSpy = self.suspicionsBlackboard[i][0]
                    break
            
            for i in range(len(players) - 1, -1, -1):
                if(players[self.suspicionsBlackboard[i][0]] not in self.spies):
                    memberRes1 = self.suspicionsBlackboard[i][0]
                    break
            
            for i in range(len(players) - 1, -1, -1):
                if(players[self.suspicionsBlackboard[i][0]] not in self.spies and memberRes1 != self.suspicionsBlackboard[i][0]):
                    memberRes2 = self.suspicionsBlackboard[i][0]
                    break
                
            #return appropiate amount of teammates
            spyList = []
            if(count == 2):
                spyList = [players[memberSpy],players[memberRes1]]
            if(count == 3):
                spyList = [players[memberSpy],players[memberRes1],players[memberRes2]]
            
            """ duplicate debugging
            print(spyList)

            if(any(spyList.count(x) > 1 for x in spyList)):
                print(self.spies)
                print(self.suspicionsBlackboard)
                print(spyList)
                print(memberSpy)
            
            """
            return spyList
        
        else:
            return [self] + random.sample(self.others(), count - 1)

    def vote(self, team):
        #always vote yes on the first turn
        if(self.game.turn == 1 and self.game.tries == 1):
            return True

        if self.game.tries == 5:
            return not self.spy

        #if there is a spy in the team, vote yes
        if(self.spy):
            for i in range(0, len(team)):
                if(team[i] in self.spies):
                    return True
            return False
        else:
            #if a team member is in top 3 o 2 (count) of spies, vote no
            pass
        return bool(self == self.game.leader)

    def sabotage(self):
        return True 
    
    def onMissionComplete(self, sabotaged):
        #there are spies on the mission
        if(sabotaged != 0):
            for i in range(0, len(self.game.team)):
                self.suspicionsBlackboard[self.players.index(self.game.team[i])][1] += 1
            self.suspicionsBlackboard[self.players.index(self.game.leader)][1] += 1
        
        self.suspicionsBlackboard = sorted(self.suspicionsBlackboard, key=lambda player: player[1])
    
            
class Paranoid(Bot):
    """An AI bot that tends to vote everything down!"""

    def select(self, players, count):
        self.say("Picking myself and others I don't trust.")
        return [self] + random.sample(self.others(), count - 1)

    def vote(self, team): 
        self.say("I only vote for my own missions.")
        return bool(self == self.game.leader)

    def sabotage(self):
        self.log.debug("I always sabotage when I'm a spy.")
        return True 


class Hippie(Bot):
    """An AI bot that's OK with everything!"""

    def select(self, players, count):
        self.say("Picking some cool dudes to go with me!")
        return [self] + random.sample(self.others(), count - 1)

    def vote(self, team): 
        self.say("Everything is OK with me, man.")
        return True

    def sabotage(self):
        self.log.debug("Sabotaging is what spy dudes do, right?")
        return True


class RandomBot(Bot):
    """An AI bot that's perhaps never played before and doesn't understand the
    rules very well!"""

    def select(self, players, count):
        self.say("A completely random selection.")
        return random.sample(self.game.players, count)

    def vote(self, team): 
        self.say("A completely random vote.")
        return random.choice([True, False])

    def sabotage(self):
        self.log.debug("A completely random sabotage.")
        return random.choice([True, False])

    def announce(self):
        subset = random.sample(self.others(), random.randint(0, len(self.others())))
        return {p: random.random() for p in subset}


class Neighbor(Bot):
    """An AI that picks and votes for its neighbours and specifically does not
    use randomness in its decision-making."""

    @property
    def neighbors(self):
        n = self.game.players[self.index:] + self.game.players[0:self.index]
        return n

    def select(self, players, count):
        return self.neighbors[0:count]

    def vote(self, team):
        if self.game.tries == 5:
            return not self.spy
        n = self.neighbors[0:len(team)] + [self]
        for p in team:
            if not p in n: return False
        return True

    def sabotage(self):
        return len(self.game.team) == 2 or self.game.turn > 3


class Deceiver(Bot):
    """A tricky bot that's good at pretending being resistance as a spy."""

    def onGameRevealed(self, players, spies):
        self.spies = spies

    def select(self, players, count):
        return [self] + random.sample(self.others(), count - 1)

    def vote(self, team): 
        # Since a resistance would vote up the last mission...
        if self.game.tries == 5:
            return True
        # Spies select any mission with only one spy on it.
        if self.spy and len(self.game.team) == 2:
            return len([p for p in self.game.team if p in self.spies]) == 1
        # If I'm not on the team, and it's a team of 3...
        if len(self.game.team) == 3 and not self in self.game.team: 
            return False
        return True

    def sabotage(self):
        # Shoot down only missions with more than another person.
        return len(self.game.team) > 2


class RuleFollower(Bot):
    """Rule-based AI that does a pretty good job of capturing
    common sense play rules for THE RESISTANCE."""

    def onGameRevealed(self, players, spies):
        self.spies = spies

    def select(self, players, count):
        return [self] + random.sample(self.others(), count - 1)

    def vote(self, team): 
        # Both types of factions have constant behavior on the last try.
        if self.game.tries == 5:
            return not self.spy
        # Spies select any mission with one or more spies on it.
        if self.spy:
            return len([p for p in self.game.team if p in self.spies]) > 0
        # If I'm not on the team, and it's a team of 3...
        if len(self.game.team) == 3 and not self in self.game.team:
            return False
        return True

    def sabotage(self):
        return True


class Jammer(Bot):
    """An AI bot that plays simply as Resistance, but as a Spy plays against
    the common wisdom for synchronizing sabotages."""

    def onGameRevealed(self, players, spies):
        self.spies = spies

    def select(self, players, count):
        if not self.spies:
            return random.sample(self.game.players, count)
        else:
            # Purposefully go out of our way to pick the other spy so that we
            # can trick him with deceptive sabotaging!
            self.log.info("Picking the other spy to trick them!")    
            return list(self.spies) + random.sample(set(self.game.players) - set(self.spies), count-2)

    def vote(self, team): 
        return True

    def sabotage(self):
        spies = [s for s in self.game.team if s in self.spies]
        if len(spies) > 1:
            # Intermediate to advanced bots assume that sabotage is "controlled"
            # by the mission leader, so we go against this practice here.
            if self == self.game.leader:
                self.log.info("Not coordinating not sabotaging because I'm leader.")
                return False 

            # This is the opposite of the same practice, sabotage if the other
            # bot is expecting "control" the sabotage.
            if self.game.leader in spies:
                self.log.info("Not coordinating and sabotaging despite the other spy being leader.")
                return True
            spies.remove(self)

            # Often, intermeditae bots synchronize based on their global index
            # number.  Here we go against the standard pracitce and do it the
            # other way around!
            self.log.info("Coordinating according to the position around the table...")
            return self.index > spies[0].index
        return True




