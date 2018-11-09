import random
from player import Bot

class SalBot(Bot):
    """An AI bot that tends to vote everything down!"""
    def onGameRevealed(self, players, spies):
        global noOfSabotages
        global suspectedplayers
        # initializing our dict of player spy probabilities
        suspectedplayers = {}
        for n in players:
            suspectedplayers.update({n: 30.0})
        noOfSabotages = 0

    def select(self, players, count):
        global suspectedplayers
        if not self.spy:

            #Just pick randomly since we have no information for this round
            if self.game.turn == 1:
                return [self] + random.sample(self.others(), count - 1)

            self.say("Picking myself and people that aren't spies")
            innocentpeople = self.innocentpeople(self.others(), suspectedplayers)
            self.say(innocentpeople)
            if count == 2:
                return [self] + [innocentpeople[0]]
            else:
                return [self] + innocentpeople

        return [self] + random.sample(self.others(), count - 1)


    def innocentpeople(self, team, probabilities):

        # declare two variables to hold the names of the two least suspicious players
        leastsuspicious = team[0]
        secondleastsuspicious = team[1]

        # loop to find the two least suspicious players
        for f in probabilities:
            if str(self.name) in str(f):
                continue
            if probabilities[f] < probabilities[leastsuspicious]:
                leastsuspicious = f
                continue
            if (probabilities[f] <= probabilities[secondleastsuspicious] and f is not leastsuspicious) or leastsuspicious == secondleastsuspicious:
                secondleastsuspicious = f

        # throw two least suspicious people in a list and throw it back
        goodpeople = [leastsuspicious, secondleastsuspicious]
        return goodpeople

    def vote(self, team):
        global suspectedplayers

        # return true if it's the fifth vote
        if self.game.tries == 5:
            return True
        if not self.spy:

            # return true if it's the first mission and we have no information about the spies
            if self.game.turn == 1:
                return True
            else:

                # return false if the two most suspicious people are on the mission team
                return self.suspiciouspeople(team, suspectedplayers)

        return False

    def suspiciouspeople(self, team, probabilities):

        # declare two variables to hold the names of the two most suspicious players
        mostsuspicious = team[0]
        secondmostsuspicious = team[1]
        # loop to find the two most suspicious players
        for f in probabilities:
            if probabilities[f] > probabilities[mostsuspicious]:
                mostsuspicious = f
            elif probabilities[f] > probabilities[secondmostsuspicious]:
                secondmostsuspicious = f

        # check if any of the most suspicious players are in the team
        for x in team:
            if x is self:
                continue
            if x is mostsuspicious or x is secondmostsuspicious:
                self.say("This team has a spy! We can't vote for it!")
                return False
        return True

    def sabotage(self):
        self.log.debug("I always sabotage when I'm a spy. Unless I'm in a team with only one other")
        if len(self.game.team) == 2:
            return False
        return True

    def onMissionComplete(self, sabotaged):
        global noOfSabotages
        if sabotaged > 0:
            self.say("You're all dirty spies!!")
            noOfSabotages = sabotaged

    def announce(self):

        global noOfSabotages
        global suspectedplayers

        # if there was a failed mission...
        if noOfSabotages != 0:
            self.say(str(noOfSabotages) + " Sabotages detected!")

            # iterate through all team members...
            for f in self.game.team:

                # ignore self...
                if f == self:
                    continue

                # if self was part of the team...
                if self in self.game.team:

                    # if there was a sabotage and only one other team member, declare the other a spy
                    if len(self.game.team) == 2:
                        suspectedplayers[f] += 200
                        self.say(str(suspectedplayers[f]) + " is a spy!!")

                    # if the team size was 3 instead of 2
                    else:

                        # if there were two sabotages, declare both others spies
                        if noOfSabotages == 2:
                            suspectedplayers[f] += 200
                            self.say((str(suspectedplayers[f]) + " is a spy!!"))

                        # otherwise just increase the spy score of the other team members by the regular amount
                        else:
                            suspectedplayers[f] += 20
                # otherwise if self was not part of the team...
                else:

                    # if self is not in the team and it's a team of two...
                    if len(self.game.team) == 2:

                        # if somehow two spies in a team of two are stupid enough to sabotage twice...
                        if noOfSabotages == 2:
                            suspectedplayers[f] += 200
                            self.say(str(suspectedplayers[f]) + " is a spy!!")

                        # otherwise just increase their spy scores by the regular amount
                        else:
                            suspectedplayers[f] += 20

                    # if it's not a team of two it must be a team of three...
                    else:

                        # if there were two sabotages in a team of three increase spy scores by good amount
                        if noOfSabotages == 2:
                            suspectedplayers[f] += 30

                        # otherwise increase spy score by a small amount instead
                        else:
                            suspectedplayers[f] += 10

            for x, y in suspectedplayers.items():
                self.say(str(x) + " has a spy score of " + str(y))

        #if no sabotages
        else:
            for f in self.game.team:

                # ignore self...
                if f == self:
                    continue

                suspectedplayers[f] -= 5

        self.say(suspectedplayers)
        return suspectedplayers