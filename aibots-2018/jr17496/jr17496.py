from player import Bot
import pickle
from sklearn import tree
import random

class jr17496(Bot):
    #importing the decision tree classifier
    trained_tree = pickle.load(open("aibots-2018/jr17496/training_tree.p", "rb"))
    preparation_list_x = []
    preparation_list_y = []
    training_set_list_x = []
    training_set_list_y = []
    negative_votes = [0, 0, 0, 0, 0]

    other_players_temp = 0
    other_players = []
    other_players_spy_probability = dict()
    new_list = []
    new_list_end = []
    spy_chance = [0.5, 0.5, 0.5, 0.5]
    negative = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    counter = [0, 0, 0, 0, 0]
    probability_list = [0.5, 0.5, 0.5, 0.5]
    player_negative = dict()
    x = 0
    neg_count = 0
    total_sabotages = 0
    player_team_fails = dict()

    def onGameRevealed(self, players, spies):

        for i in range(0, len(self.others())):
            self.other_players_temp = str(self.others()[i])
            self.other_players_temp = self.other_players_temp[2:]
            self.other_players.append(self.other_players_temp)
            self.other_players_spy_probability[self.other_players[i]] = self.spy_chance[i]
        #saves the names of the spies
        self.spies = spies
        if self.spy:
            self.ressistance = [p for p in players if p not in self.spies]
            self.spies_if_im_spy = [p for p in players if p in self.spies]

        self.players = players
        self.player = []
        for i in range(0, len(self.players)):
            if self.players[i] not in self.player:
                self.players2 = str(self.players[i])
                self.players2 = self.players2[2:]
                self.player.append(self.players2)
                self.player_negative[self.player[i]] = self.x
                # SELF.PLAYER_NEGATIVE is a dictionary of players given 0 negative votes at start
                # SELF.PLAYER contains the list of players for the game that is being played

    def select(self, players, count):  #
        """If im a spy  """
        if (self.spy == True):
            return random.sample(self.spies_if_im_spy, 1) + random.sample(self.ressistance, count - 1)
        #if i am a ressistance player
        else:
            probabilityes = self.probability_list
            for i in range(0, len(self.players)):
                if self.players[i] == self:
                    index_self = i
                    # the probability list consists of 4 players probability as it is not necesary to keep track of our own probability
                    #the list has to be extended to 5 players to make the prediction
                    probabilityes = self.probability_list[index_self:] + [0] + self.probability_list[:index_self]
            self.temp_list = []
            selection_list = []
            for i in range(0, len(self.players)):
                self.temp_list.append(
                    self.trained_tree.predict([[self.negative[i], self.counter[i], probabilityes[i]]]))
            for i in range(0, len(self.temp_list)):
                #players who are classified as spies have a value of 1, so the if checks if that player is a spy
                # and if not it apends it to a list of possible players for the team
                if self.temp_list[i][0] == 0:
                    selection_list.append(self.players[i])
            selection_list = selection_list[:count - 1]
            if len(selection_list) >= count:
                return selection_list[:count - 1]
            else:
                #if not enough players were classified as ressistance this is a safety mechanic to stop the program from crashing
                return random.sample(self.game.players, count)

            selection_list[:] = []
            self.temp_list[:] = []


    def onTeamSelected(self, leader, team):
        self.selected_for_team_count = dict()
        self.team_member_name = []
        self.team_selected_with_numbers = team
        self.team_selected = team
        for i in range(0, len(self.team_selected)):
            list_preparation = str(self.team_selected[i])
            list_preparation = list_preparation[2:]
            self.new_list.append(list_preparation)
        self.team_selected = self.new_list
        for i in range(0, len(self.team_selected)):
            for j in range(0, len(self.player)):
                if self.team_selected[i] == self.player[j]:
                    self.counter[j] = self.counter[j] + 1
                    self.selected_for_team_count[self.team_selected[i]] = self.counter[j]
                    # DEFINE HOW MANY TIMES A PLAYER WAS SELECTED FOR A TEAM


    def vote(self, team):
        prediction = []
        probabilityes = self.probability_list
        #adds one element to the probability list
        for i in range(0, len(self.players)):
            if self.players[i] == self:
                index_self = i
                probabilityes = self.probability_list[index_self:] + [0] + self.probability_list[:index_self]

        current_team = team
        if (self.spy == True):
            # IF A SPY IS ON THE SELECTED TEAM FLAG UP = True
            flag = 0
            for i in range(0, len(self.spies_if_im_spy)):
                if (self.spies_if_im_spy[i] in current_team):
                    flag = 1
            if flag == 1:
                return True
            else:
                return random.choice([True, False])

        #if I am a ressistance player and the team leader, always return True
        else:
            if bool((self.game.leader == self) == True):
                return bool(self == self.game.leader)
            #if I am a ressistance player and not the leader predict for each player on the team is he a spy,
            #if a player is a spy a value of 1 is returned, so considering the sum of all players on the list it is possible to determen is there a spy on the mission
            else:
                for i in range(0, len(self.player)):
                    for j in range(0, len(self.team_selected)):
                        if (self.player[i] == self.team_selected[j]):
                            prediction.append(self.trained_tree.predict([[self.negative[i], self.counter[i], probabilityes[i]]]))
                if sum(prediction) > 0:
                    return False
                else:
                    return True

    def onVoteComplete(self, votes):

        self.votes = votes
        for i in range(0, len(self.votes)):
            if self.votes[i] == False:
                self.negative[i] = self.negative[i] + 1
                self.neg_count = self.neg_count + 1
            self.player_negative[self.player[i]] = self.negative[i]
            # COUNTING EACH PLAYERS NEGATIVE VOTES , and overall negative counts for the mission

    def sabotage(self):
        #never sabotage if the number of players on the mission is 2, the risk of being descovered is to high
            if len(self.game.team) == 2:
                    return False
            elif len(self.game.team) == 3:
                    # if number is smaller than 7 return False, it is a small percentage to make it harder to predict the behaviour of the bot
                selection_value = random.randint(1, 101)
                if (selection_value < 7):
                    return False
                else:
                    return True
        #if the number of players on the mission is higher than 3 always return False
            else:
                return True




    def onMissionComplete(self, sabotaged):
        self.sabotaged = dict()
        #total number of sabotages throughout the game
        self.total_sabotages = self.total_sabotages + sabotaged
        for i in range(0, len(self.team_selected)):
            self.sabotaged[self.team_selected[i]] = self.total_sabotages
            for j in range(0, len(self.other_players)):
                if self.team_selected[i] == self.other_players[j]:
                    #probability is calculated as the previous probability, +1/number of people on the team
                    temp_value = self.other_players_spy_probability[self.other_players[j]]
                    self.probability_list[j] = self.probability_list[j] + 1 / len(self.team_selected)
                    self.other_players_spy_probability[self.other_players[j]] = 1 / len(self.team_selected) + temp_value
        self.team_selected[:] = []

        # Number of sabotages while this player was on a mission


    def onGameComplete(self, win, spies):
        true_false_list_spies = [0, 0, 0, 0, 0]
        # list of spies at the end of a iteration
        self.spies_end_preparation = spies
        for i in range(0, len(self.players)):
            if self.players[i] in self.spies_end_preparation:
                true_false_list_spies[i] = 1
        self.spies_end_preparation = list(self.spies_end_preparation)
        for i in range(0, len(self.spies_end_preparation)):
            list_preparation = str(self.spies_end_preparation[i])
            list_preparation = list_preparation[2:]
            self.new_list_end.append(list_preparation)
        self.spies_end = self.new_list_end
        # which team won
        self.win = win
        # Player name without numbers
        self.player_names = self.player
        # Player name with numbers
        self.player_names_with_number = self.players
        # Total number of negative votes for each player
        self.negative_votes = self.player_negative
        for i in range(0, len(self.players)):
            if self.players[i] == self:
                index_self = i
        self.probability_list = self.probability_list[index_self:] + [0] + self.probability_list[:index_self]
        #saving the data acumulated
        saved_data = open('data_bots_ai.txt', 'a')
        for i in range(0, len(self.player_names)):
            Data = [self.negative_votes[self.player_names[i]], self.counter[i], self.probability_list[i],
                    true_false_list_spies[i]]
            Data = str(Data)
            Data = Data[:-1]
            Data = Data[1:]
            Data = Data + "\n"
            saved_data.write(Data)
        saved_data.close()
        for i in range(0, len(self.counter)):
            self.counter[i] = 0
        for i in range(0, len(self.probability_list)):
            self.probability_list[i] = 0
        self.negative = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.neg_count = 0
        self.other_players[:] = []
        self.spies_end[:] = []

