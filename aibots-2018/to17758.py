import copy

from player import Bot
import random
import arff
from sklearn import tree


class GameBlackboard:
    def __init__(self):
        self.arff_data = []
        self.games_played = 0
        self.player_stats = []


class To17758(Bot):
    game_blackboard = GameBlackboard()

    def __init__(self, game, index, spy):
        super(To17758, self).__init__(game, index, spy)

    def onGameRevealed(self, players, spies):
        self.spies = spies
        self.player_mission_results = {p.name: 0 for p in players}
        self.player_spy_chances = {p.name: 0. for p in players}
        self.game_stats = GameStats()
        self.game_stats.players = players
        self.game_blackboard.games_played += 1
        self.weka_export = False

    def onTeamSelected(self, leader, team):
        self.game_stats.leaders.append(leader)
        self.game_stats.teams.append(team)

    def select(self, players, count):
        if self.spy:
            return [self] + random.sample([p for p in self.others() if p not in self.spies], count - 1)
        else:
            if self.use_tree():
                sorted_players = sorted(self.player_spy_chances, key=self.player_spy_chances.get)
            else:
                sorted_players = sorted(self.player_mission_results, key=self.player_mission_results.get)

            selected_players = [self]
            i = 0
            while len(selected_players) != count:
                selected_players = selected_players + [p for p in self.others() if p.name == sorted_players[i]]
                i += 1
            return selected_players

    def use_tree(self):
        for player_stats in self.game_blackboard.player_stats:
            if player_stats.name in [p.name for p in self.game_stats.players] and player_stats.clf is None:
                return False

        return True

    def onVoteComplete(self, votes):
        self.game_stats.votes.append(votes)

    def vote(self, team):
        if self.game.leader == self:
            return True
        elif self.spy:
            return len([s for s in team if s in self.spies]) >= 1
        else:
            sorted_players = sorted(self.player_spy_chances, key=self.player_spy_chances.get)
            if len([p for p in team if p.name != self.name and (p.name == sorted_players[-1])]):
                return False
            else:
                return True

    def sabotage(self):
        # if it is the first round, choose randomly how to vote to throw other players of guard
        # does not seem to help...
        # if self.game.tries == 1:
        #     return bool(random.getrandbits(1))
        return True

    def onMissionComplete(self, sabotaged):
        if sabotaged > 0:
            for player in [p for p in self.game.team if p != self]:
                self.player_mission_results[player.name] = self.player_mission_results[player.name] + 1
            self.game_stats.results.append(0)  # sabotaged
        else:
            self.game_stats.results.append(1)  # completed
        self.turn_end()

    def onMissionFailed(self, leader, team):
        self.game_stats.results.append(2)  # failed
        self.turn_end()

    def turn_end(self):
        self.create_tree_data()
        for player_stats in self.game_blackboard.player_stats:
            # predict whether player is spy if enough data is provided
            if player_stats.name in [p.name for p in self.game_stats.players] and player_stats.clf is not None:
                current_game_stats = list(filter(lambda p: p.name == player_stats.name, self.game_stats.player_stats))[0]
                probably_is_spy = player_stats.clf.predict([current_game_stats.tree_data[-1]])[0]
                if probably_is_spy:
                    current_game_stats.spy_chance_total += 1.0
                    self.player_spy_chances[current_game_stats.name] = (current_game_stats.spy_chance_total / (self.game.turn + self.game.tries - 1))

    def onGameComplete(self, win, spies):
        self.game_stats.spies = spies
        self.game_stats.resistance_won = win
        self.create_results_player()

        for ps in self.game_stats.player_stats:
            player_stats = list(filter(lambda p: p.name == ps.name, self.game_blackboard.player_stats))
            if len(player_stats) > 0:
                player_stats[0].arff_data.extend(ps.arff_data)
                player_stats[0].tree_data.extend(ps.tree_data)
                player_stats[0].tree_results.extend(ps.tree_results)
            else:
                self.game_blackboard.player_stats.append(ps)

        self.update_spy_chances()

        if self.game_blackboard.games_played == 250 and self.weka_export:
            self.export_arff()

    # used for creating a file readable by weka
    def export_arff(self):
        for ps in self.game_blackboard.player_stats:
            file_name = "botResult " + ps.name
            arff.dump("botResult " + ps.name, ps.arff_data, relation=file_name, names=[
                "VotedUp", "IsLeader", "TeamSize", "MissionResult", "IsOnTeam", "Turn", "Try", "IsSpy"
            ])

    def create_results_player(self):
        for player_stats in self.game_stats.player_stats:
            is_spy = player_stats.name in [p.name for p in self.game_stats.spies]
            for data in player_stats.arff_data:
                data.append(is_spy)
                player_stats.tree_results.append(is_spy)

    def create_tree_data(self):
        turn_index = self.game.tries + self.game.turn - 2
        for i, player in enumerate(self.game_stats.players):
            tree_data = []
            tree_data.append(self.game_stats.votes[turn_index][i])
            tree_data.append(self.game_stats.leaders[turn_index] == player)
            tree_data.append(len(self.game_stats.teams[turn_index]))
            tree_data.append(self.game_stats.results[turn_index])
            tree_data.append(player in self.game_stats.teams[turn_index])
            tree_data.append(self.game.turn)
            tree_data.append(self.game.tries)
            player_stats = list(filter(lambda p: p.name == player.name, self.game_stats.player_stats))
            arff_array = copy.copy(tree_data)
            if len(player_stats) > 0:
                player_stats[0].arff_data.append(tree_data)
                player_stats[0].tree_data.append(arff_array)
            else:
                self.game_stats.player_stats.append(PlayerStats(player.name, tree_data, arff_array))

    # updates chances after each game
    def update_spy_chances(self):
        for player_stats in self.game_blackboard.player_stats:
            if len(player_stats.tree_results) > 20:
                clf = tree.DecisionTreeClassifier()
                player_stats.clf = clf.fit(player_stats.tree_data, player_stats.tree_results)


class GameStats:
    def __init__(self):
        self.players = []
        self.teams = []
        self.votes = []
        self.leaders = []
        self.spies = []
        self.results = []
        self.resistance_won = False
        self.player_stats = []

    def create_tree_data(self):
        pass


# this class is used both globally in the GameBlackboard and locally in the GameStats
class PlayerStats:
    def __init__(self, name, tree_data, arff_data):
        self.name = name
        self.tree_data = [tree_data]
        self.tree_results = []
        self.arff_data = [arff_data]
        self.clf = None
        # this is used only locally during a game
        self.spy_chance_total = 0

        # future tips
        # did they always vote to sabotage if they were on a mission
        # did they sabotage on the first round
        # did they behave differently on the last mission
