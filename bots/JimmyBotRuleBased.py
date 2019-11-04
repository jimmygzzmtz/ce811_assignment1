import logging
import logging.handlers

import core

from player import Bot

class JimmyBotRuleBased(Bot):

    __metaclass__ = core.Observable

    #variables used to keep track of suspicion on players
    players = []
    leaderSusp = 3
    teamMemberSusp = 2
    votedYesSusp = 1

    def onGameRevealed(self, players, spies):
        #used to give access to these values across the bot's functions
        self.players = players
        self.spies = spies

        #list of lists used to keep track of suspicion, being constantly sorted to save time, in the following format: id, susp
        self.suspicionsBlackboard = [[0,0],[1,0],[2,0],[3,0],[4,0]]
        self.suspicionsBlackboardSort = [[0,0],[1,0],[2,0],[3,0],[4,0]]

    def onMissionAttempt(self, mission, tries, leader):
        pass

    def select(self, players, count):
        #Values used to assign team members
        memberRes1 = -1
        memberRes2 = -1
        teamList = []

        if(self.spy):
            #find resistance member with the most suspicion (to throw the blame), save id and suspicion value
            memberRes1 = -1
            memberRes2 = -1

            for i in range(len(players) - 1, -1, -1):
                if(players[self.suspicionsBlackboardSort[i][0]] not in self.spies):
                    memberRes1 = self.suspicionsBlackboardSort[i][0]
                    break
            
            for i in range(len(players) - 1, -1, -1):
                if(players[self.suspicionsBlackboardSort[i][0]] not in self.spies and memberRes1 != self.suspicionsBlackboardSort[i][0]):
                    memberRes2 = self.suspicionsBlackboardSort[i][0]
                    break

            if(count == 2):
                teamList = [self,players[memberRes1]]
            if(count == 3):
                teamList = [self,players[memberRes1],players[memberRes2]]

            return teamList
        
        else:
            #include players with least suspicion

            memberRes1 = -1
            memberRes2 = -1

            for i in range(0, len(players)):
                if(players[self.suspicionsBlackboardSort[i][0]] != self):
                    memberRes1 = self.suspicionsBlackboardSort[i][0]
                    break
            
            for i in range(0, len(players)):
                if(players[self.suspicionsBlackboardSort[i][0]] != self and memberRes1 != self.suspicionsBlackboardSort[i][0]):
                    memberRes2 = self.suspicionsBlackboardSort[i][0]
                    break

            if(count == 2):
                teamList = [self,players[memberRes1]]
            if(count == 3):
                teamList = [self,players[memberRes1],players[memberRes2]]

            return teamList

    def onTeamSelected(self, leader, team):
        pass

    def vote(self, team):
        #always vote yes on the first turn
        if(self.game.turn == 1 and self.game.tries == 1):
            return True

        #always vote yes when leader
        if(self == self.game.leader):
            return True
        
        #if on last try and spy, return false, otherwise true
        if self.game.tries == 5:
            return self.spy

        #if there is a spy in the team, vote yes
        if(self.spy):
            for i in range(0, len(team)):
                if(team[i] in self.spies):
                    return True

            return False
        else:
            #if a team member is in top 3 or 2 of suspicions, and is bigger than 0, vote no
            for i in range(0, len(team)):
                if(team[i] in self.suspicionsBlackboardSort[((len(self.players)) - (len(team))):((len(self.players)) - 1)] and self.suspicionsBlackboard[i][1] != 0):
                    return False
                    
            return True

    def onVoteComplete(self, votes):
        pass

    def sabotage(self):
        #don't sabotage if only 2 in team, since it drastically increases supicion, otherwise do sabotage
        if(self.game.team == 2):
            return False

        return True 

    def onMissionComplete(self, sabotaged):
        #if there are spies on the mission, add suspicion points accordingly
        if(sabotaged != 0):
            for i in range(0, len(self.game.team)):
                self.suspicionsBlackboard[self.players.index(self.game.team[i])][1] += self.teamMemberSusp
            self.suspicionsBlackboard[self.players.index(self.game.leader)][1] += self.leaderSusp

            for i in range(0, len(self.game.votes)):
                if(self.game.votes[i] == True):
                    self.suspicionsBlackboard[i][1] += self.votedYesSusp
            
        self.suspicionsBlackboardSort = sorted(self.suspicionsBlackboard, key=lambda player: player[1])

    def onMissionFailed(self, leader, team):
        spyCheck = False

        #check if a spy, based on suspicion, was probably part of the team
        for i in range(0, len(team)):
                if(team[i] in self.suspicionsBlackboardSort[((len(self.players)) - (len(team))):((len(self.players)) - 1)] and self.suspicionsBlackboard[i][1] >= 5):
                    spyCheck = True
        
        #if there was probably a spy, add suspicion points accordingly
        if(spyCheck == True):
            self.suspicionsBlackboard[self.players.index(self.game.leader)][1] += self.leaderSusp

            for i in range(0, len(self.game.votes)):
                if(self.game.votes[i] == True):
                    self.suspicionsBlackboard[i][1] += self.votedYesSusp
            
        pass

    def announce(self):
        return {}

    def onAnnouncement(self, source, announcement):
        pass

    def say(self, message):
        self.log.info(message)

    def onMessage(self, source, message):
        pass

    def onGameComplete(self, win, spies):
        pass

    def others(self):
        return [p for p in self.game.players if p != self]

    def __init__(self, game, index, spy):
        super(Bot, self).__init__(self.__class__.__name__, index)

        self.game = game
        self.spy = spy

        self.log = logging.getLogger(self.name)
        if not self.log.handlers:
            try:
                output = logging.FileHandler(filename='logs/'+self.name+'.log')
                self.log.addHandler(output)
                self.log.setLevel(logging.DEBUG)
            except IOError:
                pass

    def __repr__(self):
        type = {True: "SPY", False: "RST"}
        return "<%s #%i %s>" % (self.name, self.index, type[self.spy])