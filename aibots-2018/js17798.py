from player import Bot
import random
from sklearn import tree
from sklearn.model_selection import ShuffleSplit
from sklearn.model_selection import cross_val_score
import pandas as pd
import os
import itertools
from functools import reduce
import math
import graphviz
import pydot
import sys


# Render decision trees to dot files
create_graphs = False
# store data to csv files
remember_between_competitions = False
track_stats = False
# use rules when accuracy is down
use_rule_fallback = True
# use player modeling
use_player_modeling = True
# use decision trees for sabotaging and voting
with_decision_trees = False
# rebuild the decision trees every X games
split = int(sys.argv[1]) / 10

accuracy_min = .25


# determine the average of an array of integers or floats
def average(scores):
    return reduce(lambda x, y: x + y, scores) / len(scores)


# The base class for creating decision tree,
# offers an additional layer of abstraction in order to make it easy to update and rebuild trees
class DecisisionTree:
    def __init__(self, columns, name=""):
        self.version = 0
        self.columns = columns
        self.filename = "data/{}_training_data.csv".format(name)

        # Initialize the historical data
        self.data = pd.DataFrame(columns=columns)

        # Initialize the active data
        if os.path.exists(self.filename):
            self.new_data = pd.read_csv(self.filename, header=0, sep=",")
        else:
            self.new_data = pd.DataFrame(columns=columns)
        self.name = name

    def reset_new_data(self):
        # Reset the working data
        self.new_data = pd.DataFrame(columns=self.columns)

    # Update the classifiers
    def update_classifier(self, target, excluded_columns, existing_tree=False, existing_model=False):
        new_model, new_tree = self.build_classifier(self.new_data, target, excluded_columns)

        X, Y = self.determine_attribtues_and_classifier(self.data, target, excluded_columns)

        # compare the new model with the old model and keep the best one
        if existing_tree:
            cv = ShuffleSplit(n_splits=5)
            new_score = average(cross_val_score(new_model, X, Y, cv=cv))
            old_score = average(cross_val_score(existing_model, X, Y, cv=cv))
            if old_score >= new_score:
                self.version += 1
                return list(X), existing_model, existing_tree
        # create pretty pictures
        if create_graphs:
            tree.export_graphviz(
                new_tree,
                out_file="data/{}-{}-{}.dot".format(target, self.name, self.version),
                feature_names=list(X),
                class_names=["False", "True"],
                filled=True,
                rounded=True,
                special_characters=True,
                label='all',
                impurity=False,
                node_ids=False,
                proportion=True,
                rotate=True
            )
        # should the data be written to the filesystem for future use
        if remember_between_competitions:
            self.new_data.to_csv(
                self.filename,
                mode='w',
                index=False,
                header=True  # not os.path.exists(self.filename)
            )

        self.version += 1

        return list(X), new_model, new_tree

    def determine_attribtues_and_classifier(self, data, target, excluded_columns):
        X = data
        for column in list(data):
            if column in excluded_columns:
                X = X.drop(column, axis=1)

        return X, list(data[target].values)

    def build_classifier(self, data, target, excluded_columns):
        clf = tree.DecisionTreeClassifier(random_state=99, min_samples_split=20, min_samples_leaf=5, max_depth=5)

        X, Y = self.determine_attribtues_and_classifier(data, target, excluded_columns)

        return clf.fit(X, Y), clf

    # Add data record to the working memory
    def append(self, record):
        data = pd.DataFrame([record.to_array(columns=self.columns)], columns=self.columns)
        self.new_data = self.new_data.append(data)

    # retrieve the accuracy of a prediction
    def predict_proba(self, model, input_data, index=1):
        result = model.predict_proba([input_data])
        try:
            return result[0][index]
        except:
            pass

    # classify the input_data
    def predict(self, model, input_data):
        result = model.predict([input_data])
        return not not result[0]


