
# This class keeps statistics of the resistance game.
class Statistics:

    # Number of times selected.
    selects = None
    # Player has been on failed mission.
    sabotages = None
    # Highest sabotage probability (later action is valued more).
    spyProb = None
    # Highest sabotage probability (all actions are equaly treated).
    spyProb2 = None
    # number of failed mission for players.
    failedMissions = None
    # Number of times a player has been on mission success.
    successes = None
    # Number of times a player has votes yes.
    yesVotes = None
    # Number of times a player has votes no.
    noVotes = None
    # isSpy
    isSpies = None


    # ******************** INIT FUNCTIONS ********************


    # Reset statistics.
    def newGame(self, players):
        playerCount = len(players)
        self.selects = self.initArray(playerCount, 0)
        self.sabotages = self.initArray(playerCount, 0)
        self.spyProb = self.initArray(playerCount, float(1/playerCount))
        self.spyProb2 = self.initArray(playerCount, float(1/playerCount))
        self.failedMissions = self.initArray(playerCount, 0)
        self.successes = self.initArray(playerCount, 0)
        self.yesVotes = self.initArray(playerCount, 0)
        self.noVotes = self.initArray(playerCount, 0)
        self.isSpies = self.initArray(playerCount, 0)

    # Initate array with same lenth as players with zeroes.
    def initArray(self, c, value):
        a = []
        for i in range(c):
            a.append(value)
        return a


    # ******************** CHANGE FUNCTIONS ********************


    # Update probability for player.
    def changeProbability(self, p, prob):
        # Update spyProb.
        self.spyProb[p.index] = (self.spyProb[p.index] + prob) / 2

        # Update spyProb2.
        difference = prob - self.spyProb2[p.index]
        self.spyProb2[p.index] = self.spyProb2[p.index] + (difference / (1+self.getSpyProbAdjustments(p)))

        # If we know who the spies are, then set their probability to 1.
        if self.isSpies[p.index] == 1.0:
            self.spyProb2[p.index] == 1.0
            self.spyProb[p.index] == 1.0


    # ******************** ADD FUNCTIONS ********************


    # Update selects count for players on the team.
    def addSelects(self, team):
        for p in team:
            self.selects[p.index] += 1

    # Update Sabotages count for players in the team.
    # And update probability for players in the team.
    # Dont calculate probability according to that I am a spy,
    # Because we want to play like we are an resistance and dont know
    # that the other players are spies.
    def addSabotages(self, team, players, sabotageCount, me):
        for p in team:
            self.sabotages[p.index] += 1

        # Check if there was 2 sabotages on a team with 2 players.
        # Then we know that both are spies.
        if not me.iAmSpy and len(team) == 2 and sabotageCount == 2:
            for p in team:
                self.isSpies[p.index] = 1.0
                # If we know who the spies are, then set their probability to 1.
                self.spyProb[p.index] = 1.0
                self.spyProb2[p.index] = 1.0

        # Calculate probalibity.

        # List of all players in the team (not me inculded).
        teamNotMe = []
        for t in team:
            if t != me:
                teamNotMe.append(t)

        # List of all other players.
        playersNotMe = []
        for p in players:
            if p != me:
                playersNotMe.append(p)

        # Calculate probalibity for every player based on this round.
        # And update players spy probalibity.
        for p in playersNotMe:
            prob = 0.0
            if p in teamNotMe:
                # Calculate probability of player on team.
                prob = float(sabotageCount) / (float(len(teamNotMe)))
                if prob > 1.0:
                    prob = 1.0
            else:
                # Calculate probability of player not in team.
                prob = 1 - (float(sabotageCount) / (float(len(teamNotMe))))
                # If I and another spy sabotaged sabotageCount is greater than teamNotMe.
                if prob < 0:
                    prob = 0.0
                prob = prob / (float(len(playersNotMe)) - float(len(teamNotMe)))

            # Update probalibities.
            self.changeProbability(p, prob)

    # Update failed mission count for players on the team.
    def addFailedMissions(self, team):
        for p in team:
            self.failedMissions[p.index] += 1

    # Update mission success count for players on the team.
    # And update players spy probalibity.
    def addSuccessMission(self, team):
        for p in team:
            self.successes[p.index] += 1

    # Update votes.
    def addVotes(self, votes):
        for i in range(len(votes)):
            if votes[i]:
                # Votes yes.
                self.yesVotes[i] += 1
            else:
                # Votes no.
                self.noVotes[i] += 1


    # ******************** GET FUNCTIONS ********************


    def getStatsFromPlayer(self, p, turn, tries):
        inputs = []
        inputs.append(tries)
        inputs.append(turn)
        inputs.append(self.sabotages[p.index])
        inputs.append(self.spyProb[p.index])
        inputs.append(self.spyProb2[p.index])
        inputs.append(self.failedMissions[p.index])
        inputs.append(self.successes[p.index])
        inputs.append(self.getVoteRatio(p.index))
        inputs.append(self.selects[p.index])
        inputs.append(self.isSpies[p.index])
        return inputs


    # Returns the vote ratio.
    def getVoteRatio(self, index):
        y = float(self.yesVotes[index])
        n = float(self.noVotes[index])
        if (y + n) == 0:
            return 0.5
        return float(y / (y + n))

    # Gets the number of times the probability has changed for a this player.
    def getSpyProbAdjustments(self, p):
        x = self.successes[p.index] + self.sabotages[p.index]
        if x > 0:
            return x
        return 1
