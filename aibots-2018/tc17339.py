from player import Bot
import random

class tc17339(Bot):

    def onGameRevealed(self, players, spies):
        self.spies = spies
        self.players = players

    def select(self, players, count):
        # If i am spy, i will select myself and randomly select another players
        if not self.spy:
            return random.sample(self.others(), count)
        else:
            return [self] + random.sample(self.others(), count - 1)

    def vote(self, team):
        #if i am spy that in the team, at the begin of the game, i would object
        if self.spy:
            if self in self.game.team:
                if self.game.tries ==1:
                    return False

                return True
        if not self.spy:
            if self.game.tries == 1:
                return False
        if self.game.leader:
            return True
        else:
            return True

    def sabotage(self):
        #spies = [n for n in self.game.team if n in self.spies]
        #print(self.spies)
        if self.game.turn == 1 and self.game.leader not in self.spies:
            return False
        if len(self.spies) > 1:
            return False
        if self.game.turn == 5:
            return True
        return False