# Decision Tree for resistance players
class GeneralResistanceDecisionTree(DecisisionTree):
    columns = ["turn", "tries", "wins", "losses", "is_leader", "in_team", "team_size", "spies_in_team", "team_suspicion", "leader_suspicion", "vote"]

    def __init__(self):
        DecisisionTree.__init__(self, GeneralResistanceDecisionTree.columns, 'resistance')

        self.vote_model = False
        self.vote_columns = []
        self.vote_tree = False

    def append(self, record):
        DecisisionTree.append(self, record)

    def update(self):
        if len(self.new_data) > 0:
            self.data = self.data.append(self.new_data)
            self.vote_columns, self.vote_model, self.vote_tree = self.update_classifier(
                "vote",
                ["vote"],
                self.vote_tree,
                self.vote_model
            )
            self.reset_new_data()

    def predict_vote(self, record):
        if not self.vote_model:
            return True, 1.0
        input_data = record.to_array(columns=self.vote_columns)
        return self.predict(self.vote_model, input_data), self.predict_proba(self.vote_model, input_data)


# Decision tree for all players (used for make assumptions for the team
class GeneralDecisionTree(DecisisionTree):
    columns = ["turn", "tries", "team_size", "team_suspicion", "leader_suspicion", "success", "sabotaged"]

    def __init__(self):
        DecisisionTree.__init__(self, GeneralDecisionTree.columns, 'general')

        self.success_model = False
        self.success_columns = []
        self.success_tree = False

        self.sabotage_model = False
        self.sabotage_columns = []
        self.sabotage_tree = False

    def append(self, record):
        DecisisionTree.append(self, record)

    def update(self):
        if len(self.new_data) > 0:
            self.data = self.data.append(self.new_data)
            self.success_columns, self.success_model, self.success_tree = self.update_classifier(
                "success",
                ["success", "sabotaged"],
                self.success_tree,
                self.success_model
            )
            self.sabotage_columns, self.sabotage_model, self.sabotage_tree = self.update_classifier(
                "sabotaged",
                ["sabotaged"],
                self.sabotage_tree,
                self.sabotage_model
            )
            self.reset_new_data()

    def predict_success(self, record):
        if not self.success_model:
            return True
        input_data = record.to_array(columns=self.success_columns)
        return self.predict(self.success_model, input_data), self.predict_proba(self.success_model, input_data)

    def determine_sabotage_probability(self, record, spy):
        if not self.sabotage_model:
            return 1.0
        input_data = record.to_array(columns=self.sabotage_columns)
        proba = self.predict_proba(self.sabotage_model, input_data)
        if spy:
            return 1-proba
        return proba


# General decision tree for spies
class GeneralSpyDecisionTree(DecisisionTree):
    columns = ["turn", "tries", "wins", "losses", "in_team", "is_leader", "team_size",
               "team_suspicion", "leader_suspicion", "spies_in_team", "sabotaged", "vote"]

    def __init__(self):
        DecisisionTree.__init__(self, GeneralSpyDecisionTree.columns, 'spy')

        self.vote_model = False
        self.vote_columns = []
        self.vote_tree = False

        self.sabotage_model = False
        self.sabotage_columns = []
        self.sabotage_tree = False

    def append(self, record):
        DecisisionTree.append(self, record)

    def update(self):
        if len(self.new_data) > 0:
            self.data = self.data.append(self.new_data)
            self.vote_columns, self.vote_model, self.vote_tree = self.update_classifier(
                "vote",
                [
                    "vote", "sabotaged"
                ],
                self.vote_tree,
                self.vote_model
            )
            self.sabotage_columns, self.sabotage_model, self.sabotage_tree = self.update_classifier(
                "sabotaged",
                [
                    "sabotaged", "vote"
                ],
                self.sabotage_tree,
                self.sabotage_model
            )
            self.reset_new_data()

    def predict_vote(self, record):
        if not self.vote_model:
            return True, 1.0
        input_data = record.to_array(columns=self.vote_columns)
        return self.predict(self.vote_model, input_data), self.predict_proba(self.vote_model, input_data)

    def predict_sabotage(self, record):
        if not self.sabotage_model:
            return True
        input_data = record.to_array(columns=self.sabotage_columns)
        return self.predict(self.sabotage_model, input_data), self.predict_proba(self.sabotage_model, input_data)


