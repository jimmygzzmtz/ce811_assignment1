import random
import information
import operator

from player import Bot

class ml17390(Bot):

    def onGameRevealed(self, players, spies):
        self.info = information.Information()
        self.spies = spies
        self.players = players
        self.resistance = {}
        if self.spies != []:
            self.spies_list = []
            self.resistance_list = []
            for x in range(len(players)):
                if (players[x] in spies) == False:
                    self.resistance[players[x]] = random.uniform(0.5, 1.0)
                    self.resistance_list.append(players[x])
                else:
                    self.spies_list.append(players[x])

        for x in range(5):
            self.info.votes_up[x]= 0
            self.info.votes_down[x] = 0

    def onMissionAttempt(self, mission, tries, leader):
        self.mission = mission
        self.tries = tries
        self.info.leader = leader

    def onVoteComplete(self, votes):
        self.info.setVotes(votes)

    def onTeamSelected(self, leader, team):
        self.info.last_team = {}

    def announce(self):
        if self.spy:
            if random.choice([True, False]):
                return self.resistance
        else:
            resistance_probability_sorted = sorted(self.info.resistance_probability.items(), key=operator.itemgetter(1))
            prob_spies = {}
            x = 0
            while (x < len(resistance_probability_sorted)) and (x < 2):
                if resistance_probability_sorted[x][1] <= 0.49:
                    prob_spies[resistance_probability_sorted[x][0]] = resistance_probability_sorted[x][1]
                x += 1
            return prob_spies

    def select(self, players, count):
        selected_list = []

        if self.mission > 1:
            if self.spy:
                #The choose is betwwen me and my spies partners(only one of us) and the rest the resistance
                x = random.randrange(len(self.spies_list))
                if self.spies_list[x] == self:
                    random.choice([self.say("Picking myself and others I don't trust."), self.say("Picking myself and others I trust.")])
                else:
                    random.choice([self.say("Picking others I don't trust."), self.say("Picking others I trust.")])
                selected_list.append(self.spies_list[x])
                for x in range(count-1):
                    player =  self.resistance_list[x]
                    selected_list.append(player)

            else:
                # The choose is between those who has lees probability of being spy (always include myself)
                spy_probability_sorted = sorted(self.info.spy_probability.items(), key=operator.itemgetter(1))
                selected_list.append(self)
                random.choice([self.say("Picking myself and others I don't trust."), self.say("Picking myself and others I trust.")])
                for x in range(count-1):
                    player =  spy_probability_sorted[x][0]
                    selected_list.append(player)

        else:
            #In the firs mission I have no information at all
            self.say("Picking myself and others I don't trust.")
            selected_list = [self] + random.sample(self.others(), count - 1)

        return selected_list

    def onMissionComplete(self, sabotaged):
        self.info.setSabotages(sabotaged)
        self.info.setNONSabotages((len(self.game.team) - sabotaged))
        self.info.setSelectTeam(self.mission, self.game.team, self.index)
        self.info.setWhenSabotage(self.mission, self.game.team)
        self.info.setSpiesVictories(sabotaged)
        self.info.setResistanceVictories(sabotaged)
        self.info.setIdentity(self.index, self.players, self.mission)

        # Restore the number of votes per mission
        for x in range(5):
            self.info.votes_up[x] = 0
            self.info.votes_down[x] = 0

    def vote(self, team):
        if self.mission > 1:
            if self.spy:
                # If I am a SPY, I want to VOT UP only if at least one my partners is in the team
                for x in range(len(team)):
                    if team[x] in self.spies:
                        self.say("Everything is OK with me, man.")
                        return True
                self.say("I don't trust in that team, man.")
                return False
            else:
                #If I am RESISTANCE, I want to VOTE DOWN only if I think there is no spies in it
                max_prob = 0.0
                for x in range(len(team)):
                    if team[x] in self.info.spy_probability:
                        if self.info.spy_probability[team[x]] > max_prob:
                            max_prob = self.info.spy_probability[team[x]]
                if max_prob <= 0.50:
                    self.say("Everything is OK with me, man.")
                    return True
                else:
                    self.say("I don't trust in that team, man.")
                    return False
        else:
            # Trivial decisions
            if (self.game.leader == self) or (self.game.tries == 5):
                self.say("Everything is OK with me, man.")
                return True
            if len(team) == 3 and not self.index in [p.index for p in team]:
                self.say("I'm not on the team and it's a team of 3!.")
                return False
            self.say("I leave you the responsibility team.")
            return random.choice([True, False])

    def sabotage(self):
        '''spies_in_team = []
        for x in range(len(self.game.team)):
            if self.game.team[x] in self.spies:
                spies_in_team.append(self.game.team[x])

        answer = self.info.shouldIsabotaged(spies_in_team, len(self.game.team), self)
        #If we choose to sabotage, we increment the sabotages per player
        if answer == 'YES':
            self.info.setNumSabotagesPerPlayer(self)
            return True
        else:
            return False'''
        return self.spy


    #def onGameComplete(self, win, spies):
        #self.info.writeIdentities("mission.arff", spies)
        #self.info.calculateWhenSabotage(win,spies,self.game.sabotages_player)
        #self.info.writeSabotages("sabotages.arff")
