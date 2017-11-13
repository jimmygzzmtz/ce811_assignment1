
from player import Bot

import random
import itertools

class sg17402(Bot):
    def onGameRevealed(self, players, spies):
        self.p = []
        self.spies = spies
        self.ProbabilityOfBeingASpy = [0, 0, 0, 0, 0]
        self.GameItirationCount = 0
        self.winCount = 0
        self.lp = players
        for i, x in enumerate(self.lp):
            if (x == self):
                self.selfindex = x.index
        if (len(spies) == 0):
            self.i_Am_RST = True
        else:
            for i, x in enumerate(players):
                if x in spies:
                    self.ProbabilityOfBeingASpy[i] = 1
                else:
                    self.ProbabilityOfBeingASpy[i] = 0

            self.i_Am_RST = False

    def sabotage(self):

        if self.GameItirationCount == 0:
            return False

        if self.winCount == 2 or self.game.losses == 2:
            return True

        if len(self.game.team) == 2:
            if self.game.turn == 1:
                return False

        spies = [s for s in self.game.team if s in self.spies]
        if len(spies) > 1:
            return False

        return True

    def onTeamSelected(self, leader, team):
        pass

    def onVoteComplete(self, votes):
        # print votes
        self.prob(votes)
        pass

    def onMissionComplete(self, sabotaged):
        # print "sabataged",sabotaged

        if not sabotaged:
            self.team = self.game.team

        if (len(self.selectedTeamProbability) == 0):
            self.selectedTeamProbability = [0, 0, 0]

        if (len(self.selectedTeamProbability) == 2):
            self.selectedTeamProbability += [0]

        roundedPlayerProbability = ['%.4f' % elem for elem in self.ProbabilityOfBeingASpy]
        roundedTeamProbability = ['%.4f' % elem for elem in self.selectedTeamProbability]

        if (self.spy):
            spyd = 1
        else:
            spyd = 0

        if (sabotaged == 0):
            sbb = 'win'
        else:
            sbb = 'lost'

        votes = []

        for i in range(len(self.game.votes)):
            # print self.game.votes[i]
            if self.game.votes[i] == True:
                votes.append(1)
            else:
                votes.append(0)

        if (self.game.votes[self.index]):
            selfvote = 1
        else:
            selfvote = 0

        # temp = roundedPlayerProbability  + roundedTeamProbability + self.game.votes + [sbb] + [self.game.votes[self.index]] + [self.spy]
        temp = [spyd] + roundedTeamProbability + [sabotaged] + [selfvote]
        # temp = roundedPlayerProbability + roundedTeamProbability + votes + [sabotaged] + [selfvote] + [spyd]
        # print temp

        # with open('testdata1.csv', 'a') as myfile:
        #     wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
        #     wr.writerow(temp)

        self.Sprob(sabotaged)

        if (sabotaged == 0):
            self.winCount = self.winCount + 1
        self.GameItirationCount = self.GameItirationCount + 1

    def onGameComplete(self, win, spies):
        # print spies
        self.GameItirationCount = 0
        self.winCount = 0

    def select(self, players, count):

        if not self.i_Am_RST:
            """if SPY """
            """ Add self and any other random player and not other spy"""

            temp_ary = [p for p in self.others() if p not in self.spies]
            return [self] + random.sample(temp_ary, count - 1)
        else:
            """ if RST """
            temp_ary = []
            if self.GameItirationCount == 0:
                return [self] + random.sample(self.others(), count - 1)

            temp_sp = list(self.ProbabilityOfBeingASpy)
            temp_sp[self.selfindex] = 99999
            # temp_team = list(self.others())

            """Always select a successful team if there was any in the previous iterations """

            if self.game.wins > 0:
                if self.team:
                    temp = [p for p in self.team if p.index != self.index and p not in self.spies]
                if temp == count:
                    return temp

            """While selecting the other team players always give priority for less probabil-ity value player"""

            for i in range(count):
                if i == 0:
                    temp_ary.append(self)
                else:
                    for j, x in enumerate(self.others()):
                        bst_set = temp_sp.index(min(temp_sp))
                        if x.index == bst_set:
                            temp_ary.append(x)
                            temp_sp[temp_sp.index(min(temp_sp))] = 9999
                            # excluding added player by adding 9999 as probability for next loop
                            break
            return temp_ary

    def vote(self, team):
        # print " "

        def second_largest(numbers):
            count = 0
            m1 = m2 = float('-inf')
            for x in numbers:
                count += 1
                if x > m2:
                    if x >= m1:
                        m1, m2 = x, m1
                    else:
                        m2 = x
            return m2 if count >= 2 else None

        snd_num = second_largest(self.ProbabilityOfBeingASpy)

        """if its the 5th try to make a team and all players must or may not
        trust the team but its better to trust the 5th selected team"""

        if self.game.tries == 5:
            return True

        """when the win count is 2 its better to vote true after 3 failed team missions """

        if self.game.tries == 3 and self.winCount == 2:
            return True

        team_data = []

        self.selectedTeamProbability = []

        if self.i_Am_RST:
            """compare all the value of each player and if the probability of all the players
             is less than the other players outside the team"""
            for i, x in enumerate(self.lp):
                if x == self and x in self.game.team and self.GameItirationCount == 0:
                    return True
                if x in self.game.team:
                    team_data.append(self.ProbabilityOfBeingASpy[x.index])

            self.selectedTeamProbability = team_data

            safeToVote = 0
            # print self.game.team,self.ProbabilityOfBeingASpy

            for i in team_data:
                if i > 0.00:
                    if max(team_data) < max(self.ProbabilityOfBeingASpy) and max(
                            team_data) < snd_num and self.GameItirationCount != 4:
                        return True
                    else:
                        return False
                else:
                    safeToVote = 1

            if safeToVote != 1:
                return False
            else:
                return True

        if self.spy and self.GameItirationCount == 0:
            """If I am a spy and its the first mission always vote true """
            return True

        if not self.i_Am_RST:
            """When the player is spy and has a other spy in the selected team or self in the team vote"""
            if self.spy:
                return len([p for p in team if p in self.spies]) > 0

        if (self.i_Am_RST != True and (self not in self.game.team)):
            return False
        """if not in the game and no other spy is in the game vote false"""
        return True

    def prob(self, vote):
        if (self.i_Am_RST == True):
            if (all(vote[0] == item for item in vote) and self.GameItirationCount == 0):
                for i, x in enumerate(self.lp):
                    if (x in self.game.team):
                        if (x == self):
                            continue
                        else:
                            if self in self.game.team:
                                self.ProbabilityOfBeingASpy[i] += (0.15)
                            else:
                                self.ProbabilityOfBeingASpy[i] += (0.1)

            for i in range(5):
                if (i == self.lp.index(self)):
                    continue
                if (vote[i] == False and self.ProbabilityOfBeingASpy[i] < max(self.ProbabilityOfBeingASpy)):
                    continue
                if (vote[i] == False):
                    self.ProbabilityOfBeingASpy[i] += ((1 / 5.00) * 0.5)  # may be 1/5
        pass

    def Sprob(self, sabotaged):
        me_in_game = False
        if (self in self.game.team):
            me_in_game = True
        if (self.i_Am_RST):
            others = [p for p in self.game.players if p not in self.game.team]

            for i, x in enumerate(self.lp):
                if (x in others):
                    if (x == self):
                        continue
                    if (len(others) == 2 and self in others):
                        self.ProbabilityOfBeingASpy[i] += (1)
                    if (len(others) == 2 and self not in others):
                        self.ProbabilityOfBeingASpy[i] += (0.5)
                    if (len(others) == 3 and self in others):
                        self.ProbabilityOfBeingASpy[i] += (0.5)
                    if (len(others) == 3 and self not in others):
                        self.ProbabilityOfBeingASpy[i] += (0.33)
            """If the team size is 2 and not 3 we can infer that any one among these 2 players
                                 can we a spy with probability of 0.5"""
            """If one of the player is self which is the player itself then its a dead lock
            for the other player who is a spy for sure by probability of 1 """
            # if (self.GameItirationCount == 0 and self in self.game.team):
            #     pass
            if (sabotaged == 1):

                if (len(self.game.team) == 2):
                    for i, x in enumerate(self.lp):
                        if (x in self.game.team):
                            if (x == self):
                                continue
                            if (me_in_game):
                                self.ProbabilityOfBeingASpy[i] += 1
                                self.spy_for_sure = x
                            else:
                                self.ProbabilityOfBeingASpy[i] += (0.5)
                # print others

                if (len(self.game.team) == 3):
                    for i, x in enumerate(self.lp):
                        if (x == self):
                            continue
                        if (x in self.game.team):
                            if (me_in_game):
                                self.ProbabilityOfBeingASpy[i] += 0.5
                            else:
                                self.ProbabilityOfBeingASpy[i] += (0.33)

            if (sabotaged == 2):
                if (len(self.game.team) == 2):
                    for i, x in enumerate(self.lp):
                        if (x in self.game.team):
                            if (x == self):
                                continue
                            self.ProbabilityOfBeingASpy[i] += 1

                if (len(self.game.team) == 3):
                    for i, x in enumerate(self.lp):
                        if (x == self):
                            continue
                        if (x in self.game.team):
                            self.ProbabilityOfBeingASpy[i] += (0.666)

            if (sabotaged == 0 and self.GameItirationCount >= 1):
                for i in range(5):
                    if (i == self.lp.index(self)):
                        continue
                    if (self.game.votes[i] == False):
                        self.ProbabilityOfBeingASpy[i] += (1 / 4.0)  # may be 1/5

                if (len(self.game.team) == 2):
                    for i, x in enumerate(self.lp):
                        if (x == self):
                            continue
                        if (x in self.game.team):
                            self.ProbabilityOfBeingASpy[i] -= (0.5)
                            # self.ProbabilityOfBeingASpy[i] = (0.0)
                if (len(self.game.team) == 3):
                    for i, x in enumerate(self.lp):
                        if (x == self):
                            continue
                        if (x in self.game.team):
                            self.ProbabilityOfBeingASpy[i] = (0.0)
                            # self.ProbabilityOfBeingASpy[i] -= (0.33)

                rst = [p for p in self.lp if p not in self.game.team]

                # print "they are spy", rst
                if (len(rst) == 2):
                    for i, x in enumerate(self.lp):
                        if (x == self):
                            continue
                        if (x in rst):
                            if (self in rst):
                                self.ProbabilityOfBeingASpy[i] += (1)
                            else:
                                self.ProbabilityOfBeingASpy[i] += (0.5)

                if (len(rst) == 3):
                    for i, x in enumerate(self.lp):
                        if (x == self):
                            continue
                        if (x in rst):
                            if (x in rst):
                                if (self in rst):
                                    self.ProbabilityOfBeingASpy[i] += (0.5)
                                else:
                                    self.ProbabilityOfBeingASpy[i] += (0.33)