# Player specific decision tree
class PlayerResistanceDecisionTree(DecisisionTree):
    columns = ["turn", "tries", "wins", "losses", "up_votes", "down_votes", "failed_up_votes",
               "success_down_votes", "in_successful_team", "in_failed_team", "is_leader", "in_team", "team_size",
               "spies_in_team", "team_suspicion", "leader_suspicion", "vote"]

    def __init__(self, player_name):
        DecisisionTree.__init__(self, GeneralResistanceDecisionTree.columns, '{}-resistance'.format(player_name))

        self.vote_model = False
        self.vote_columns = []
        self.vote_tree = False

    def append(self, record):
        DecisisionTree.append(self, record)

    def update(self):
        if len(self.new_data) > 0:
            self.data = self.data.append(self.new_data)
            self.vote_columns, self.vote_model, self.vote_tree = self.update_classifier(
                "vote",
                ["vote"],
                self.vote_tree,
                self.vote_model
            )
            self.reset_new_data()

    def predict_vote(self, record):
        if not self.vote_model:
            return True, 1.0
        input_data = record.to_array(columns=self.vote_columns)
        return self.predict(self.vote_model, input_data), self.predict_proba(self.vote_model, input_data)


# Player spy decision tree
class PlayerSpyDecisionTree(DecisisionTree):
    columns = ["turn", "tries", "wins", "losses", "up_votes", "down_votes", "failed_up_votes",
               "success_down_votes", "in_successful_team", "in_failed_team", "in_team", "is_leader", "team_size",
               "team_suspicion", "leader_suspicion", "spies_in_team", "sabotaged", "vote"]

    def __init__(self, player_name):
        DecisisionTree.__init__(self, PlayerSpyDecisionTree.columns, "{}-spy".format(player_name))

        self.vote_model = False
        self.vote_columns = []
        self.vote_tree = False

        self.sabotage_model = False
        self.sabotage_columns = []
        self.sabotage_tree = False

    def append(self, record):
        DecisisionTree.append(self, record)

    def update(self):
        if len(self.new_data) > 0:
            self.data = self.data.append(self.new_data)
            self.vote_columns, self.vote_model, self.vote_tree = self.update_classifier(
                "vote",
                [
                    "vote", "sabotaged"
                ],
                self.vote_tree,
                self.vote_model
            )
            self.sabotage_columns, self.sabotage_model, self.sabotage_tree = self.update_classifier(
                "sabotaged",
                [
                    "sabotaged", "suspicion", "vote"
                ],
                self.sabotage_tree,
                self.sabotage_model
            )
            self.reset_new_data()

    def predict_vote(self, record):
        if not self.vote_model:
            return True, 1.0
        input_data = record.to_array(columns=self.vote_columns)
        return self.predict(self.vote_model, input_data), self.predict_proba(self.vote_model, input_data)

    def predict_sabotage(self, record):
        if not self.sabotage_model:
            return True
        input_data = record.to_array(columns=self.sabotage_columns)
        return self.predict(self.sabotage_model, input_data), self.predict_proba(self.sabotage_model, input_data)


