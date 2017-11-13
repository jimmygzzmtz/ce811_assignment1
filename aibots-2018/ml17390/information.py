from __future__ import division
import os

"""Class to store information about the bot ml17390"""
class Information(object):
    MISSIONS_NUMBER = 5

    def __init__(self):
        self.spies_victories = 0                 # Spies victories number
        self.resistance_victories = 0            # Resistance victories number
        self.sabotages = 0                       # Number of sabotages in the previous mission
        self.non_sabotages = 0                   # Number of NON sabotages in the previous mission
        self.leader = []                         # Last leader of the team
        self.selected_team = {}                  # Array storing: spy_v, res_v, sabotages, non_sabotages, votes_up, votes_down
        self.votes_up = {}                       # Number of votes UP of an specific player
        self.votes_down = {}                     # Number of votes DOWN of an specific player
        self.last_team = {}                      # Player name: si era lider y si se ha includi
        self.identity_probability = {}           # Player name: Identity, probability
        self.spy_probability_count = {}          # Counter for build the probabilities
        self.resistance_probability_count = {}   # Counter for build the probabilities
        self.spy_probability = {}                # Player: probability of that player to by a spy
        self.resistance_probability = {}         # Player: probability of that player to be a resistance
        self.num_sabotages_per_player = {}       # Player: num_sabotages in a game
        self.when_sabotage = {}                  # Array sotirng: spy_v, res_v, spies_in_team, size_team
        self.calculate_when_sabotage = {}        # Array sotirng: spy_v, res_v, spies_in_team, size_team, num_sabotages_per_player, if the player sabotaged or not


    def clone(self):
        s = Information()
        s.__dict__ = self.__dict__.copy()
        return s

    def __eq__(self, other):
        return \
            self.spies_victories == other.spies_victories \
            and self.resistance_victories == other.resistance_victories \
            and self.sabotages == other.sabotages \
            and self.non_sabotages == other.non_sabotages \
            and self.leader == other.leader \
            and self.selected_team == other.selected_team \
            and self.votes_up == other.votes_up \
            and self.votes_down == other.votes_down \
            and self.last_team == other.last_team \
            and self.identity_probability == other.identity_probability \
            and self.spy_probability_count == other.spy_probability_count \
            and self.resistance_probability_count == other.resistance_probability_count \
            and self.spy_probability == other.spy_probability \
            and self.resistance_probability == other.resistance_probability \
            and self.num_sabotages_per_player == other.num_sabotages_per_player \
            and self.when_sabotage == other.when_sabotage \
            and self.calculate_when_sabotage == other.calculate_when_sabotage \


    def setSpiesVictories(self, spieswon):
        if spieswon:
            self.spies_victories += 1

    def setResistanceVictories(self, spieswon):
        if spieswon == 0:
            self.resistance_victories += 1

    def setSabotages(self, sabotages):
        self.sabotages = sabotages

    def setNONSabotages(self, non_sabotages):
        self.non_sabotages = non_sabotages

    def setVotes(self, votes):
        for x in range(len(votes)):
            if votes[x]:
                self.votes_up[x] += 1
            else:
                self.votes_down[x] += 1

    def setSelectTeam(self, mission, team, me):
        i = 0
        while i < len(team):
            if team[i].index != me:
                x = []
                x.append(self.spies_victories)
                x.append(self.resistance_victories)
                x.append(self.sabotages)
                x.append(self.non_sabotages)
                x.append(self.votes_up[team[i].index])
                x.append(self.votes_down[team[i].index])
                self.selected_team[team[i],mission] = x
                #We stored the information of the last team
                y = []
                y.append(mission)
                y.append(self.votes_up[team[i].index])
                y.append(self.votes_down[team[i].index])
                self.last_team[team[i]] = y
            i += 1

    def setIdentity(self, me, players, current_mission):
        keys = list(self.last_team.keys())
        for x in range(len(self.last_team)):
            #I know my role, so I dont include me
            if keys[x].index != me:
                # Calculation of probabilities for a specific player, using information of the current game (In the first mission it cannot be done)
                mission = self.last_team[keys[x]][0]
                voteup = self.last_team[keys[x]][1]
                votedown = self.last_team[keys[x]][2]
                self.isSpy(voteup, votedown, keys[x], mission)

        #Once we have a list with all the probabilities of each player(several for a same player, one per mission)
        #We calculate TWO unique probability per player, ONE per SPY and one per RESISTANCE:
        for i in range(len(players)):
            for x in range(current_mission,current_mission+1):
                if (players[i],x) in self.identity_probability:
                    role = self.identity_probability[players[i],x][0]
                    if role == 'SPY':
                        if players[i] in self.spy_probability_count:
                            self.spy_probability_count[players[i]] += 1
                        else:
                            self.spy_probability_count[players[i]] = 1
                    elif role == 'RESISTANCE':
                        if players[i] in self.resistance_probability_count:
                            self.resistance_probability_count[players[i]] += 1
                        else:
                            self.resistance_probability_count[players[i]] = 1

        #Finally, calculation of the probabilities for each player
        for i in range(len(players)):
            if players[i].index != me:
                playerisspy = (players[i] in self.spy_probability_count)
                playerisrst = (players[i] in self.resistance_probability_count)
                if playerisspy and playerisrst:
                    # probSPY[player1]= (pSP1+pSP2+..pSPn)/(#SPY+#RST)
                    # probRST[player1]= (pRP1+pRP2+..pRPn)/(#SPY+#RST)
                    num_spy = self.spy_probability_count[players[i]]
                    num_resistance = self.resistance_probability_count[players[i]]
                    sp = (num_spy / (num_spy + num_resistance))
                    rs = (num_resistance / (num_spy + num_resistance))
                    self.spy_probability[players[i]] = sp
                    self.resistance_probability[players[i]] = rs

                elif playerisspy:
                    self.spy_probability[players[i]] = 1.0
                    self.resistance_probability[players[i]] = 0.0

                elif playerisrst:
                    self.spy_probability[players[i]] = 0.0
                    self.resistance_probability[players[i]] = 1.0

                else:
                    #Suponinedo que yo soy resistance, el jugador podria ser cualquier cosa por igual
                    self.spy_probability[players[i]] = 2.0 / 4
                    self.resistance_probability[players[i]] = 2.0 / 4




    def isSpy(self, votes_up, votes_down, player, mission):

        # Los numeros entre brakets indican la fiabilidad. ((bien clasificados)/(total de casos clasificados))*bien clasificados---- NO LO USO AUN
        if votes_up == 0:
            if self.non_sabotages == 0:
                self.identity_probability[player, mission] = ['SPY', -777]
            elif self.non_sabotages == 1:
                if votes_down == 5:
                    self.identity_probability[player, mission] = ['SPY', -777]
                else:
                    self.identity_probability[player, mission] = ['RESISTANCE', -777]
            elif self.non_sabotages == 2:
                if votes_down == 5:
                    self.identity_probability[player, mission] = ['SPY', -777]
                else:
                    self.identity_probability[player, mission] = ['RESISTANCE', -777]
            elif self.non_sabotages == 3:
                if self.spies_victories == 0:
                    self.identity_probability[player, mission] = ['SPY', -777]
                elif self.spies_victories == 1:
                    if self.resistance_victories == 0:
                        self.identity_probability[player, mission] = ['SPY', -777]
                    else:
                        self.identity_probability[player, mission] = ['RESISTANCE', -777]
                elif self.spies_victories == 2:
                    self.identity_probability[player, mission] = ['RESISTANCE', -777]
        elif votes_up == 1:
            if self.non_sabotages == 0:
                self.identity_probability[player, mission] = ['SPY', -777]
            elif self.non_sabotages == 1:
                if votes_down == 0:
                    self.identity_probability[player, mission] = ['SPY', -777]
                elif votes_down == 1:
                    if self.resistance_victories == 0:
                        self.identity_probability[player, mission] = ['SPY', -777]
                    elif self.resistance_victories == 1:
                        self.identity_probability[player, mission] = ['RESISTANCE', -777]
                    elif self.resistance_victories == 2:
                        if self.sabotages == 1:
                            self.identity_probability[player, mission] = ['SPY', -777]
                        else:
                            self.identity_probability[player, mission] = ['RESISTANCE', -777]
                elif votes_down == 2:
                    if self.sabotages == 0:
                        self.identity_probability[player, mission] = ['RESISTANCE', -777]
                    elif self.sabotages == 1:
                        if self.resistance_victories == 1:
                            self.identity_probability[player, mission] = ['RESISTANCE', -777]
                        else:
                            self.identity_probability[player, mission] = ['SPY', -777]
                    elif self.sabotages == 2:
                        if self.resistance_victories == 0:
                            self.identity_probability[player, mission] = ['SPY', -777]
                        else:
                            self.identity_probability[player, mission] = ['RESISTANCE', -777]
                elif votes_down == 3:
                    if self.resistance_victories == 0:
                        self.identity_probability[player, mission] = ['SPY', -777]
                    else:
                        self.identity_probability[player, mission] = ['RESISTANCE', -777]
                elif votes_down == 4:
                    if self.resistance_victories == 0:
                        self.identity_probability[player, mission] = ['SPY', -777]
                    elif self.resistance_victories == 1:
                        if self.spies_victories == 2:
                            self.identity_probability[player, mission] = ['SPY', -777]
                        else:
                            self.identity_probability[player, mission] = ['RESISTANCE', -777]
                    elif self.resistance_victories == 2:
                        self.identity_probability[player, mission] = ['RESISTANCE', -777]
                elif votes_down == 5:
                    self.identity_probability[player, mission] = ['SPY', -777]
            elif self.non_sabotages == 2:
                self.identity_probability[player, mission] = ['RESISTANCE', -777]
            elif self.non_sabotages == 3:
                self.identity_probability[player, mission] = ['RESISTANCE', -777]
        elif votes_up == 2:
            if self.sabotages == 0:
                if self.resistance_victories == 0:
                    self.identity_probability[player, mission] = ['RESISTANCE', -777]
                elif self.resistance_victories == 1:
                    if self.spies_victories == 0:
                        if (votes_down == 2) or (votes_down == 3):
                            self.identity_probability[player, mission] = ['RESISTANCE', -777]
                        else:
                            self.identity_probability[player, mission] = ['SPY', -777]
                    elif self.spies_victories == 1:
                        if votes_down == 1:
                            self.identity_probability[player, mission] = ['SPY', -777]
                        else:
                            self.identity_probability[player, mission] = ['RESISTANCE', -777]
                    elif self.spies_victories == 2:
                        self.identity_probability[player, mission] = ['RESISTANCE', -777]
                elif self.resistance_victories == 2:
                    self.identity_probability[player, mission] = ['RESISTANCE', -777]
            elif self.sabotages == 1:
                if votes_down == 0:
                    if self.resistance_victories == 0:
                        if self.non_sabotages == 1:
                            self.identity_probability[player, mission] = ['RESISTANCE', -777]
                        else:
                            self.identity_probability[player, mission] = ['SPY', -777]
                    elif self.resistance_victories == 1:
                        self.identity_probability[player, mission] = ['SPY', -777]
                    elif self.resistance_victories == 2:
                        self.identity_probability[player, mission] = ['SPY', -777]
                elif votes_down == 1:
                    if self.resistance_victories == 0:
                        self.identity_probability[player, mission] = ['RESISTANCE', -777]
                    elif self.resistance_victories == 1:
                        self.identity_probability[player, mission] = ['SPY', -777]
                    elif self.resistance_victories == 2:
                        if self.non_sabotages == 1:
                            self.identity_probability[player, mission] = ['RESISTANCE', -777]
                        else:
                            self.identity_probability[player, mission] = ['SPY', -777]
                elif votes_down == 2:
                    if self.non_sabotages == 0:
                        self.identity_probability[player, mission] = ['RESISTANCE', -777]
                    elif self.non_sabotages == 1:
                        self.identity_probability[player, mission] = ['SPY', -777]
                    elif self.non_sabotages == 2:
                        if self.resistance_victories == 0:
                            self.identity_probability[player, mission] = ['SPY', -777]
                        else:
                            self.identity_probability[player, mission] = ['RESISTANCE', -777]
                    elif self.non_sabotages == 3:
                        self.identity_probability[player, mission] = ['RESISTANCE', -777]
                elif votes_down == 3:
                    if self.resistance_victories == 0:
                        self.identity_probability[player, mission] = ['SPY', -777]
                    else:
                        self.identity_probability[player, mission] = ['RESISTANCE', -777]
                elif votes_down == 4:
                    self.identity_probability[player, mission] = ['SPY', -777]
                elif votes_down == 5:
                    self.identity_probability[player, mission] = ['SPY', -777]
            elif self.sabotages == 2:
                self.identity_probability[player, mission] = ['SPY', -777]
        elif votes_up == 3:
            if self.sabotages == 0:
                if self.resistance_victories == 0:
                    self.identity_probability[player, mission] = ['RESISTANCE', -777]
                elif self.resistance_victories == 1:
                    if votes_down == 0:
                        if self.spies_victories == 2:
                            self.identity_probability[player, mission] = ['RESISTANCE', -777]
                        else:
                            self.identity_probability[player, mission] = ['SPY', -777]
                    elif votes_down == 1:
                        if self.spies_victories == 2:
                            self.identity_probability[player, mission] = ['RESISTANCE', -777]
                        else:
                            self.identity_probability[player, mission] = ['SPY', -777]
                    elif votes_down == 2:
                        self.identity_probability[player, mission] = ['RESISTANCE', -777]
                    elif votes_down == 3:
                        self.identity_probability[player, mission] = ['RESISTANCE', -777]
                    elif votes_down == 4:
                        self.identity_probability[player, mission] = ['RESISTANCE', -777]
                    elif votes_down == 5:
                        self.identity_probability[player, mission] = ['RESISTANCE', -777]
                elif self.resistance_victories == 2:
                    self.identity_probability[player, mission] = ['RESISTANCE', -777]
            elif self.sabotages == 1:
                if votes_down == 0:
                    if self.resistance_victories == 0:
                        self.identity_probability[player, mission] = ['RESISTANCE', -777]
                    else:
                        self.identity_probability[player, mission] = ['SPY', -777]
                elif votes_down == 1:
                    if self.resistance_victories == 0:
                        self.identity_probability[player, mission] = ['RESISTANCE', -777]
                    elif self.resistance_victories == 1:
                        if self.spies_victories == 1:
                            self.identity_probability[player, mission] = ['RESISTANCE', -777]
                        else:
                            self.identity_probability[player, mission] = ['SPY', -777]
                    elif self.resistance_victories == 2:
                        self.identity_probability[player, mission] = ['SPY', -777]
                elif votes_down == 2:
                    if self.non_sabotages == 0:
                        self.identity_probability[player, mission] = ['RESISTANCE', -777]
                    elif self.non_sabotages == 1:
                        if self.spies_victories == 2:
                            self.identity_probability[player, mission] = ['RESISTANCE', -777]
                        else:
                            self.identity_probability[player, mission] = ['SPY', -777]
                    elif self.non_sabotages == 2:
                        self.identity_probability[player, mission] = ['RESISTANCE', -777]
                    elif self.non_sabotages == 3:
                        self.identity_probability[player, mission] = ['RESISTANCE', -777]
                elif votes_down == 3:
                    self.identity_probability[player, mission] = ['SPY', -777]
                elif votes_down == 4:
                    self.identity_probability[player, mission] = ['SPY', -777]
                elif votes_down == 5:
                    self.identity_probability[player, mission] = ['SPY', -777]
            elif self.sabotages == 2:
                if self.resistance_victories == 0:
                    if votes_down == 2:
                        self.identity_probability[player, mission] = ['SPY', -777]
                    else:
                        self.identity_probability[player, mission] = ['RESISTANCE', -777]
                elif self.resistance_victories == 1:
                    self.identity_probability[player, mission] = ['SPY', -777]
                elif self.resistance_victories == 2:
                    self.identity_probability[player, mission] = ['SPY', -777]
        elif votes_up == 4:
            if self.resistance_victories == 0:
                self.identity_probability[player, mission] = ['RESISTANCE', -777]
            elif self.resistance_victories == 1:
                if self.spies_victories == 0:
                    self.identity_probability[player, mission] = ['SPY', -777]
                elif self.spies_victories == 1:
                    if votes_down == 0:
                        self.identity_probability[player, mission] = ['RESISTANCE', -777]
                    else:
                        self.identity_probability[player, mission] = ['SPY', -777]
                elif self.spies_victories == 2:
                    if self.sabotages == 0:
                        self.identity_probability[player, mission] = ['RESISTANCE', -777]
                    else:
                        self.identity_probability[player, mission] = ['SPY', -777]
            elif self.resistance_victories == 2:
                if self.sabotages == 0:
                    self.identity_probability[player, mission] = ['RESISTANCE', -777]
                elif self.sabotages == 1:
                    if votes_down == 0:
                        self.identity_probability[player, mission] = ['RESISTANCE', -777]
                    elif votes_down == 1:
                        if self.spies_victories == 1:
                            self.identity_probability[player, mission] = ['RESISTANCE', -777]
                        else:
                            self.identity_probability[player, mission] = ['SPY', -777]
                    elif votes_down == 2:
                        self.identity_probability[player, mission] = ['SPY', -777]
                    elif votes_down == 3:
                        self.identity_probability[player, mission] = ['SPY', -777]
                    elif votes_down == 4:
                        self.identity_probability[player, mission] = ['SPY', -777]
                    elif votes_down == 5:
                        self.identity_probability[player, mission] = ['SPY', -777]
                elif self.sabotages == 2:
                    self.identity_probability[player, mission] = ['SPY', -777]
        elif votes_up == 5:
            if self.sabotages == 0:
                if self.spies_victories == 0:
                    self.identity_probability[player, mission] = ['SPY', -777]
                else:
                    self.identity_probability[player, mission] = ['RESISTANCE', -777]
            elif self.sabotages == 1:
                if self.spies_victories == 0:
                    self.identity_probability[player, mission] = ['SPY', -777]
                elif self.spies_victories == 1:
                    if self.resistance_victories == 1:
                        self.identity_probability[player, mission] = ['RESISTANCE', -777]
                    else:
                        self.identity_probability[player, mission] = ['SPY', -777]
                elif self.spies_victories == 2:
                    if self.resistance_victories == 2:
                        self.identity_probability[player, mission] = ['RESISTANCE', -777]
                    else:
                        self.identity_probability[player, mission] = ['SPY', -777]
            elif self.sabotages == 2:
                self.identity_probability[player, mission] = ['SPY', -777]


    def writeIdentities(self, file, spies):
        exist = os.path.isfile("./"+file)
        f = open(file, "a")

        if exist != True:

            f.write('@relation \'Identity\'\n\n')
            f.write('@attribute spies_victories {0,1,2}\n')
            f.write('@attribute resistance_victories {0,1,2}\n')
            f.write('@attribute sabotages {0,1,2}\n')
            f.write('@attribute non_sabotages {0,1,2,3}\n')
            f.write('@attribute votes_up {0,1,2,3,4,5}\n')
            f.write('@attribute votes_down {0,1,2,3,4,5}\n')
            f.write('@attribute identity {RESISTANCE, SPY}\n\n')

            f.write('@data\n')

            keys = self.selected_team.keys()
            for x in range(len(self.selected_team)):
                # Spies victories
                f.write('%d,' % self.selected_team[keys[x]][0])
                # Resistance victories
                f.write('%d,' % self.selected_team[keys[x]][1])
                # Number of sabotages in a mision
                f.write('%d,' % self.selected_team[keys[x]][2])
                # Number of non sabotages in a mision
                f.write('%d,' % self.selected_team[keys[x]][3])
                # Number of votes UP
                f.write('%d,' % self.selected_team[keys[x]][4])
                # Number of votes DOWN
                f.write('%d,' % self.selected_team[keys[x]][5])

                # The class
                if keys[x][0] in spies:
                    f.write('SPY')
                else:
                    f.write('RESISTANCE')
                f.write('\n')

        else:
            keys = self.selected_team.keys()
            for x in range(len(self.selected_team)):
                    # Spies victories
                    f.write('%d,' % self.selected_team[keys[x]][0])
                    # Resistance victories
                    f.write('%d,' % self.selected_team[keys[x]][1])
                    # Number of sabotages in a mision
                    f.write('%d,' % self.selected_team[keys[x]][2])
                    # Number of non sabotages in a mision
                    f.write('%d,' % self.selected_team[keys[x]][3])
                    # Number of votes UP
                    f.write('%d,' % self.selected_team[keys[x]][4])
                    # Number of votes DOWN
                    f.write('%d,' % self.selected_team[keys[x]][5])

                    # The class
                    if keys[x][0] in spies:
                        f.write('SPY')
                    else:
                        f.write('RESISTANCE')
                    f.write('\n')
        f.close()

    def setNumSabotagesPerPlayer(self, player):
        if player in self.num_sabotages_per_player:
            self.num_sabotages_per_player[player] += 1
        else:
            self.num_sabotages_per_player[player] = 1

    def setWhenSabotage(self, mission, team):
        for i in range(len(team)):
            x = []
            x.append(self.spies_victories)
            x.append(self.resistance_victories)
            x.append(len(team))
            self.when_sabotage[team[i], mission] = x

    def calculateWhenSabotage(self, win, spies, sabotages_per_player):
        keys = self.when_sabotage.keys()
        for i in range(len(keys)):
            player = keys[i][0]
            mission = keys[i][1]
            if player in spies:
                #We only want to learn if the player won
                if win == False:
                    x = []
                    # Number of SPY victories
                    x.append(self.when_sabotage[keys[i]][0])
                    # Number of RESISTANCE victories
                    x.append(self.when_sabotage[keys[i]][1])
                    # Size of the team
                    x.append(self.when_sabotage[keys[i]][2])
                    # Number of spies in the team
                    num_spies_in_team = 0
                    for z in range(len(keys)):
                        if mission == keys[z][1]:
                            if keys[z][0] in spies:
                                num_spies_in_team += 1
                    x.append(num_spies_in_team)
                    # Previous sabotages of a specific player
                    key_s = sabotages_per_player.keys()
                    num_sabotages = 0
                    for z in range(len(key_s)):
                        if (player == key_s[z][0]) and (key_s[z][1] < mission):
                            num_sabotages += 1
                    x.append(num_sabotages)
                    # YES: if the player chose to sabotage, NO otherwise
                    if (player, mission) in sabotages_per_player:
                        x.append('YES')
                    else:
                        x.append('NO')
                    self.calculate_when_sabotage[keys[i]] = x

    def shouldIsabotaged(self, spies_in_team, size_team, player):
        if player in self.num_sabotages_per_player:
            num_sabotages = self.num_sabotages_per_player[player]
        else:
            num_sabotages = 0

        if (self.spies_victories == 1) and (spies_in_team == 2) and (size_team == 2) and (num_sabotages == 0): return 'NO'
        else: return 'YES'

    def writeSabotages(self, file):
        exist = os.path.isfile("./"+file)
        f = open(file, "a")

        if exist != True:

            f.write('@relation \'Sabotages\'\n\n')
            f.write('@attribute spies_victories {0,1,2}\n')
            f.write('@attribute resistance_victories {0,1,2}\n')
            f.write('@attribute size_team {2,3}\n')
            f.write('@attribute spies_in_team {1,2}\n')
            f.write('@attribute previous_sabotages {0,1,2}\n')
            f.write('@attribute sabotage {YES, NO}\n\n')

            f.write('@data\n')

            keys = self.calculate_when_sabotage.keys()
            for x in range(len(keys)):
                # Spies victories
                f.write('%d,' % self.calculate_when_sabotage[keys[x]][0])
                # Resistance victories
                f.write('%d,' % self.calculate_when_sabotage[keys[x]][1])
                # Size team
                f.write('%d,' % self.calculate_when_sabotage[keys[x]][2])
                # Number of spies in team
                f.write('%d,' % self.calculate_when_sabotage[keys[x]][3])
                # previous sabotages
                f.write('%d,' % self.calculate_when_sabotage[keys[x]][4])
                # If he sabotages o not
                f.write('%s' % self.calculate_when_sabotage[keys[x]][5])
                f.write('\n')
        else:
            keys = self.calculate_when_sabotage.keys()
            for x in range(len(keys)):
                # Spies victories
                f.write('%d,' % self.calculate_when_sabotage[keys[x]][0])
                # Resistance victories
                f.write('%d,' % self.calculate_when_sabotage[keys[x]][1])
                # Size team
                f.write('%d,' % self.calculate_when_sabotage[keys[x]][2])
                # Number of spies in team
                f.write('%d,' % self.calculate_when_sabotage[keys[x]][3])
                # previous sabotages
                f.write('%d,' % self.calculate_when_sabotage[keys[x]][4])
                # If he sabotages o not
                f.write('%s' % self.calculate_when_sabotage[keys[x]][5])
                f.write('\n')
        f.close()
