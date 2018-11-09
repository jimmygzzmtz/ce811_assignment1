from player import Bot
import os
import random
import csv
import pandas as pd
import graphviz
from sklearn.tree import DecisionTreeClassifier

class GlobalBlackboard(object):

    def __init__(self):
        self.player_stats = []
        self.decision_tree_classifier = None
        self.class_mapping = {"resistance": 0, "spy": 1}
        self.train_tree()

    def save_data(self, player_data):
        self.player_stats = player_data
        # For data collection purposes only.
        # self.save_player_stats_to_file()

    def save_player_stats_to_file(self):
        file = os.path.join(os.path.dirname(__file__), 'SD18621stats.csv')

        with open(file, "a", newline='') as file:
            wr = csv.writer(file)
            for stats in self.player_stats:
                wr.writerow(stats)

    def train_tree(self):
        file = os.path.join(os.path.dirname(__file__), 'SD18621stats.csv')

        # Read data from csv and turn it into a Pandas data frame
        data_frame = pd.read_csv(
            file,
            index_col=0)

        data_frame.drop_duplicates()

        # Slice data
        attr_names = list(data_frame.columns[:12])
        attributes = data_frame[attr_names]
        target = data_frame["Is_spy"]

        # Create decision tree with tuned parameters
        self.decision_tree_classifier = tree.DecisionTreeClassifier(criterion="entropy", max_depth=12,
                                                               min_samples_leaf=6, presort=True, random_state=0)

        print("Tree has been trained")
        self.decision_tree_classifier = self.decision_tree_classifier.fit(attributes, target)

        # Tree can be
        # os.environ["PATH"] += os.pathsep + "C:\\Users\\sgo_a\\Documents\\graphviz-2.38-1\\release\\bin"
        # tree_data = tree.export_graphviz(self.decision_tree_classifier, out_file=None)
        # graph = graphviz.Source(tree_data)
        # graph.view()

    def predict(self, features, get_probability=False):
        f = features[:12]
        f = [f]
        if self.decision_tree_classifier:
            return (self.decision_tree_classifier.predict_proba(f)[0][1]
                    if get_probability else self.decision_tree_classifier.predict(f)[0])
        else:
            return 0


class PlayerStatsBlackboard(object):

    def __init__(self):
        self.name = None
        self.is_spy = False
        self.number_of_failed_missions = 0  # How many failed missions the player participated in
        self.number_of_succeeded_missions = 0  # How many succeeded missions the player participated in
        self.leader_of_failed_missions = 0  # How many failed missions was the player the leader of
        self.leader_of_succeeded_missions = 0  # How many succeeded missions was the player the leader of
        self.voted_for_failed_missions = 0  # How many failed missions did the player vote for
        self.voted_for_succeeded_missions = 0  # How many succeeded missions did the player vote for
        self.downvoted_for_failed_missions = 0  # How many failed missions did the player downvote
        self.downvoted_for_succeeded_missions = 0  # How many succeeded missions did the player downvote
        self.downvoted_in_fifth_try = 0  # How many times did the player downvote a mission in the 5th try
        # The highest of the probabilities of a given player being a spy given the information from a mission:
        # number_of_sabotages_in_mission / number_of_players_in_team
        self.highest_spy_probability_index = 0.0
        # A dictionary that stores how many times that player was selected for a mission by this player
        # with its index as a key -> player_index: times_selected
        self.player_selection_count = {}
        # A dictionary that stores the number of times the player got selected for missions by other players
        # with the other player's index as a key -> player_index: times_selected
        self.selected_by_player = {}
        # Index telling player selection variety with the formula:
        # Nd / Nt, where Nd = number of different players selected, Nt = total number of players selected
        self.player_selection_variety = 0.0
        # Map from a player name to a number
        self.player_name_mapping = {"Suspicious": 1, "Logicalton": 2, "Bounder": 3, "Trickerton": 4,
                                    "Simpleton": 5, "SD18621": 6}

    def to_list(self):
        """
        Turns the data in the Blackboard into a list.
        :return: A list with the data from the class. The last element of the list is the outcome.
        """
        li = [self.number_of_failed_missions, self.player_name_mapping.get(self.name, 0),
              self.number_of_succeeded_missions, self.leader_of_failed_missions, self.leader_of_succeeded_missions,
              self.voted_for_failed_missions, self.voted_for_succeeded_missions, self.downvoted_for_failed_missions,
              self.downvoted_for_succeeded_missions, self.highest_spy_probability_index,
              self.player_selection_variety, max(self.player_selection_count.values(), default=0),
              max(self.selected_by_player, default=0)]
        if self.is_spy:
            li.append(1)
        else:
            li.append(0)

        return li

    def add_player_selection(self, player):
        """
        Adds a player to the player selection count.
        :param player: A player selected for the current team.
        """
        # Add player to dictionary.
        if player.index in self.player_selection_count.keys():
            self.player_selection_count[player.index] += 1
        else:
            self.player_selection_count[player.index] = 1

        # Update player selection variety
        different_players = len(self.player_selection_count)
        total_selections = sum(self.player_selection_count.values())
        self.player_selection_variety = float(different_players) / float(total_selections)

    def add_selected_by_player(self, player):
        """
        Adds a player to the selected by player count.
        :param player: A player that selected this player.
        """
        # Add player to dictionary.
        if player.index in self.selected_by_player.keys():
            self.selected_by_player[player.index] += 1
        else:
            self.selected_by_player[player.index] = 1