# Manages all decision trees
class DecisionTreeManager:
    columns = ["player", "turn", "tries", "wins", "losses", "up_votes", "down_votes", "failed_up_votes",
               "success_down_votes", "in_successful_team", "in_failed_team", "in_team", "is_leader", "team_size",
               "suspicion", "team_suspicion", "leader_suspicion",
               "success", "sabotaged", "sabotages", "vote", "spies_in_team", "spy"]

    def __init__(self):
        self.players = []
        self.resistance_decision_tree = []
        self.spy_decision_tree = []
        self.record_count = 0
        # initialize general decision trees
        self.general_decision_tree = GeneralDecisionTree()
        self.general_resistance_decision_tree = GeneralResistanceDecisionTree()
        self.general_spy_decision_tree = GeneralSpyDecisionTree()

        # load training data
        self.general_decision_tree.update()
        self.general_resistance_decision_tree.update()
        self.general_spy_decision_tree.update()

    # add all players in the game, if they do not already exists (when competition is ran with more than 5 players)
    def add_players(self, players):
        for player in players:
            if not player.name in self.players:
                self.init_player(player.name)

    # Initialize a single player
    def init_player(self, name):
        self.players.append(name)
        if use_player_modeling:
            self.resistance_decision_tree.append(PlayerResistanceDecisionTree(name))
            self.spy_decision_tree.append(PlayerSpyDecisionTree(name))

    # check if there is a specific tree for a specific player
    def has_tree_for_player(self, player, spy, model):
        try:
            index = self.players.index(player.name)
            if index:
                if spy:
                    return getattr(self.spy_decision_tree[index], "{}_model".format(model))
                else:
                    return getattr(self.resistance_decision_tree[index], "{}_model".format(model))
        except ValueError:
            return False
        return False

    # Get the index of a player by name
    def get_player_index(self, name):
        return self.players.index(name)

    def append(self, data):
        players = []
        for record in data:
            index = self.get_player_index(record.player)
            players.append(index)
            self.general_decision_tree.append(record)
            if not record.spy:
                if use_player_modeling:
                    self.resistance_decision_tree[index].append(record)
                self.general_resistance_decision_tree.append(record)
            else:
                if use_player_modeling:
                    self.spy_decision_tree[index].append(record)
                self.general_spy_decision_tree.append(record)

        self.record_count += 1

        if (self.record_count < 1000 > split and self.record_count % 100 == 0) or self.record_count % split == 0:
            if use_player_modeling:
                for index in players:
                    self.resistance_decision_tree[index].update()
                    self.spy_decision_tree[index].update()
            self.general_spy_decision_tree.update()
            self.general_resistance_decision_tree.update()
            self.general_decision_tree.update()

    # decide how to vote based on the decision trees
    def decide_vote(self, record, spy, player=False):
        index = -1
        if player:
            try:
                index = self.players.index(player.name)
            except ValueError:
                index = -1

        if spy:
            if player and index >= 0 and self.has_tree_for_player(player, True, "vote"):
                return self.spy_decision_tree[index].predict_vote(record)
            return self.general_spy_decision_tree.predict_vote(record)

        if player and index >= 0 and self.has_tree_for_player(player, True, "vote"):
            return self.resistance_decision_tree[index].predict_vote(record)
        return self.general_resistance_decision_tree.predict_vote(record)

    # decide if to sabotage based on the decision tree
    def decide_sabotage(self, record, player=False):
        index = -1
        if player:
            index = self.players.index(player.name)
        if index >= 0 and self.has_tree_for_player(player, True, "sabotage"):
            return self.spy_decision_tree[index].predict_sabotage(record)

        return self.general_spy_decision_tree.predict_sabotage(record)


decision_tree = DecisionTreeManager()


# data for the game state
class DataRecord:
    def __init__(self, game, player=False, up_votes=0, down_votes=0, failed_up_votes=0, success_down_votes=0,
                 in_successful_team=0, in_failed_team=0, in_team=False, is_leader=False, team_size=0, suspicion=0.0,
                 team_suspicion=0.0, leader_suspicion=0.0, vote=False, spy=False, spies_in_team=0,
                 sabotages=0,
                 success=True, victory=False):
        self.player = player
        self.turn = game.turn
        self.tries = game.tries
        self.wins = game.wins
        self.losses = game.losses
        self.up_votes = up_votes
        self.down_votes = down_votes
        self.failed_up_votes = failed_up_votes
        self.success_down_votes = success_down_votes
        self.in_successful_team = in_successful_team
        self.in_failed_team = in_failed_team
        self.in_team = in_team
        self.is_leader = is_leader
        self.team_size = team_size
        self.suspicion = suspicion
        self.team_suspicion = team_suspicion
        self.leader_suspicion = leader_suspicion
        self.success = success
        self.vote = vote
        self.spy = spy
        self.spies_in_team = spies_in_team
        self.sabotages = sabotages
        self.sabotaged = sabotages > 0
        self.victory = victory

    # reduce data to only what is required for input of the decision tree
    def to_array(self, columns, player=-1):
        record = []
        for column in columns:
            try:
                if column == "player" and player > -1:
                    record.append(player)
                else:
                    record.append(getattr(self, column))
            except:
                continue
        return record


