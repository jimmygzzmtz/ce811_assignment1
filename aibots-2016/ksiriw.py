from player import Bot
from game import State
import random

class Ksiriw(Bot):
    
    def onGameRevealed(self,players,spies):
		'''
		Method used to initialize memory
		'''
        self.log.debug("GAME START")
        self.Memory=[]
        self.Wins=0
        for p in players:
            currentplayer=[p,"r",0,0,0]
            self.Memory.append(currentplayer)

        for s in spies:
            for p in self.Memory:
                if p[0]==s:
                    p[1]="s"
    
    def select(self, players, count):
        #self.say("Picking Players")
        selected=self.SortedPlayerCache()
		selected=selected[0:count]
        return selected

    def vote(self, team):
        #self.say("Voting Current Team")
        return self.RVoter(team)

    def sabotage(self):
        #self.log.debug("SabotageComplete")
        if self.game.turn==1:
            return False
        else:
            return True

    def SortedPlayerCache(self):
		#Method used to sort players using the memory and return said players to the required method.
        playercache=self.Memory
        sendcache=[]
        #Purely Successful Players
        tempcache=[]
        for p in playercache:
            if p[2]>0 and p[4]==0:
                tempcache.append(p)

        tempcache.sort(key=lambda tup:tup[2], reverse=True)
        for p in tempcache:
            sendcache.append(p[0])

        #Untested players
        tempcache=[]
        for p in playercache:
            if p[2]==0:
                tempcache.append(p)
        tempcache.sort(key=lambda tup:tup[2], reverse=True)
        for p in tempcache:
            sendcache.append(p[0])

        #Players with more success than failure
        tempcache=[]
        for p in playercache:
            if p[3]>p[4] and p[4]!=0:
                tempcache.append(p)
        tempcache.sort(key=lambda tup:tup[2], reverse=True)
        for p in tempcache:
            sendcache.append(p[0])

        #Players with equal success and failure
        tempcache=[]
        for p in playercache:
            if p[2]>0 and p[3]==p[4]:
                tempcache.append(p)
        tempcache.sort(key=lambda tup:tup[2], reverse=True)
        for p in tempcache:
            sendcache.append(p[0])

        #players with more failure than success
        tempcache=[]
        for p in playercache:
            if p[4]>p[3]:
                tempcache.append(p)
        tempcache.sort(key=lambda tup:tup[2], reverse=True)
        for p in tempcache:
            sendcache.append(p[0])

        return sendcache

    def RVoter(self, team):
		#Gets sorted list of players based on value and determines value of team composition before determines vote.
        if self.game.tries==5:
            return True
        sortedcache=self.SortedPlayerCache()

        teamsize=len(team)
        threshold=0

        if teamsize==2:
            threshold=3
            currentscore=0
            currentpos=1
            for p in sortedcache:
                for x in team:
                    if p==x:
                        currentscore=currentscore+currentpos
                currentpos+1
            if currentscore>threshold:
                return False
            else:
                return True

        if teamsize==3:
            threshold=6
            currentscore=0
            currentpos=1
            for p in sortedcache:
                for x in team:
                    if p==x:
                        currentscore=currentscore+currentpos
                currentpos+1
            if currentscore>threshold:
                return False
            else:
                return True

        if teamsize==4:
            threshold=10
            currentscore=0
            currentpos=1
            for p in sortedcache:
                for x in team:
                    if p==x:
                        currentscore=currentscore+currentpos
                currentpos+1
            if currentscore>threshold:
                return False
            else:
                return True
            

    def onMissionComplete(self, sabotaged):
		#Saves team from the most recent mission
        self.ShortMemory = self.game.team

    def onMissionAttempt(self, mission, tries, leader):
		#Updates memory based on the results of the previous mission
        if mission==1:
            return None
        if self.game.wins>self.Wins:
            for p in self.Memory:
                for l in self.ShortMemory:
                    if p[0]==l:
                        p[2]=p[2]+1
                        p[3]=p[3]+1
        else:
            for p in self.Memory:
                for l in self.ShortMemory:
                    if p[0]==l:
                        p[2]=p[2]+1
                        p[4]=p[4]+1
                        
        self.Wins=self.game.wins
