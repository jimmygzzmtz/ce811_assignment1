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

