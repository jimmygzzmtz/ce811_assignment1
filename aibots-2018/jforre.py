"""
jforre.py
A bot that plays The Resistance using a decision tree, opponent modelling
and expert rules.
"""
from player import Bot
import random


class jforre(Bot):

    def onGameRevealed(self, players, spies):
        self.players = players
        self.spies = spies
        self.upvotes = [0]*5
        self.downvotes = [0]*5
        self.thisvotes = [False]*5
        self.missionFails = [0]*5
        self.leaderFails = [0]*5
        self.succeededMissions = [0]*5
        self.sabotages = [0]*5
        self.sel = [0]*5
        self.wins = [0]*5
        self.losses = [0]*5
        self.selfsel = [0]*5

    def is_spy(self, p):
        """
        Deduce whether a given player is a spy or not
        :param p:  the player to examine
        :return: true if spy, else false
        """
        if self.wins[p.index] <= 0:
            if self.game.wins <= 1:
                if self.selfsel[p.index] <= 0:
                    if self.missionFails[p.index] <= 0:
                        if self.downvotes[p.index] <= 0:
                            if self.sabotages[p.index] <= 1:
                                return False
                            else:
                                if self.sabotages[p.index] <= 2:
                                    if self.game.losses <= 1:
                                        return True
                                    else:
                                        return False
                                else:
                                    return True
                        else:
                            if self.game.wins <= 0:
                                if self.sabotages[p.index] <= 1:
                                    if self.game.tries <= 1:
                                        return False
                                    else:
                                        if self.sel[p.index] <= 0:
                                            return False
                                        else:
                                            return True
                                else:
                                    if self.upvotes[p.index] <= 1:
                                        if self.sel[p.index] <= 1:
                                            return True
                                        else:
                                            return False
                                    else:
                                        return True
                            else:
                                return True
                    else:
                        return False
                else:
                    if self.sabotages[p.index] <= 1:
                        if self.missionFails[p.index] <= 1:
                            if self.sel[p.index] <= 1:
                                if self.game.turn <= 3:
                                    if self.game.losses <= 1:
                                        return True
                                    else:
                                        if self.upvotes[p.index] <= 1:
                                            return False
                                        else:
                                            if self.downvotes[p.index] <= 0:
                                                return True
                                            else:
                                                if self.downvotes[p.index] <= 1:
                                                    return False
                                                else:
                                                    return True
                                else:
                                    return True
                            if self.leaderFails[p.index] <= 0:
                                return False
                            else:
                                if self.upvotes[p.index] <= 3:
                                    if self.downvotes[p.index] <= 1:
                                        return True
                                    else:
                                        if self.game.turn <= 3:
                                            return False
                                        else:
                                            if self.downvotes[p.index] <= 2:
                                                return True
                                            else:
                                                return False
                                else:
                                    return False
                        else:
                            if self.downvotes[p.index] <= 1:
                                return False
                            else:
                                if self.upvotes[p.index] <= 3:
                                    return False
                                else:
                                    return True
                    else:
                        if self.sabotages[p.index] <= 2:
                            if self.game.losses <= 1:
                                return True
                            else:
                                if self.sel[p.index] <= 1:
                                    return True
                                else:
                                    if self.sel[p.index] <= 2:
                                        if self.game.tries <= 1:
                                            if self.upvotes[p.index] <= 2:
                                                return True
                                            else:
                                                if self.downvotes[p.index] <= 1:
                                                    if self.leaderFails[p.index] <= 0:
                                                        return False
                                                    else:
                                                        return True
                                                else:
                                                    return False
                                        else:
                                            return True
                                    else:
                                        if self.sel[p.index] <= 3:
                                            if self.upvotes[p.index] <= 4:
                                                if self.game.tries <= 1:
                                                    return True
                                                else:
                                                    return False
                                            else:
                                                return True
                                        else:
                                            return False
                        else:
                            return True
            else:
                if self.downvotes[p.index] <= 0:
                    if self.missionFails[p.index] <= 1:
                        if self.selfsel[p.index] <= 0:
                            if self.upvotes[p.index] <= 3:
                                if self.sabotages[p.index] <= 1:
                                    return False
                                else:
                                    return True
                            else:
                                return False
                        else:
                            return True
                    else:
                        return False
                else:
                    return True
        else:
            if self.sabotages[p.index] <= 2:
                if self.upvotes[p.index] <= 1:
                    if self.upvotes[p.index] <= 0:
                        return True
                    else:
                        if self.losses[p.index] <= 0:
                            return False
                        else:
                            if self.wins[p.index] <= 1:
                                if self.game.wins <= 1:
                                    if self.game.turn <= 3:
                                        if self.downvotes[p.index] <= 3:
                                            return False
                                        else:
                                            return True
                                    else:
                                        return False
                                else:
                                    if self.sabotages[p.index] <= 1:
                                        return False
                                    else:
                                        return True
                            else:
                                return False
                else:
                    return False
            else:
                if self.upvotes[p.index] <= 3:
                    if self.wins[p.index] <= 1:
                        return True
                    else:
                        return False
                else:
                    return False

    def onTeamSelected(self, leader, team):
        if leader in team:
            self.selfsel[leader.index] += 1
        for p in team:
            self.sel[p.index] += 1


    def onVoteComplete(self, votes):
        self.thisvotes = votes
        for i in range(0, len(self.players)):
            if votes[i]:
                self.upvotes[i] += 1
            else:
                self.downvotes[i] += 1

    def onMissionComplete(self, sabotaged):
        for p in self.game.team:
            self.sabotages[p.index] += sabotaged

            if sabotaged>0:
                self.losses[p.index] += 1
            else:
                self.wins[p.index] += 1




    def onMissionFailed(self, leader, team):
        self.leaderFails[leader.index] += 1
        for p in team:
            self.missionFails[p.index] += 1

    def select(self, players, count):
        ##f = open("data.arff", "a")
        ##if self.game.turn != 1 and not self.spy:
        ##    for p in players:
        ##        f.write(str(self.game.turn) + ",")
        ##        f.write(str(self.game.tries) + ",")
        ##        f.write(str(self.game.wins) + ",")
        ##        f.write(str(self.game.losses) + ",")
        ##        f.write(str(self.sel[p.index]) + ",")
        ##        f.write(str(self.sabotages[p.index]) + ",")
        ##        f.write(str(self.upvotes[p.index]) + ",")
        ##        f.write(str(self.downvotes[p.index]) + ",")
        ##        f.write(str(self.missionFails[p.index]) + ",")
        ##        f.write(str(self.leaderFails[p.index]) + ",")
        ##        f.write(str(self.wins[p.index]) + ",")
        ##        f.write(str(self.losses[p.index]) + ",")
        ##        f.write(str(self.selfsel[p.index]) + ",")
        ##        f.write(str(p in self.spies) + "\n")

        # Always add self to team
        team = [self]

        if not self.spy:
            # Use decision tree to add any players we think aren't spies
            for p in players:
                if not self.is_spy(p) and not p in team:
                    team.append(p)

        # Ensure team is correct size
        if not self.spy:
            if len(team) < count:
                # If team is too small, add some people randomly
                others = self.others()
                for p in team:
                    if p in others: others.remove(p)
                return team + random.sample(others, count - len(team))
            if len(team) > count:
                # If team is too big, truncate it
                return team[:count]
            return team

        # If spy, return a random selection of people as well as ourself
        return [self] + random.sample(self.others(), count - 1)

    def vote(self, team):
        ##f = open("votedata.arff", "a")
        ##if self.game.turn != 1 and not self.spy:
        ##    for p in team:
        ##        f.write(str(self.game.turn) + ",")
        ##        f.write(str(self.game.tries) + ",")
        ##        f.write(str(self.game.wins) + ",")
        ##        f.write(str(self.game.losses) + ",")
        ##        f.write(str(self.sel[p.index]) + ",")
        ##        f.write(str(self.sabotages[p.index]) + ",")
        ##        f.write(str(self.upvotes[p.index]) + ",")
        ##        f.write(str(self.downvotes[p.index]) + ",")
        ##        f.write(str(self.missionFails[p.index]) + ",")
        ##        f.write(str(self.leaderFails[p.index]) + ",")
        ##        f.write(str(self.wins[p.index]) + ",")
        ##        f.write(str(self.losses[p.index]) + ",")
        ##        f.write(str(self.selfsel[p.index]) + ",")
        ##        f.write(str(p in self.spies) + "\n")

        if self.spy:
            # Vote to accept any team with a spy in
            for p in team:
                if p in self.spies:
                    return True
            return False

        nonspycount = 0
        if not self.spy:
            # Must approve the last try otherwise spies autowin the round
            if self.game.tries == 5:
                return True

            # IF there's a team of 3, and i'm not a spy, and i'm not in the team,
            # there is guaranteed to be a spy in the team
            if len(team) == 3 and not self in team:
                return False

            # Else, count how many players probably aren't spies
            for p in team:
                if p == self:
                    nonspycount += 1
                    continue
                if not self.is_spy(p):
                    nonspycount += 1

            # Trust my own selected team
            if self.game.leader == self:
                return True

            # If we reckon all players aren't spies, approve the team
            if len(team) - nonspycount == 0:
                return True
            else:
                return False
        return True

    def sabotage(self):
        # Never sabotage the first turn - reduces suspicion!
        if self.game.turn == 1:
            return False

        # Always sabotage the last turn - suspicion doesn't matter anymore
        if self.game.turn == 5:
            return True

        # Count spies in team
        spycount = 0
        for p in self.game.team:
            if p in self.spies and p != self:
                spycount += 1

        # Only vote to sabotage if we're the only spy, reduces suspicion
        if spycount > 0:
            return False
        return True