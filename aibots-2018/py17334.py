from player import Bot
import random

#Class to store bot data. (their trustworthiness and wether they're a spy)
class BotInformation(object):
    def __init__(self, bot):
        self.BotEntity = bot
        self.isSpy = False
        self.trustworthiness = 0
        # 0 is not spy      >0 means more likely spy

#Class to store data about the game which should not be in the bot's individual class
class WorldInformation(object):

    def __init__(self, bot):
        self.BotData = []

    #used to find all the other resistance bots if bot is a spy
    def FindAllResistanceBots(self):
        ListOfResistanceBots = []
        for Bot in self.BotData:
            if not Bot.isSpy: ListOfResistanceBots.append(Bot.BotEntity)
        return ListOfResistanceBots

    #used to find all spy bots if figures out during the game
    def FindAllSpyBots(self):
        ListOfSpyBots = []
        for Bot in self.BotData:
            if Bot.isSpy: ListOfSpyBots.append(Bot.BotEntity)
        return ListOfSpyBots

    #gets the player data
    def getPlayerData(self, BotEntity):
        for BotData in self.BotData:
            if BotData.BotEntity == BotEntity: return BotData

class py17334(Bot):

    #selects a team if team leader
    def select(self, players, count):

            #section used to find the most likely resistance bot using trustworthiness score
            Botlist = []
            Botindex = []
            LikelyResistanceBot = []

            for Eachbot in players:
                if Eachbot.index != self.index:
                    Botlist.append(self.WorldInfo.getPlayerData(Eachbot).trustworthiness)
                    Botindex.append(Eachbot)
                    LikelyResistanceScore = min(Botlist)
                    if self.WorldInfo.getPlayerData(Eachbot).trustworthiness == LikelyResistanceScore:
                        LikelyResistanceBot.append(Eachbot)

            # If i am a spy, pick myself and another resistance
            if self.spy == True:
                self.say("Picking myself and random player.")
                ResistanceList = []
                ResistanceList = self.WorldInfo.FindAllResistanceBots()
                if ResistanceList:
                    return [self] + random.sample(self.others(), count - 1)
                else:
                    return [self] + random.sample(ResistanceList, count- 1)

            else:
                if count == 2:
                    return [self] + random.sample(LikelyResistanceBot, count - 1)
                if count == 3: #mission with 3 people, pick self, likely resistance and next likely resistance)
                    return [self] + random.sample(self.others(), count - 1) #didnt finish this function

    def vote(self, team):
        # If i am a spy & leader, try and pass the mission
        if self.spy == True and self.game.leader:
            self.say("I vote PASS because i am in it")
            return True

        # If i am a resistance, vote PASS if there are no spies
        if self.spy == False:
            for Eachbot in self.game.team:
                 if self.WorldInfo.getPlayerData(Eachbot).isSpy == True:
                     return  False
                 else:
                     return  True

    #SPY ONLY CLASS ================================================================
    def sabotage(self):

        # bare faced liar tactic. (fail the first mission and blame the other person)
        randomNumber = range(0,4)
        if self.game.turn == 1 and randomNumber == 2:
            return True

        #last chance tactic (let the other spy fail the missions until, there are [resistance 2 PASS wins] or spy has at least[2 FAILS])
        if self.game.wins == 2 or self.game.losses == 2:
            return True

        # if there are only 2 people on team, do not sabotage
        if len(self.game.team) == 2 and self.game.turn == 1 and randomNumber != 2: return False
        if len(self.game.team) == 2 and self.game.turn == 3: return False
        return True

    #====================UTILITY FUNCTIONS BELOW====================================

    def onMissionComplete(self, sabotaged):

        # Looking at each rounds results for EACH BOT
        for EachBot in self.game.team:
            PlayerData = self.WorldInfo.getPlayerData(EachBot)

            # TURN 1 RESULTS =======================================================================
            if self.game.turn == 1:
                if sabotaged == 0:
                    PlayerData.trustworthiness += 1
                if sabotaged > 0 & self.spy == False: #for resistance, if there was sabotage in 2 man team other must be a spy.
                    for Bot in self.game.team: #for each bot in team that isnt me
                        if Bot.index != self.index:
                            self.WorldInfo.getPlayerData(Bot).isSpy = True
                            self.WorldInfo.getPlayerData(Bot).trustworthiness += 10

            # TURN 2 RESULTS =======================================================================
            if self.game.turn == 2:
                if sabotaged == 0:
                    PlayerData.trustworthiness += 0
                else:
                    for Bot in self.game.team: # for each bot in team that isnt me
                        if Bot.index != self.index:
                            self.WorldInfo.getPlayerData(Bot).trustworthiness += 5

            # TURN 3 RESULTS =======================================================================
            if self.game.turn == 3:
                if sabotaged == 0:
                    PlayerData.trustworthiness += 1
                if sabotaged > 0 & self.spy == False:
                    for Bot in self.game.team: #for each bot in team that isnt me
                        if Bot.index != self.index:
                            self.WorldInfo.getPlayerData(Bot).isSpy = True
                            self.WorldInfo.getPlayerData(Bot).trustworthiness += 10

            # TURN 4 RESULTS =======================================================================
            if self.game.turn == 4:
                if sabotaged == 0:
                    PlayerData.trustworthiness += 0
                else:
                    for Bot in self.game.team: # for each bot in team that isnt me
                        if Bot.index != self.index:
                            self.WorldInfo.getPlayerData(Bot).trustworthiness += 5

            # TURN 5 RESULTS =======================================================================
            if self.game.turn == 5:
                if sabotaged == 0:
                    PlayerData.trustworthiness += 0
                else:
                    for Bot in self.game.team: # for each bot in team that isnt me
                        if Bot.index != self.index:
                            self.WorldInfo.getPlayerData(Bot).trustworthiness += 5

# Set WorldInformation and Player data
    def onGameRevealed(self, players, spies):
        self.WorldInfo = WorldInformation(players[self.index])

        for EachBot in players:
            playerData = BotInformation(EachBot)
            if EachBot in spies:
                playerData.isSpy = True
            self.WorldInfo.BotData.append(playerData)

    def onVoteComplete(self, votes):
        # the type of bot that suspects people becuase they dont want the mission to go on
        for Bot, vote in zip(self.game.players, votes):
                if (vote == False):
                    self.say("You voted down! you must be a spy!")
                    self.WorldInfo.getPlayerData(Bot).trustworthiness += 1