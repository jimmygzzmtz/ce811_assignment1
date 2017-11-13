from player import Bot

import random

class cl17571(Bot):

    def onGameRevealed(self, players, spies):
        self.spies = spies

        self.selectednumber = 0
        self.camppoints = {}
        self.camppoints.clear()
        for player in players:
            self.camppoints[player] = 0.0
        self.camppointsorder = []

        self.Myvoteresult = True
        self.lastmissionresult = True
        self.playerslist = players
        self.voteresult = {}
        self.sabotageresult = 1
        self.missionlabel = False

        self.lastsabotage = 0
        self.currentteam = []
        self.lastteamlog = []
        self.lastwinlog = False
        self.currentwinstate = False

        spiescount = [[5, 2], [6, 2], [7, 3], [8, 3], [9, 3], [10, 4]]
        for playerscount, spiescounts in spiescount:
            if len(players) == playerscount :
                self.spycount = spiescounts

    def select(self, players, count):

        for role in players:
            if role == self:
                Myselectresult = [role]

        if self.spy:
            if self.game.turn == 1:
                Myselectresult += random.sample(self.others(), count - 1)
            else:
                p = 0
                for i in range(0, len(self.camppointsorder)):
                    if self.camppointsorder[i] == self:
                        p = i
                        break
                if p <= len(self.game.players)/2:
                    for i in range(0, len(self.camppointsorder)):
                        if self.camppointsorder[i] in self.spies and self.camppointsorder[i] != self:
                            Myselectresult.append(self.camppointsorder[i])
                            break
                    for i in range(0, len(self.camppointsorder)):
                        if self.camppointsorder[i] not in self.spies:
                            if len(Myselectresult)<count:
                                Myselectresult.append(self.camppointsorder[i])
                            else:
                                break
                else:
                    for i in range(0, len(self.camppointsorder)):
                        if len(Myselectresult)<count:
                            Myselectresult.append(self.camppointsorder[i])
                        else:
                            break
        else:
            if self.game.turn == 1:
                Myselectresult += random.sample(self.others(), count - 1)
            else:
                for i in range(0, len(self.camppointsorder)):
                    k = -i-1
                    if len(Myselectresult)<count:
                        if self.camppointsorder[k] != self:
                            Myselectresult.append(self.camppointsorder[k])
                    else:
                        break

        return tuple(Myselectresult)


    def vote(self, team):

        self.currentteam = team

        if self in team:
            if self.game.leader != self:
                self.selectednumber += 1

        if self.game.tries == 5:
            self.Myvoteresult = not self.spy

        if self.spy:
            if self == self.game.leader:
                self.Myvoteresult = True
            else:
                if self.game.turn == 1 and self.game.tries < 2:
                    self.Myvoteresult = bool(self in team)
                else:
                    for player in self.spies:
                        if player in team:
                            self.Myvoteresult = True
                        else:
                            self.Myvoteresult = False

        else:
            if self.game.turn == 1 and self.game.tries < 2:
                self.Myvoteresult = bool(self in team)
            else:
                for i in range(0, len(team)):
                    if self.camppointsorder[i] in team:
                        if self.camppointsorder[i] != self:
                            self.Myvoteresult = False
                        else:
                            self.Myvoteresult = True
                    else:
                        self.Myvoteresult = True

        return self.Myvoteresult

    def sabotage(self):

        if len(self.spies) >= 3:
            return True
        if self.game.wins == 2 or self.game.losses == 2:
            return True
        if self == self.game.leader:
            return True
        if self.selectednumber <= 1:
            for player in self.game.team:
                if player in self.spies and player != self:
                    return False
                else:
                    return True
        else:
            return True

    def onVoteComplete(self, votes):

        i = 0
        for p in self.game.players:
            self.voteresult[p] = votes[i]
            i += 1
        pass

    def onMissionComplete(self, sabotaged):

        self.missionlabel = True
        self.sabotageresult = sabotaged
        pass

    def onMissionFailed(self, leader, team):

        self.missionlabel = False
        pass

    def announce(self):

        I = (float(self.sabotageresult))/(len(self.game.team))
        I2 = (float(self.spycount - self.sabotageresult))/(len(self.game.players)-len(self.game.team))
        Inormal = (float(self.spycount)) / (len(self.game.players))

        if self.spy:
            ks = 1.0
        else:
            ks = -1.0
        if self.missionlabel:
            if self.sabotageresult != 0:
                self.currentwinstate = False
                for role in self.game.team:
                    self.camppoints[role] += I
                for role in self.game.players:
                    if self.voteresult[role] == True:
                        if role not in self.currentteam:
                            self.camppoints[role] = self.camppoints[role] + I2
                        else:
                            self.camppoints[role] = self.camppoints[role] + Inormal
                if self.game.turn !=1:
                    if self.currentwinstate == False and self.lastwinlog == True:
                        t = []
                        for role in self.currentteam:
                            if role not in self.lastteamlog:
                                t.append(role)
                        Lt = len(t) + 1
                        It = (float(self.sabotageresult))/Lt
                        for role in t:
                            self.camppoints[role] = self.camppoints[role] + It
                    if self.currentwinstate == False and self.lastwinlog == False:
                        t = []
                        for role in self.currentteam:
                            if role in self.lastteamlog:
                                t.append(role)
                        Lt = len(t) + 1
                        It = (float(self.sabotageresult)) / Lt
                        for role in t:
                            self.camppoints[role] = self.camppoints[role] + It

            else:
                self.currentwinstate = True
                if self.currentwinstate == True and self.lastwinlog == False:
                    t = []
                    for role in self.lastteamlog:
                        if role not in self.currentteam:
                            t.append(role)
                    Lt = len(t) + 1
                    It = (float(self.lastsabotage)) / Lt
                    for role in t:
                        self.camppoints[role] = self.camppoints[role] + It
            self.lastteamlog = self.currentteam
            self.lastwinlog = self.currentwinstate
            self.lastsabotage = self.sabotageresult

        if  self.game.turn == 1 and self.game.tries < 2:
            for role in self.game.players:
                if self.voteresult[role] == True and role not in self.currentteam:
                    self.camppoints[role] = self.camppoints[role] + Inormal
                else:
                    self.camppoints[role] = self.camppoints[role] - Inormal
        else:
            for role in self.game.players:
                if self.voteresult[role] == self.Myvoteresult:
                    self.camppoints[role] = self.camppoints[role] + Inormal * ks
                else:
                    self.camppoints[role] = self.camppoints[role] - Inormal * ks



        orderofcamp = sorted(self.camppoints.items(), key=lambda d:d[1], reverse=True)
        self.camppointsorder = []
        for key,value in orderofcamp:
            self.camppointsorder.append(key)
        pass