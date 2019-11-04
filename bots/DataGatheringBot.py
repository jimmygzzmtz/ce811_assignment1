import logging
import logging.handlers

import core
import random

import csv

from player import Bot

class DataGatheringBot(Bot):
    """This is the base class for your AI in THE RESISTANCE.  To get started:
         1) Derive this class from a new file that will contain your AI.  See
            bots.py for simple stock AI examples.

         2) Implement mandatory API functions below; you must re-implement
            those that raise exceptions (i.e. vote, select, sabotage).

         3) If you need any of the optional callback API functions, implement
            them (i.e. all functions named on*() are callbacks).

       Aside from parameters passed as arguments to the functions below, you 
       can also access the game state via the self.game variable, which contains
       a State class defined in game.py.

       For debugging, it's recommended you use the self.log variable, which
       contains a python logging object on which you can call .info() .debug()
       or warn() for instance.  The output is stored in a file in the #/logs/
       folder, named according to your bot. 
    """

    __metaclass__ = core.Observable

    """Version 0.0.1"""
    
    def onGameRevealed(self, players, spies):
        """This function will be called to list all the players, and if you're
        a spy, the spies too -- including others and yourself.
        @param players  List of all players in the game including you.
        @param spies    List of players that are spies, or an empty list.
        """
        #name, votes, role
        #self.trainingData = [['name',[],[],0],['name',[],[],0],['name',[],[],0],['name',[],[],0],['name',[],[],0]]
        self.trainingData = []
        self.players = players
        #example: ['RandomBot',[['Leader',['TeamMember1','TeamMember2',etc],Mission,Round,Sabotaged,Vote],...],[[['TeamMember1','TeamMember2',etc],Mission,Round,Sabotaged,Vote],...],Spy]

        #names = [str(player)[2:] for player in players]

        #print(str(players[0])[2:])

        for i in range(0, len(players)):
            #print(str(players[i])[2:])
            #name, then per mission: leader, member, completed, vote, sabotaged, then at the end: spy
            playerTemplate = [str(players[i])[2:],'leader11','member111','member211','member311','member411','member511',-1,-1,-1,'leader12','member112','member212','member312','member412','member512',-1,-1,-1,'leader13','member113','member213','member313','member413','member513',-1,-1,-1,'leader14','member114','member214','member314','member414','member514',-1,-1,-1,'leader15','member115','member215','member315','member415','member515',-1,-1,-1,'leader21','member121','member221','member321','member421','member521',-1,-1,-1,'leader22','member122','member222','member322','member422','member522',-1,-1,-1,'leader23','member123','member223','member323','member423','member523',-1,-1,-1,'leader24','member124','member224','member324','member424','member524',-1,-1,-1,'leader25','member125','member225','member325','member425','member525',-1,-1,-1,'leader31','member131','member231','member331','member431','member531',-1,-1,-1,'leader32','member132','member232','member332','member432','member532',-1,-1,-1,'leader33','member133','member233','member333','member433','member533',-1,-1,-1,'leader34','member134','member234','member334','member434','member534',-1,-1,-1,'leader35','member135','member235','member335','member435','member535',-1,-1,-1,'leader41','member141','member241','member341','member441','member541',-1,-1,-1,'leader42','member142','member242','member342','member442','member542',-1,-1,-1,'leader43','member143','member243','member343','member443','member543',-1,-1,-1,'leader44','member144','member244','member344','member444','member544',-1,-1,-1,'leader45','member145','member245','member345','member445','member545',-1,-1,-1,'leader51','member151','member251','member351','member451','member551',-1,-1,-1,'leader52','member152','member252','member352','member452','member552',-1,-1,-1,'leader53','member153','member253','member353','member453','member553',-1,-1,-1,'leader54','member154','member254','member354','member454','member554',-1,-1,-1,'leader55','member155','member255','member355','member455','member555',-1,-1,-1,0]
            self.trainingData.append(playerTemplate)
        
        #print(self.trainingData)

        pass

    def onMissionAttempt(self, mission, tries, leader):
        """Callback function when a new turn begins, before the
        players are selected.
        @param mission  Integer representing the mission number (1..5).
        @param tries    Integer count for its number of tries (1..5).
        @param leader   A Player representing who's in charge.
        """
        pass

    def select(self, players, count):
        """Pick a sub-group of players to go on the next mission.
        @param players  The list of all players in the game to pick from.
        @param count    The number of players you must now select.
        @return list    The players selected for the upcoming mission.
        """
        return random.sample(self.game.players, count)

    def onTeamSelected(self, leader, team):
        """Called immediately after the team is selected to go on a mission,
        and before the voting happens.
        @param leader   The leader in charge for this mission.
        @param team     The team that was selected by the current leader.
        """
        pass

    def vote(self, team):
        """Given a selected team, decide whether the mission should proceed.
        @param team      List of players with index and name. 
        @return bool     Answer Yes/No.
        """
        return random.choice([True, False])

    def onVoteComplete(self, votes):
        """Callback once the whole team has voted.
        @param votes        Boolean votes for each player (ordered).
        """

        pos = 1

        #do turn and tries - 1 first
        turn = self.game.turn - 1
        tries = self.game.tries - 1

        pos = pos + turn*45 + tries*9

        OriginalPos = pos
        
        for i in range(0, len(self.players)):
            pos = OriginalPos
            self.trainingData[i][pos] = str(self.game.leader)[2:]
            
            memberPos = pos + 1
            for j in range(0, len(self.game.team)):
                self.trainingData[i][memberPos + j] = str(self.game.team[j])[2:]

            #completed
            pos = pos + 6
            self.trainingData[i][pos] = 0

            #voted
            pos = pos + 2
            if(self.game.votes[i] == True):
                intVotes = 0
            else:
                intVotes = 1
            self.trainingData[i][pos] = intVotes

        pass

    def sabotage(self):
        """Decide what to do on the mission once it has been approved.  This
        function is only called if you're a spy, otherwise you have no choice.
        @return bool        Yes to shoot down a mission.
        """
        return random.choice([True, False])

    def onMissionComplete(self, sabotaged):
        """Callback once the players have been chosen.
        @param sabotaged    Integer how many times the mission was sabotaged.
        """

        #voteList = [str(self.game.leader)[2:],[str(player)[2:] for player in self.game.team],self.game.turn,self.game.tries,sabotaged,True]

        #find in votes the position that the converted string matches the name from trainingdata

        #turn = mission
        #tries = attempt

        pos = 1

        #do turn and tries - 1 first
        turn = self.game.turn - 1
        tries = self.game.tries - 1

        pos = pos + turn*45 + tries*9

        #print(self.game.turn)

        #print(self.trainingData[0][pos])

        OriginalPos = pos
        
        for i in range(0, len(self.players)):
            pos = OriginalPos
            self.trainingData[i][pos] = str(self.game.leader)[2:]
            
            memberPos = pos + 1
            for j in range(0, len(self.game.team)):
                self.trainingData[i][memberPos + j] = str(self.game.team[j])[2:]

            #completed
            pos = pos + 6
            self.trainingData[i][pos] = 1

            #sabotaged
            pos = pos + 1
            self.trainingData[i][pos] = sabotaged

            #voted
            pos = pos + 1
            if(self.game.votes[i] == True):
                intVotes = 0
            else:
                intVotes = 1
            self.trainingData[i][pos] = intVotes

        pass

    def onMissionFailed(self, leader, team):
        """Callback once a vote did not reach majority, failing the mission.
        @param leader       The player responsible for selection.
        @param team         The list of players chosen for the mission.
        """
        pass

    def announce(self):
        """Publicly state beliefs about the game's state by announcing spy
        probabilities for any combination of players in the game.  This is
        done after each mission completes, and takes the form of a mapping from
        player to float.  Not all players must be specified, and of course this
        can be innacurate!

        @return dict[Player, float]     Mapping of player to spy probability.
        """
        return {}

    def onAnnouncement(self, source, announcement):
        """Callback if another player decides to announce beliefs about the
        game.  This is passed as a potentially incomplete mapping from player
        to spy probability.

        @param source        Player making the announcement.
        @param announcement  Dictionnary mapping players to spy probabilities.
        """
        pass

    def say(self, message):
        """Helper function to print a message in the global game chat, visible
        by all the other players.

        @param message       String containing free-form text.
        """
        self.log.info(message)

    def onMessage(self, source, message):
        """Callback if another player sends a general free-form message to the
        channel.  This is passed in as a generic string that needs to be parsed.

        @param source        Player sending the message.
        @param announcement  Arbitrary string for the message sent.
        """
        pass

    def onGameComplete(self, win, spies):
        """Callback once the game is complete, and everything is revealed.
        @param win          Boolean true if the Resistance won.
        @param spies        List of only the spies in the game.
        """

        """
        for spy in spies:
            for i in range(0, len(self.players)):
                if(str(spy)[2:] == self.trainingData[i][0]):
                    self.trainingData[i][2] = 1


        #print(self.trainingData)

        with open("dataGatheringOutput.csv", "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerows(self.trainingData)
        """

        #print(self.trainingData[0][226])

        for spy in spies:
            for i in range(0, len(self.players)):
                if(str(spy)[2:] == self.trainingData[i][0]):
                    self.trainingData[i][226] = 1
        
        labels = [['player','leader11','member111','member211','member311','member411','member511','completed','sabotaged','vote','leader12','member112','member212','member312','member412','member512','completed','sabotaged','vote','leader13','member113','member213','member313','member413','member513','completed','sabotaged','vote','leader14','member114','member214','member314','member414','member514','completed','sabotaged','vote','leader15','member115','member215','member315','member415','member515','completed','sabotaged','vote','leader21','member121','member221','member321','member421','member521','completed','sabotaged','vote','leader22','member122','member222','member322','member422','member522','completed','sabotaged','vote','leader23','member123','member223','member323','member423','member523','completed','sabotaged','vote','leader24','member124','member224','member324','member424','member524','completed','sabotaged','vote','leader25','member125','member225','member325','member425','member525','completed','sabotaged','vote','leader31','member131','member231','member331','member431','member531','completed','sabotaged','vote','leader32','member132','member232','member332','member432','member532','completed','sabotaged','vote','leader33','member133','member233','member333','member433','member533','completed','sabotaged','vote','leader34','member134','member234','member334','member434','member534','completed','sabotaged','vote','leader35','member135','member235','member335','member435','member535','completed','sabotaged','vote','leader41','member141','member241','member341','member441','member541','completed','sabotaged','vote','leader42','member142','member242','member342','member442','member542','completed','sabotaged','vote','leader43','member143','member243','member343','member443','member543','completed','sabotaged','vote','leader44','member144','member244','member344','member444','member544','completed','sabotaged','vote','leader45','member145','member245','member345','member445','member545','completed','sabotaged','vote','leader51','member151','member251','member351','member451','member551','completed','sabotaged','vote','leader52','member152','member252','member352','member452','member552','completed','sabotaged','vote','leader53','member153','member253','member353','member453','member553','completed','sabotaged','vote','leader54','member154','member254','member354','member454','member554','completed','sabotaged','vote','leader55','member155','member255','member355','member455','member555','completed','sabotaged','vote','spy']]

        #writableList = labels + self.trainingData
        #print(writableList)

        writableList = labels + self.trainingData

        with open("dataGatheringOutput.csv", "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerows(writableList)

        pass

    def others(self):
        """Helper function to list players in the game that are not your bot."""
        return [p for p in self.game.players if p != self]

    def __init__(self, game, index, spy):
        """Constructor called before a game starts.  It's recommended you don't
        override this function and instead use onGameRevealed() to perform
        setup for your AI.
        @param game     the current game state
        @param index    Your own index in the player list.
        @param spy      Are you supposed to play as a spy?
        """
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
        """Built-in function to support pretty-printing."""
        type = {True: "SPY", False: "RST"}
        return "<%s #%i %s>" % (self.name, self.index, type[self.spy])