class GameRecord:
    def __init__(self, player, votes):
        self.player = player
        self.turn = player.game.turn
        self.tries = player.game.tries
        self.leader = player.game.leader
        self.team = player.game.team
        self.votes = votes
        self.success = True
        self.sabotages = 0
        self.sabotaged = False
        self.player_probability = []
        self.player_records = []
        self.player_sabotaged = False

    # Update the record when the mission completes
    def complete(self, sabotages):
        self.sabotages = sabotages
        for i in range(0, 5):
            participant = self.player.game.players[i]
            record = self.player.memory.gather_game_state(participant, self.team, self.leader)
            record.success = self.success
            record.sabotaged = self.sabotages > 0
            record.sabotages = self.sabotages
            self.player_probability.append(self.calc_probability(self.player.game.players[i], self.team, self.sabotages))

        self.record()

    # update the record when the mission fails
    def failed(self):
        self.success = False
        self.record()

    # Calculate the probability of a player being a spy
    def calc_probability(self, player, team, sabotages):
        team_size = len(self.team)
        in_team = player in team

        spy_1_in_team = sabotages >= 1
        spy_2_in_team = sabotages == 2

        if spy_1_in_team and (spy_2_in_team or self.player.spy):
            if in_team:
                return sabotages/team_size
            else:
                return 0.0
        elif spy_1_in_team:
            if in_team:
                return 1.0/team_size + (1.0/team_size)/4.0
            else:
                return 1.0/4.0
        else:
            return 1.0/5.0 + 1.0/4.0

    # Store flattened data
    def record(self):
        self.sabotaged = self.sabotages > 0
        for i in range(0, 5):
            participant = self.player.game.players[i]
            record = self.player.memory.gather_game_state(participant, self.team, self.leader)
            record.success = self.success
            record.sabotaged = self.sabotaged
            record.sabotages = self.sabotages
            self.player_records.append(record)

    # Flatten data to array and update with spy and victory result
    def to_array(self, spies, victory):
        records = []
        for i in range(0, 5):
            if i != self.player.index:
                record = self.player_records[i]
                record.vote = self.votes[i]
                record.victory = victory
                record.spy = len([p for p in spies if p.index == i]) > 0
                if record.spy:
                    record.spies_in_team = len([spy for spy in spies if spy in self.team])
                records.append(record)

        return records