global_blackboard = GlobalBlackboard()


class SD18621(Bot):
    """
    AI Bot by Sergio Adrian de Leon Rivera for the Game AI November project.

    This bot uses a series of decision trees in the form of conditional statements
    to play the board game 'The Resistance'. It also uses a learned decision tree
    to calculate the probabilities of players being spies.
    """

    def onGameRevealed(self, players, spies):
        global global_blackboard
        self.votes_in_favor = []  # List of players who voted in favor of the current mission
        self.votes_against = []  # List of players who voted against the current mission
        self.current_team = []  # List of the players in the current team
        self.last_successful_team = []
        self.current_leader = None  # Current leader
        self.missions_succeeded = 0
        self.missions_failed = 0
        self.missions_total = 0
        self.player_stats_blackboard = {p.name: PlayerStatsBlackboard() for p in players}
        self.spies = []
        for name, stats in self.player_stats_blackboard.items():
            self.player_stats_blackboard[name].name = name
        if self.spy:
            self.spies = spies

    def select(self, players, count):
        team_list = []
        if self.spy:
            self.log.debug("Select(spy): ")
            # If the player is a spy, select the spy with the lowest spy probability
            team_list.append(self.least_suspicious_spy())
            count -= 1
            i = 0
            # Append random resistance players
            while count > 0 and i < len(players):
                if players[i] != self and players[i] not in self.spies and players[i] not in team_list:
                    team_list.append(players[i])
                    count -= 1
                i += 1
        else:
            self.log.debug("Select(resistance): ")
            # Use the last successful team, modifying it depending on the required count
            team_list = self.last_successful_team
            while len(team_list) > count:
                del team_list[-1]
            if len(team_list) < count:
                team_list.extend(self.least_suspicious_players(count - len(team_list), team_list))

        self.log.debug(team_list)
        return team_list

    def vote(self, team):
        if self.game.leader == self:
            self.log.debug("Vote for myself")
            return True
        if self.spy:
            # If there are spies in the team, flip a coin biased to vote true unless there is one more
            # mission to win/lose
            s = (p for p in team if p in self.spies)
            if len(list(s)) > 0:
                if self.missions_failed == 2 or self.missions_succeeded == 2:
                    return True
                return random.random() < 0.8
            # If the number of tries is 5, flip a coin biased to vote false
            if self.game.tries == 5:
                return random.random() < 0.3
            # If there are no spies in the team, flip a coin biased to vote false
            return random.random() < 0.2
        else:
            if self.game.tries == 5:
                return True
            for p in team:
                if p != self and global_blackboard.predict(self.player_stats_blackboard[p.name].to_list()):
                    self.log.debug("(resistance)" + p.name + " is a spy, voted false")
                    return False

            # Check whether leader is a spy, if not, return true
            return not bool(global_blackboard.predict(self.player_stats_blackboard[self.game.leader.name].to_list()))

    def sabotage(self):
        # If two missions have failed, sabotage to win game.
        # If two missions have succeeded, sabotage not to lose.
        if self.missions_failed == 2 or self.missions_succeeded == 2:
            return True
        spies_in_team = 0
        for p in self.current_team:
            if p != self and p in self.spies:
                spies_in_team += 1
        # If there is more than one spy in the team, it is risky to sabotage mission.
        # Never sabotage first mission and don't sabotage if there are only two players in the team.
        if spies_in_team > 0 or self.missions_total == 0 or len(self.current_team) <= 2:
            return False
        return True


    def onTeamSelected(self, leader, team):
        self.current_leader = leader
        self.current_team = team
        for p in team:
            self.player_stats_blackboard[p.name].add_selected_by_player(leader)
            self.player_stats_blackboard[leader.name].add_player_selection(p)


    def onVoteComplete(self, votes):
        self.votes_in_favor = []
        self.votes_against = []
        for p in self.game.players:
            if votes[p.index]:
                self.votes_in_favor.append(p)
            else:
                self.votes_against.append(p)


    def onMissionFailed(self, leader, team):
        if self.game.tries == 5:
            self.missions_total += 1
            self.missions_failed += 1
            for p in self.votes_against:
                self.player_stats_blackboard[p.name].downvoted_in_fifth_try += 1


    def onMissionComplete(self, sabotaged):
        # Record stats
        self.missions_total += 1
        spy_probability = float(sabotaged) / float(len(self.current_team))
        if sabotaged:
            self.missions_failed += 1
            for p in self.current_team:
                self.player_stats_blackboard[p.name].number_of_failed_missions += 1
                if spy_probability > self.player_stats_blackboard[p.name].highest_spy_probability_index:
                    self.player_stats_blackboard[p.name].highest_spy_probability_index = spy_probability

            for p in self.votes_in_favor:
                self.player_stats_blackboard[p.name].voted_for_failed_missions += 1

            for p in self.votes_against:
                self.player_stats_blackboard[p.name].downvoted_for_failed_missions += 1

            self.player_stats_blackboard[self.current_leader.name].leader_of_failed_missions += 1
        else:
            self.missions_succeeded += 1
            self.last_successful_team = self.current_team
            for p in self.current_team:
                self.player_stats_blackboard[p.name].number_of_succeeded_missions += 1

            for p in self.votes_in_favor:
                self.player_stats_blackboard[p.name].voted_for_succeeded_missions += 1

            for p in self.votes_against:
                self.player_stats_blackboard[p.name].downvoted_for_succeeded_missions += 1

            self.player_stats_blackboard[self.current_leader.name].leader_of_succeeded_missions += 1


    def onGameComplete(self, win, spies):
        for s in spies:
            self.player_stats_blackboard[s.name].is_spy = True
        player_stats_list = []
        for stats in self.player_stats_blackboard.values():
            player_stats_list.append(stats.to_list())
        global_blackboard.save_data(player_stats_list)


