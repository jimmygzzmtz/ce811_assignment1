import random
import copy

from player import Bot

class lhfver(Bot):

    def onGameRevealed(self, players, spies):
        """ this method is called at the start of each game
            so is therefore used to make create the blackBoards for each player of each game
            no data is passed from game to game to try and learn trends
        """
        global player_list, otherspy


        player_list = []
        otherspy = None


        i = 0
        # if i am a spy i need to know who the other spies are
        if(self.spy):
            temp = copy.deepcopy(spies)
            spy1 = temp.pop()
            spy2 = temp.pop()

            if(spy1 != players[self.index]):
                otherspy = spy1
            else:
                otherspy = spy2

        # create a blackboard for every other player
        while(i < len(players)):
            if(i != self.index):
                player_list.append(BlackBoard(players[i], i))
            i+=1
        i = 0

        # if i am a spy i add the infomration about the other spy to their blackboard
        if(self.spy):
            while(i < len(player_list)):
                if (player_list[i].getName() == spy1 or player_list[i].getName() == spy2):
                    player_list[i].setSpy(True)
                i+=1
        i = 0

    def select(self, players, count):
        if (self.spy):  # this path for if I am a spy

            if(self.game.turn == 1 ):
                other = random.sample(self.others(), count - 1)
                while(other[0].name == other):
                    other = random.sample(self.others(), count -1)
                return (self, other[0])
            else: # if it is not the first turn
                rand = random.randrange(0,1)

                if(rand == 0):
                    return [self] + random.sample(self.others(), count -1)
                else:
                    templist = copy.deepcopy(self.game.players)
                    del templist[self.index]
                    del templist[otherspy.index]
                    return [otherspy] + random.sample(templist, count -1)

        else:  # this path for if i am not a spy
            if(self.game.turn == 1): # if the its mission one select me and one other player
                return [self] + random.sample(self.others(), count - 1)
            else:
                if(count == 2): # select me and the player that is least likely to be spyS
                    result = self.leastLikeyToBeSpies()
                    return (self, result[0].name)
                if(count == 3):# select me and 2 other players that are least likely to be spies
                    result = self.leastLikeyToBeSpies()
                    return (self, result[0].name, result[1].name)

    def vote(self, team):

        if (self.spy):  # this path for if I am a spy
            if(self.game.turn == 0):
                return True
            else:
                if(self.game.tries == 5):
                    return True
                if (self.name in team or otherspy in team):
                    return True
                else:
                    return False

        else:  # this path for if i am not a spy

            if (self.game.turn == 1):
                return True
            else:

                info = self.leastLikeyToBeSpies()
                if(False):
                    pass
                else:
                    if(self.game.tries == 4):
                        return True
                    if(info[3].name in team ):
                         return False
                    return True

    def onVoteComplete(self, votes):
        if(self.game.turn == 1): # if its the first round and someone rejects a team it increases there chance of being a spy.
            i = 0
            if (False in votes):
                while (i < len(votes)):
                    j = 0
                    if (votes[i] == False):
                        while (j < len(player_list)):
                            if (player_list[j].index == i):
                                self.addValueTo(player_list[j].name, 1)
                            j += 1
                    i += 1
        if (self.game.tries == 5):  ## if a player rejects a vote on the hammer round then they are a spy
            i = 0
            if(False in votes):
                while (i < len(votes)):
                    j = 0
                    if(votes[i] == False):
                        while(j < len(player_list)):
                           if(player_list[j].index == i):
                               self.addValueTo(player_list[j].name, 50)
                           j += 1
                    i += 1

    def onMissionFailed(self, leader, team):
        if(self.game.turn == 1 and False in self.game.votes):
            i = 0
            while (i < len(self.game.votes)):
                j = 0
                if (self.game.votes[i] == False):
                    while (j < len(player_list)):
                        if (player_list[j].index == i):
                            self.addValueTo(player_list[j].name, 2)
                        j += 1
                i += 1

    def sabotage(self):

        if(self.spy):
            if(self.game.turn == 1):
                return False
            else:
                if(len(self.game.team) == 3):
                    if (otherspy in self.game.team):
                        return False
                    else:
                        return True
                else:
                    if(self.game.wins == 2):
                        return True
                    else:
                        if(self.game.losses == 2):
                            return True
                        else:
                            if(otherspy in self.game.team):

                                return False
                            else:
                                return True
        else:
            return False

    def onMissionComplete(self, sabotaged):
        if(self.game.turn == 1):
            global teamOne, sabOne
            teamOne = copy.deepcopy(self.game.team)
            sabOne = sabotaged
        elif(self.game.turn == 2):
            global teamTwo, sabTwo
            teamTwo = copy.deepcopy(self.game.team)
            sabTwo = sabotaged
        elif(self.game.turn == 3):
            global teamThree, sabThree
            teamThree = copy.deepcopy(self.game.team)
            sabThree = sabotaged
        elif(self.game.turn == 4):
            global teamFour, sabFour
            teamFour = copy.deepcopy(self.game.team)
            sabFour = sabotaged

        if (sabotaged):


            ## adding to the knowledge about the players
            if(len(self.game.team) == 2):
                i = 0
                addedValue = 9 * sabotaged
                if(sabotaged == 2 and self.game.turn == 1):
                    addedValue = 100
                if(self in self.game.team and self.spy == False):

                    addedValue = 100

                while(i < len(player_list)):
                    if(player_list[i].name == self.game.team[0]):
                        self.addValueTo(player_list[i].name, addedValue)
                    if(player_list[i].name == self.game.team[1]):
                        self.addValueTo(player_list[i].name, addedValue)
                    i += 1
            else:
                i = 0
                addedValue = 6 * sabotaged
                if (self in self.game.team and self.spy == False):

                    addedValue = 9
                    if(sabotaged == 2):
                        addedValue = 100

                while (i < len(player_list)):
                    if (player_list[i].name == self.game.team[0]):
                        self.addValueTo(player_list[i].name, addedValue)
                    if (player_list[i].name == self.game.team[1]):
                        self.addValueTo(player_list[i].name, addedValue)
                    if (player_list[i].name == self.game.team[2]):
                        self.addValueTo(player_list[i].name, addedValue)
                    i += 1

    def onGameComplete(self, win, spies):
        # this bot has no need for this method as it only learns about what is happening this game
        del player_list[0]
        del player_list[0]
        del player_list[0]
        del player_list[0]


    def leastLikeyToBeSpies(self):

        res = copy.deepcopy(player_list)
        res.sort(key=lambda x: x.value)
        return res

    def addValueTo(self, name, num):

        i = 0
        while(i < len(player_list)):
            if(name == player_list[i].name):
                player_list[i].addValue(num)
                break
            i+=1

class BlackBoard:

    def __init__(self, name, index):
        self.name = name            # the name of the player
        self.index = index          # the index of the player
        self.spy = False            # a Bool value true if player is a spy & false if i am not a spy and it is not known if they are spy
        self.value = 0              # a number value used in calculations to work out if that player is a spy


    def addToTeam(self):
        self.numberOfTeams += 1

    def getName(self):
        return self.name

    def addValue(self, value):
        self.value += value

    def setSpy(self, bool):
        self.spy = bool

    def isSpy(self):
        return self.spy