# Memory class to calculate the state of the game
class GameMemory:
    def __init__(self, game, player, spies):
        self.records = []
        self.player = player
        self.game = game
        self.spies = spies

    # add a team to the memory
    def add_team(self, team):
        self.records.append(team)

    # get the last added team
    def last(self):
        return self.records[len(self.records) - 1]

    # determine the suspicion for a player
    def get_suspicion_for_player(self, player):
        probabilities = [r.player_probability[player.index] for r in self.records if r.success and len(r.player_probability) > player.index]

        # if no probabilities are known, fallback the the default probability of any player being a spy
        if len(probabilities) == 0:
            return 1.0 / 5.0 + 1.0 / 4.0

        return average(probabilities)

    # gather all information about the game into a single record
    def gather_game_state(self, player, team, leader):
        record = DataRecord(
            player=player.name,
            game=self.game,
            up_votes=self.get_up_votes(player.index),
            down_votes=self.get_down_votes(player.index),
            failed_up_votes=self.get_up_votes_for_failed_team(player.index),
            success_down_votes=self.get_down_votes_for_successful_team(player.index),
            in_successful_team=self.in_successful_team(player),
            in_failed_team=self.in_failed_team(player),
            in_team=player in team,
            is_leader=leader == player,
            team_size=len(team),
            spy=player in self.spies,
            spies_in_team=self.spies_in_team(team, player)
        )
        record.suspicion = self.get_suspicion_for_player(player)
        record.team_suspicion = self.get_team_suspicion(team, leader)
        record.leader_suspicion = self.get_suspicion_for_player(leader)
        return record

    # how many times has a player up voted
    def get_up_votes(self, index):
        return len([r for r in self.records if r.votes[index]])

    # how many times has a player down voted
    def get_down_votes(self, index):
        return len([r for r in self.records if not r.votes[index]])

    # how many time has a player up voted a team which sabotaged a mission
    def get_up_votes_for_failed_team(self, index):
        return len([r for r in self.records if r.votes[index and r.success and r.sabotaged]])

    # how many times has a player down voted a successful team
    def get_down_votes_for_successful_team(self, index):
        return len([r for r in self.records if not r.votes[index and r.success and not r.sabotaged]])

    # how many times has a player been in a successful team
    def in_successful_team(self, player):
        return len([r for r in self.records if r.success and not r.sabotaged and player in r.team])

    # how many times has a player been in a failed team
    def in_failed_team(self, player):
        return len([r for r in self.records if r.success and r.sabotaged and player in r.team])

    # are 2 team equal
    def teams_match(self, a, b):
        match = len(a) == len(b)
        for p in a:
            match = match and p in b
        return match

    # determine if the team has failed before during this turn
    def team_has_failed(self, turn, team):
        for r in self.records:
            if turn == r.turn and self.teams_match(team, r.team):
                return not r.success
        return False

    # check how many time a player went on a mission
    def in_teams(self, player):
        return len([r for r in self.records if r.success and player in r.team])

    # guess how many spies are the team
    def spies_in_team(self, team, player=False):
        if (not player and self.player.spy) or (player and player in self.spies):
            return len([p for p in team if p in self.spies])
        return len([p for p in team if self.spy_prediction(p)])

    # retrieve the other spy in the game
    def get_other_spy(self):
        for p in self.spies:
            if p != self.player:
                return p
        pass

    # get the suspicion of the team based on the max suspicion of all players
    def get_team_suspicion(self, team, leader):
        return float(len([player for player in team if self.spy_prediction(player)])/len(team))

    # determine the average suspicion for all players
    def get_average_player_suspicion(self):
        return average([self.get_suspicion_for_player(player) for player in self.player.game.players])

    # predict how likely a player is a spy
    def spy_prediction(self, player):
        # determine the average suspicion for all players
        average = self.get_average_player_suspicion()
        # determine the suspicion for the specific player
        player_suspicion = self.get_suspicion_for_player(player)
        return player_suspicion > average

    # flatten data
    def to_array(self, spies, victory):
        data = []
        for r in self.records:
            data.extend(r.to_array(spies, victory))
        return data