# Helper methods

    def least_suspicious_spy(self):
        # From the spies, get the one which has the least probability of being a spy
        least_suspicious_index = 0
        spies = list(self.spies)
        spy0 = spies[0]
        least_suspicious_prob = global_blackboard.predict(self.player_stats_blackboard[spy0.name].to_list(),
                                                          get_probability=True)
        for i, spy in enumerate(spies[1:]):
            suspicious_prob = global_blackboard.predict(self.player_stats_blackboard[spy.name].to_list(),
                                                        get_probability=True)
            if suspicious_prob < least_suspicious_prob:
                least_suspicious_prob = suspicious_prob
                least_suspicious_index = i

        return spies[least_suspicious_index]


    def least_suspicious_players(self, count, team_list):
        # Get the probability of players being spies for players that are not in the team
        players_not_in_team = [p for p in self.game.players if p not in team_list]
        probabilities = [global_blackboard.predict(self.player_stats_blackboard[p.name].to_list(),
                                                        get_probability=True)
                         for p in players_not_in_team]
        players_with_probabilities = list(zip(probabilities, players_not_in_team))
        # Sort according to probability
        players_with_probabilities.sort(key=lambda tup: tup[0])

        # Return the specified number of players, unzipping players_with_probabilities
        return list(list(zip(*players_with_probabilities))[1])[:count]

