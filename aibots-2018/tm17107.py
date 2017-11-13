from player import Bot
from game import State
import random

class Tm17107(Bot):
    def onGameRevealed(self,players,spies):

        self.spies = spies
        self.Storage = []
        self.safeteam =[]
        self.defspy = []
        self.playervotes =[]


        # p[0] is equal to player, p[1] is equal to player faction, p[2] equals  number of player's up votes
        # p[3] is equal to number of down votes, p[4] is equal to number failed missions player embarked on
        # p[5] is probability that player is a spy, p[6] is number of sucessful missions player has done.
        #self.Storage is where all players stats are recorded. This strategy uses memory recollection
        # spyNum is number of spies and playerNum is total number of players

        for p in players:
            player = [p, "r", 0, 0, 0, 0.5,0]
            self.Storage.append(player)






    def select(self, players, count):
        prevteam =[]
        self.me = [p for p in players if p.index == self.index]

        self.choosableguys = [p for p in players if p not in self.defspy]
        self.choose = [p for p in self.choosableguys if p.index != self.index]
        if self.spy:
            #Reasoning -If i select myself, my spy teamate will vote yes, the 1 or 2 resistance members i pick will probably agree to this since they are in team
            #by logic only other resisteance member not in team may disagree to this. I still carry majority.
            #Also casting doubt amognst resistance guys when i sabotage this mission later.
            return [self] + random.sample(set(self.game.players) - set(self.spies), count - 1)

        if self.safeteam:  # and not self._discard(self.team):
            prevteam = [p for p in self.safeteam if p.index != self.index and p not in self.defspy]
            # If the previous team did not include me, reduce it by one.
        if len(prevteam) > count - 1:
            prevteam = random.sample(prevteam, count-1)
            # If there are not enough people still, pick another randomly.
        if len(prevteam) == count - 1:
            return [self] + prevteam
            # Try to put together another team that combines past winners and not spies.
        for p in self.others():
            if p not in self.defspy:
                return [self] + random.sample(self.choose, count-1)


        return [self] + random.sample(self.others(), count - 1)



    def vote(self, team):
        if self.spy:
            return len([p for p in self.game.team if p in self.spies]) > 0

        if self.game.tries == 5:
            return not self.spy

        if self.game.leader == self:
            return True

        # Assume that spies would not be dumb enough to cast themselves out on the first mission
        if len(self.game.team) == 3 and not self in self.game.team:
            return False

        for p in team:
            if p in self.defspy:
                return False

        return True

    def onVoteComplete(self, votes):
        for p in self.game.players:
            player = [p,bool]
            self.playervotes.append(player)

        self.playervotes[0][1]= votes[0]
        self.playervotes[1][1]= votes[1]
        self.playervotes[2][1] = votes[2]
        self.playervotes[3][1] = votes[3]
        self.playervotes[4][1] = votes[4]
        #a resistance player would not vote down when the game has reached its 5th try(spies would win

        self.safeteam= None


    def sabotage(self):
        spiesCount = len([p for p in self.game.team if p in self.spies])
        return spiesCount == 1 or self.game.wins==2 or (spiesCount == 2 and self.game.leader.index != self.index)

    def onMissionComplete(self, sabotaged):
        if self.spy:
            return
        if not sabotaged:
            self.safeteam = self.game.team
            for p in self.Storage:
                if p[0] in self.game.team:
                    p[5]-= 0.2
                    p[5] = 0 if p[5] < 0 else 1 if p[5] > 1 else p[5]
            return

        if self in self.game.team:
            if len(self.game.team) - 1 == sabotaged:
                for p in self.game.team:
                    if p != self:
                        self.defspy.append(p)

        if not self in self.game.team:
            if sabotaged / len(self.game.team) == 1 / 2:
                for p in self.Storage:
                    if p[0] in self.game.team:
                        p[5] += 0.50
                        p[5] = 0 if p[5] < 0 else 1 if p[5] > 1 else p[5]
            if sabotaged / len(self.game.team) == 1:
                for p in self.Storage:
                    if p[0] in self.game.team:
                        self.defspy.append(p[0])
            if sabotaged / len(self.game.team) == 1 / 3:
                for p in self.Storage:
                    if p[0] in self.game.team:
                        p[5] += 0.33
                        p[5] = 0 if p[5] < 0 else 1 if p[5] > 1 else p[5]
            if sabotaged / len(self.game.team) == 2 / 3:
                for p in self.Storage:
                    if p[0] in self.game.team:
                        p[5] += 0.67
                        p[5] = 0 if p[5] < 0 else 1 if p[5] > 1 else p[5]

    def leastLikely(self):
        """Function basically gets all the players that currently have the least probability of being a spy."""

        relativecache= self.Storage
        storeother = []
        leastlikelycache = []
        for p in relativecache:
            if p[0] in self.others():
                storeother.append(p)

        sorted(storeother, key=lambda player: player[5])
        for p in storeother:
            if p[0] != self.me:
                leastlikelycache.append(p[0])


        return leastlikelycache