class Js17798(Bot):
    def select(self, players, count):
        # create all possible permutations of other team members
        if count - 1 == 1:
            combinations = self.others()
        else:
            combinations = itertools.combinations(self.others(), count - 1)

        # include self to all combinations
        teams = []
        for team in combinations:
            if count == 2:
                teams.append([team, self])
            else:
                teams.append([team[0], team[1], self])

        # Sort teams by their suspicion
        teams = sorted(teams, key=lambda t: self.determine_sabotage_probability(t))

        # Filter out teams the agent would not vote for
        filtered_teams = list(filter(lambda t: self.will_pass_vote(t), teams))
        if len(filtered_teams) > 0:
            teams = filtered_teams

        return teams[0]

    def determine_sabotage_probability(self, team):
        if with_decision_trees:
            # gather the game state
            game_state = self.memory.gather_game_state(self, team, self.game.leader)
            # how like it is this team will sabotage
            return decision_tree.general_decision_tree.determine_sabotage_probability(game_state, self.spy)
        return self.memory.get_team_suspicion(team, self.game.leader)

    # predict if the team will be allowed to go on the mission
    def will_pass_vote(self, team):
        votes = []
        # determine the vote for each palyer
        for player in self.game.players:
            probable_spy = self.memory.spy_prediction(player)
            if decision_tree.has_tree_for_player(player, probable_spy, "vote"):
                # gather the game state
                game_state = self.memory.gather_game_state(player, team, self.game.leader)
                # Predict the vote for this player
                vote, accuracy = decision_tree.decide_vote(game_state, probable_spy, player)
                votes.append(vote)
        if len(votes) == len(self.game.players):
            # do up votes outway downvotes
            return len([vote for vote in votes if vote]) > len([vote for vote in votes if not vote])

        # Fallback when votes could not be predicted for all players
        game_state = self.memory.gather_game_state(self, team, self.game.leader)
        return decision_tree.decide_vote(game_state, self.spy)

    def vote(self, team):
        vote_accuracy = 0.5
        vote = True
        if with_decision_trees:
            # gather the game state
            game_state = self.memory.gather_game_state(self, team, self.game.leader)
            # determine the vote
            vote, vote_accuracy = decision_tree.decide_vote(game_state, self.spy)

        # use the rule fallback when uncertain
        if not with_decision_trees or (accuracy_min < vote_accuracy < (1-accuracy_min) and use_rule_fallback):
            if self.game.tries == 5:
                return not self.spy

            if self == self.game.leader:
                return True

            if not self.spy and len(team) == 3 and self not in team:
                return False

            if self.spy and self.memory.spies_in_team(team) == 0:
                return False

            own_team = self.select(self.game.players, len(team))
            own_team_suspicion = self.memory.get_team_suspicion(own_team, self.game.leader)
            return own_team_suspicion <= self.memory.get_team_suspicion(team, self.game.leader)

        # return the vote
        return vote

    def sabotage(self):
        # slight optimization, no need to go through logic is player is not a spy
        if not self.spy:
            return False

        if not with_decision_trees:
            if self.game.wins == 2 or self.game.losses == 2:
                return True

            return not (self.memory.spies_in_team(self.game.team) > 1)

        # decide to sabotage
        sabotage = self.decide_sabotage(self)
        # only spy in the game?
        if self.memory.spies_in_team(self.game.team) == 1:
            return sabotage

        # predict how the other spy in the team will vote
        other_vote = self.decide_sabotage(self.memory.get_other_spy())

        # do not sabotage when the agent would sabotage, but ther spy is likely to sabotage as well
        if other_vote and sabotage:
            return False
        return sabotage

    def decide_sabotage(self, player):
        # gather the game state
        game_state = self.memory.gather_game_state(player, self.game.team, self.game.leader)

        if self == player:
            # determine sabotage and accuracy
            sabotage, accuracy = decision_tree.decide_sabotage(game_state)
        else:
            # determine sabotage and accuracy
            sabotage, accuracy = decision_tree.decide_sabotage(game_state, player)

        # use the rule fallback when uncertain
        if (accuracy_min < accuracy < (1-accuracy_min) and use_rule_fallback):
            if self.game.wins == 2 or self.game.losses == 2:
                return True

            return not (self.memory.spies_in_team(self.game.team) > 1)
        return sabotage

    def onGameRevealed(self, players, spies):
        # add players to the decision trees
        decision_tree.add_players([p for p in players if p != self])
        # Initialize Blackboard
        self.memory = GameMemory(self.game, self, spies)

    def onVoteComplete(self, votes):
        # Add votes to the blackboard
        self.memory.add_team(GameRecord(self, votes))

    def onMissionFailed(self, leader, team):
        # Flag the last try as failed
        self.memory.last().failed()

    def onMissionComplete(self, sabotaged):
        # Flag the last try as successful
        self.memory.last().complete(sabotaged)

    def onGameComplete(self, win, spies):
        # Push the data of the game to the decision tree
        decision_tree.append(self.memory.to_array(spies, win))
