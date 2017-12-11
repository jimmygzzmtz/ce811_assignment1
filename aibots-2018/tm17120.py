
from player import Bot
from game import State
import random
import itertools

class REBot(Bot):



    #Keeps count of the games played
    gameCounter = 1
    # Initialize variables that need to be initialized once for all games

    # Dictionary mapping each bot encountered in games to an accumulated score
    evaluation_meter = {}

    #Convers Suspicion_meter dictionary to a Suspicion_meter list of tuples in ascending order, with or without self
    def suspicionMeterToSortedList(self,suspicion_meter,isSpy):

        # Create temporary list from Suspicion meter dictionary as a list of tuples
        current_suspicion_meter_list = suspicion_meter.items()

        #If I am Resistance, I don't need myself in the suspicion list, I know I am Resistance
        if isSpy is False:
            current_suspicion_meter_list = [suspicion_tuple for suspicion_tuple in current_suspicion_meter_list
                                         if suspicion_tuple[0] is not self.name]

        # Sort suspicion meter based on Suspicion metric in ascending order
        current_suspicion_meter_list = sorted(current_suspicion_meter_list, key=lambda suspicion: suspicion[1],
                                              reverse=True)

        return current_suspicion_meter_list

    def evaluationMeterToSortedList(self,evaluation_meter):

        # Create temporary list from Evaluation meter dictionary as a list of tuples
        current_evaluation_meter_list = evaluation_meter.items()

        #Get only the players in this game from Evaluation meter list that are not me
        current_evaluation_meter_list = [evaluation_tuple for evaluation_tuple in current_evaluation_meter_list
                                         if evaluation_tuple[0] in str(self.game.players) and
                                         evaluation_tuple[0] is not self.player_name]


        # Sort evaluation meter based on Evaluation metric in ascending order
        current_evaluation_meter_list = sorted(current_evaluation_meter_list, key=lambda evaluation: evaluation[1],
                                              reverse=True)

        return current_evaluation_meter_list

    def onGameRevealed(self, players, spies):

        # Initialize variables that need to be initialized every game
        self.number_each_bot_selected = {}
        self.number_each_bot_voted_for = {}
        self.selectionsMade = 0
        self.votesMade = 0
        self.isSpy = False
        self.firstSabotage = False

        # Agressive mode makes the bot more aggressive and is enabled if bot is losing
        self.agressive_mode = False

        self.log.debug("----------------------------------------\n")
        self.log.debug("GAME " + str(REBot.gameCounter) + "\n")
        self.log.debug("----------------------------------------\n")


        if REBot.gameCounter==1:

            self.log.debug("LOG: This is the first game!\n")
            REBot.gameCounter+=1

        else:


            REBot.gameCounter+=1

        self.log.debug("LOG: Players playing this game:\n")

        #List all players in the game
        for player in players:
            self.log.debug(str(player) + "\n")

        #self.log.debug("Other players: " + str(self.others()))

        self.log.debug("----------------------------------------\n")

        #Find out if Resistance or Spy
        if self in spies:
            self.isSpy = True
            self.log.debug("LOG: I am a SPY this game\n")
            self.log.debug("The spies are: " + str(spies) + "\n")
        elif self not in spies:
            self.log.debug("LOG: I am with the RESISTANCE this game\n")

        self.other_spies = [p for p in spies if p is not self]

        for player in self.others():

            # Remove index number and dash from player string (string characters index 0 and 1) to leave just
            # the player's name in order to not confuse the evaluation meter which persists through games
            self.player_name = str(player)[2:]

            #Initialize these variables for each player encountered in this game
            self.number_each_bot_selected[self.player_name] = 0
            self.number_each_bot_voted_for[self.player_name] = 0

            # <Evaluation Meter initialization>
            # Makes an new entry in the evaluation meter dictionary for bots never encountered before,
            # initializes score to 0

            #If this player's name is not in the evaluation meter, add it
            #if not REBot.evaluation_meter.has_key(self.player_name): //This was used for Python 2
            if self.player_name not in REBot.evaluation_meter:
                REBot.evaluation_meter[self.player_name] = 0
                self.log.debug("LOG: Added player " + str(player) + " to evaluation meter\n")

        self.log.debug("\nLOG: Players encountered so far: " + str(len(REBot.evaluation_meter)) + "\n")
        # </Evaluation Meter initialization>



        #<Suspicion Meter initialization>

        #Initialize Suspicion Meter as an empty dictionary
        self.suspicion_meter = {}

        '''
        #Suspicion Meter if I am RESISTANCE
        #I know I am Resistance so I do not add myself to the list of suspects
        if self.isSpy is False:
            for player in self.others():
                self.suspicion_meter.append([player.name,0])

            self.log.debug("Suspicion Meter Resistance: " + str(self.suspicion_meter) + "\n")

        #Suspicion Meter if I am SPY
        #I want to get a feel of what the others think of me and the other spy so I add myself
        if self.isSpy is True:
            for player in players:
                self.suspicion_meter.append([player.name,0])

            self.log.debug("Suspicion Meter Spies: " + str(self.suspicion_meter) + "\n")
        '''

        #Suspicion Meter used by both Resistance and Spy
        #If Resistance, disregard yourself, you know you are Resistance
        #If Spy, monitor the suspicion meter of yourself and the other spy to get a feel of what the others think of you
        for player in players:
            self.suspicion_meter[player.name] = 0


        # </Suspicion Meter initialization>

        self.log.debug("----------------------------------------\n")

        pass

    def onMissionAttempt(self, mission, tries, leader):

        #If Spy and losing
        if self.isSpy is True:
            if self.game.turn == 3 and self.game.wins >= 1:
                self.agressive_mode = True
            elif self.game.turn == 4 and self.game.wins >= 2:
                self.agressive_mode = True
            elif self.game.turn == 5 and self.game.wins >= 2:
                self.agressive_mode = True

        if self.agressive_mode is True:
            self.log.debug("--Agressive Mode is ON--\n\n")
        pass

    def select(self, players, count):

        self.log.debug("---TIME TO SELECT---\n\n")
        self.log.debug("LOG: I need to select " + str(count) + " players\n")

        #Get a sorted list of evaluated bots only if they are in this game
        self.current_evaluation_meter = self.evaluationMeterToSortedList(REBot.evaluation_meter)
        #Get a sorted list of the suspicion meter
        self.current_suspicion_meter = self.suspicionMeterToSortedList(self.suspicion_meter,self.isSpy)
        self.current_suspicion_meter_reversed = []
        self.current_suspicion_meter_reversed = self.current_suspicion_meter.reverse()

        self.selection_names = []
        self.selection_list = []
        self.current_evaluation_meter_count_names = []

        #If I am Resistance
        if self.isSpy is False:
            self.selection_list = [self] + random.sample(self.others(), count - 1)
            return self.selection_list

            '''
            #If first sabotage has been made - that means we have collected some suspicion data
            if self.firstSabotage is True:

                    print("suspmtr" + str(self.current_suspicion_meter))
                    print("suspmtrrvr" + str(self.current_suspicion_meter_reversed))
                    self.log.debug("LOG: First Sabotage Made - Always selecting myself and [count-1] lowest on suspicion meter--\n")
                    self.selection_names = [self.player_name] + self.current_suspicion_meter[0:count-1][0]


                    # For every player
                    for player in self.game.players:
                        print(player.name)
                        print(self.selection_names)
                        # If player is in the top [count] evaluated players
                        if player.name in self.selection_names:
                            # Put him on the list of selections
                            self.selection_list.append(player)

                    self.log.debug("LOG:Team Selection: \n")
                    self.log.debug(str(self.selection_list) + "\n")
                    self.log.debug("----------------------------------------\n")
                    assert(len(self.selection_list) == count)
            return self.selection_list

        #We don't have any suspicion data
        else:

            self.selection_list = [self] + random.sample(self.others(), count - 1)
            self.log.debug("LOG: Team Selection:\n")
            self.log.debug(str(self.selection_list) + "\n")
            self.log.debug("----------------------------------------\n")
            assert(len(self.selection_list) == count)
            return self.selection_list
        '''
        if self.isSpy is True:
            self.selection_list = [self] + random.sample(self.others(), count - 1)
            return self.selection_list


    def onTeamSelected(self, leader, team):

        self.log.debug("TEAM SELECTED\n\n")

        # Increment total selections that happened in this game by 1
        self.selectionsMade += 1

        #Save team members in current team variables for further processing
        self.current_team = team
        self.current_team_all = [p.name for p in team]
        self.current_team_leader = leader.name
        self.current_team_excluding_leader = [p.name for p in team if p != leader]

        #self.log.debug("Players not leader: " + str(self.current_team_excluding_leader))
        #self.log.debug("Team leader: " + self.current_team_leader)

        self.log.debug("LOG: Players selected in team:\n")
        self.log.debug(str(self.current_team))

        self.log.debug("LOG: Current team excluding leader: \n")
        self.log.debug(str(self.current_team_excluding_leader) + "\n")

        # Add one to number_each_bot_selected for each bot in selected team, excluding this bot
        for player in self.current_team:
            if player in self.others():
                self.number_each_bot_selected[player.name] += 1

        self.log.debug("LOG: Number each bot was selected in a team this game: \n")
        self.log.debug(str(self.number_each_bot_selected) + "\n")

        # Get a list of the suspected spies
        self.current_suspicion_meter = self.suspicionMeterToSortedList(self.suspicion_meter, self.isSpy)

        self.current_suspicion_meter_top_two = [str(self.current_suspicion_meter[0][0]),str(self.current_suspicion_meter[1][0])]


        if self.firstSabotage is True:
            self.log.debug("LOG: Top suspected spies ")
            self.log.debug("are " + str(self.current_suspicion_meter_top_two) + "\n")


        #<Suspicion meter update - Decision Tree for onTeamSelected>
        if self.firstSabotage is True:
                       
            #If team leader is on the first two spots of suspicion meter (suspected spy)
            if self.current_team_leader in self.current_suspicion_meter_top_two:
                self.log.debug("LOG: Team leader " + self.current_team_leader + " is a suspected spy!\n")
                #If member of the team excluding leader is a suspected spy
                for player_name in self.current_team_excluding_leader:
                    if player_name in self.current_suspicion_meter_top_two:
                        #Add 4 to the team leader's suspicion metric
                        self.suspicion_meter[self.current_team_leader] += 4
                        #Add 2 to each other team mumber that is a suspected spy
                        self.log.debug("LOG: Team member " + player_name + " is a suspected spy!\n")
                        self.suspicion_meter[player_name] +=2
                        break
                #If no member of the team excluding leader is a suspected spy
                else:
                    self.log.debug("LOG: No team member excluding leader is a suspected spy.\n")
                    #Add 1 to everyone in team
                    self.suspicion_meter[self.current_team_leader] += 1
                    for player_name in self.current_team_excluding_leader:
                        self.suspicion_meter[player_name] += 1
            
            #If team leader is not a suspected spy
            else:
                # If member of the team excluding leader is a suspected spy
                for player_name in self.current_team_excluding_leader:
                    if player_name in self.current_suspicion_meter_top_two:
                        self.log.debug("LOG: There are suspected spies as members of this team!\n")
                        # Add 1 to everyone in team
                        self.suspicion_meter[self.current_team_leader] += 1
                        self.suspicion_meter[player_name] += 1
                        break
                #If no member of the team is a suspected spy
                else:
                    self.log.debug("LOG: There are no suspected spies in this team.\n")
                    # Subtract 4 to the team leader's suspicion metric
                    self.suspicion_meter[self.current_team_leader] -= 4
                    #Subtract 2 from everyone else in team
                    for player_name in self.current_team_excluding_leader:
                        self.suspicion_meter[player_name] -= 2


        #</Suspicion meter update - Decision Tree for onTeamSelected>

        self.log.debug("----------------------------------------\n")

        pass


    def vote(self,team):

        self.log.debug("\nLOG: Voting...\n")

        if self.isSpy is False:
            for player in team:
                #If current team has suspected spies
                if player.name in self.current_suspicion_meter_top_two:
                    #If this is the last try
                    if self.game.tries == 5:
                        return True
                    else:
                        return False
                else:
                    return True


        self.log.debug("----------------------------------------\n")

        if self.isSpy is True:
            if self.agressive_mode is True:
                #If I or the other spy are in the team
                if self in team or self.other_spies in team:
                    return True
                else:
                    return False
            else:
                #Am I in team?
                if self in team:
                    #Is other spy in team?
                        if self.other_spies in team:
                            #Am I or other spy suspected?
                                if self.name in self.current_suspicion_meter_top_two or self.other_spies.name in self.current_suspicion_meter_top_two:
                                    return False
                                else:
                                    return True
                        else:
                            return True
                else:
                    # Is other spy in team?
                    if self.other_spies in team:
                        #Is other spy suspected?
                        if self.other_spies.name in self.current_suspicion_meter_top_two:
                            return False
                        else:
                            return True
                    #If neither me or other spy in team
                    else:
                        #Am I a suspected spy?
                        if self.name in self.current_suspicion_meter_top_two:
                            return True
                        else:
                            return False

    def onVoteComplete(self, votes):

        #Get a list with the names of all the players in game
        self.all_players_in_game = [p.name for p in self.game.players]

        # Increment total votes that happened in this game by 1
        self.votesMade += 1

        self.log.debug("List of votes: \n")
        self.log.debug(str(votes))

        '''
        //Old code, used list.count(True) and list.count(False) instead
        #Count positive votes
        for True in votes:
            self.log.debug("True vote found \n")
            self.numPositiveVotes += 1

        #Count negative votes
        for False in votes:
            self.log.debug("False vote found \n")
            self.numNegativeVotes += 1
        '''

        self.log.debug("LOG: Players to Votes: \n")
        for player_name in self.all_players_in_game:
            self.log.debug("|| "+ player_name + " - " + str(votes[self.all_players_in_game.index(player_name)]) + " ||\n")

        self.log.debug("LOG: Number of positive votes: " + str(votes.count(True)) + "/ Number of negative votes: " + str(votes.count(False)))



        self.number_of_suspected_spies = 0

        if self.firstSabotage is True:
            self.log.debug("--Vote Analysis:--\n")

            # Does the mission contain any suspected spies?
            for player_name_in_team in self.current_team_all:
                if player_name_in_team in self.current_suspicion_meter_top_two:
                    # Increment the number of suspected spies
                    self.number_of_suspected_spies += 1

        # <Suspicion meter update - onVoteComplete decision tree>

        if self.firstSabotage is True:

            for player_name in self.all_players_in_game:

                    #Have they voted for the mission?
                    if votes[self.all_players_in_game.index(player_name)] is True:

                        #If the mission contains suspected spies
                        if self.number_of_suspected_spies > 0:
                            #Add 2 * numberOfSpies Suspicion to the player
                            self.suspicion_meter[player_name] += 2 * self.number_of_suspected_spies
                            self.log.debug(">" + player_name + " has voted for a team with suspected spies! (+2 * noOfSpies)\n")
                        #If the mission doesn't contain any suspected spies
                        else:
                            #Subtract 2 from player
                            self.suspicion_meter[player_name] -= 2
                            self.log.debug(">" + player_name + " has voted for a team without suspected spies! (-2)\n")

                    #Have they voted against the mission?
                    elif votes[self.all_players_in_game.index(player_name)] is False:

                        #If the mission contains suspected spies
                        if self.number_of_suspected_spies > 0:
                            # Add 2 * numberOfSpies Suspicion to the player
                            self.suspicion_meter[player_name] -= 2
                            self.log.debug(">" + player_name + " has voted against a team with suspected spies! (-2)\n")
                        # If the mission doesn't contain any suspected spies
                        else:
                            # Subtract 2 from player
                            self.suspicion_meter[player_name] += 1
                            self.log.debug(">" + player_name + " has voted against a team without suspected spies! (+1)\n")

        # </Suspicion meter update - onVoteComplete decision tree>

        # Get a list of the suspected spies
        self.current_suspicion_meter = self.suspicionMeterToSortedList(self.suspicion_meter, self.isSpy)

        self.log.debug("--Current Suspicion Meter:--\n" + str(self.current_suspicion_meter) + "\n")

        #Compare the votes to see if success or failure
        if votes.count(True) > votes.count(False):
            self.log.debug("LOG: Team selected voting success\n")

            self.log.debug("LOG: Players in voted team: \n")

            # Add one to number_each_bot_selected for each bot in voted team, excluding this bot
            for player in self.current_team:
                # List players in team that passed the voting process
                self.log.debug(str(player) + "\n")
                if player in self.others():
                    # Add one to number_each_bot_selected for each bot in team
                    self.number_each_bot_voted_for[str(player)[2:]] += 1

            self.log.debug("Number each bot was in a team that was voted up this game: \n")
            self.log.debug(str(self.number_each_bot_voted_for) + "\n")

        else:
            self.log.debug("LOG: Team selected voting failed\n")

        self.log.debug("----------------------------------------\n")

        pass

    def sabotage(self):

        #If Agressive Mode is ON
        if self.agressive_mode is True:
            #Sabotage
            return True
        else:
            #Is the other spy in the team?
            if self.other_spies in self.game.team:
                #Am I a suspected spy?
                if self.name in self.current_suspicion_meter_top_two:
                    return False
                else:
                    #Is other spy a suspect?
                    if self.other_spies.name in self.current_suspicion_meter_top_two:
                        return False
                    else:
                        return True
            else:
                # Am I a suspected spy?
                if self.name in self.current_suspicion_meter_top_two:
                    return False
                else:
                    return True



    def onMissionComplete(self, sabotaged):
        # Add one to number_each_bot_selected for each bot in team

        self.log.debug("LOG: MISSION VOTING SUCCESS\n\n")

        if sabotaged > 0 and self.firstSabotage is False:
            self.firstSabotage = True
            self.log.debug("--LOG: This is the first sabotage of the game!--")

       #<Suspicion Meter Update - onMissionComplete decision tree>
        if self.firstSabotage is True:
            #If the mission has been sabotaged
            if sabotaged > 0:

                self.log.debug("LOG: Mission has been sabotaged " + str(sabotaged) + " times\n")
                #If I am Resistance, in a mission with one other player and it is sabotaged, I have found a spy
                #Add 1000 to the suspicion meter for that player
                if self in self.game.team and self.isSpy is False and len(self.game.team) == 2 and sabotaged == 1:
                    self.log.debug("LOG: I am Resistance, in a mission with one other player and it is sabotaged, I have found a spy\n")
                    for player in self.current_team:
                        if player!=self:
                            self.suspicion_meter[player.name] += 1000
                # If I am Resistance, in a mission with two other player and it is sabotaged twice, I have found both spies
                # Add 1000 to the suspicion meter to each player
                elif self in self.game.team and self.isSpy is False and len(self.game.team) == 3 and sabotaged == 2:
                    self.log.debug("LOG: I am Resistance, in a mission with two other player and it is sabotaged twice, I have found both spies\n")
                    for player in self.current_team:
                        if player!=self:
                            self.suspicion_meter[player.name] += 1000
                #If there is a team of 2 people and the mission in sabotaged twice, I have found both spies
                # Add 1000 to the suspicion meter to each player
                elif self not in self.game.team and len(self.game.team) == 2 and sabotaged == 2:
                    self.log.debug("There is a team of 2 people and the mission in sabotaged twice, I have found both spies\n")
                    for player in self.current_team:
                        self.suspicion_meter[player.name] += 1000
                else:
                    #Add 10 to the suspicion meter of the sabotaged mission's team leader multiplied by the number of sabotages
                    self.suspicion_meter[self.current_team_leader] += 10 * sabotaged
                    #Add 5 to the suspicion meter of the sabotaged mission's other members multiplied by the number of sabotages
                    for player in self.current_team_excluding_leader:
                        self.suspicion_meter[player] += 5 * sabotaged
            else:

                self.log.debug("LOG: Mission has not been sabotaged\n")

                if self.game.turn >= 3:
                    # Subtract 10 from the suspicion meter of the successful mission's team leader after turn 3
                    self.suspicion_meter[self.current_team_leader] -= 10
                    # Subtract 5 from the suspicion meter of the successful mission's other members after turn 3
                    for player in self.current_team_excluding_leader:
                        self.suspicion_meter[player] -= 5
                else:
                    # Subtract 5 from the suspicion meter of the successful mission's team leader
                    self.suspicion_meter[self.current_team_leader] -= 5
                    # Subtract 2 from the suspicion meter of the successful mission's other members
                    for player in self.current_team_excluding_leader:
                        self.suspicion_meter[player] -= 2
        # </Suspicion Meter Update - onMissionComplete decision tree>

        self.current_suspicion_meter = self.suspicionMeterToSortedList(self.suspicion_meter,self.isSpy)
        self.log.debug("Current Suspicion Meter: " + str(self.current_suspicion_meter))


        self.log.debug("----------------------------------------\n")

        pass

    def onMissionFailed(self, leader, team):

        self.log.debug("LOG: MISSION VOTING FAILURE\n")

        #<Suspicion Meter Update - onMissionFailed decision tree>

        if self.firstSabotage is True:
            for player_name in self.all_players_in_game:
                #If the leader was a suspected spy
                if self.current_team_leader in self.current_suspicion_meter_top_two:

                    #If other members of the team were suspected spies
                    if self.current_team_excluding_leader in self.current_suspicion_meter_top_two:
                        #If this player's vote was No for this team
                        if self.game.votes[self.all_players_in_game.index(player_name)] is False:
                            self.suspicion_meter[player_name] -= 2
                    # If other members of the team weren't suspected spies
                    else:
                        # If this player's vote was No for this team
                        if self.game.votes[self.all_players_in_game.index(player_name)] is False:
                            self.suspicion_meter[player_name] -= 1


                #If the leader wasn't a suspected spy
                else:
                    # If other members of the team were suspected spies
                    if self.current_team_excluding_leader in self.current_suspicion_meter_top_two:
                        # If this player's vote was No for this team
                        if self.game.votes[self.all_players_in_game.index(player_name)] is False:
                            self.suspicion_meter[player_name] -= 1
                    # If NO members of the team were suspected spies
                    else:
                        # If this player's vote was No for this team
                        if self.game.votes[self.all_players_in_game.index(player_name)] is False:
                            self.suspicion_meter[player_name] += 3
            self.log.debug("Suspicion Meter Updated...")
        #</Suspicion Meter Update - onMissionFailed decision tree>

        self.log.debug("----------------------------------------\n")

        pass

    def onGameComplete(self, win, spies):

        # Dictionary that gets a True or False value for each player in game, excluding this bot.
        # True if that player's team won at the game's end
        self.eval_won = {}

        if win == True:
            self.log.debug("LOG: RESISTANCE WON THE GAME\n\n")

        if win == False:
            self.log.debug("LOG: SPIES WON THE GAME\n\n")

        for player in self.others():
            # Remove index number and dash from player string (string characters index 0 and 1) to leave just
            # the player's name in order to not confuse the evaluation meter which persists through games
            self.player_name = str(player)[2:]

            #Sets win of this game to zero by default
            self.eval_won[self.player_name] = 0

            # If player was Resistance and Resistance won
            if player not in spies and win is True:
                self.eval_won[self.player_name] = 1
                self.log.debug(">Player " + self.player_name + " won.\n")

            if player in spies and win is False:
                self.eval_won[self.player_name] = 1
                self.log.debug(">Player " + self.player_name + " won.\n")

            #Calculate selection and voted for ratio for each player
            self.eval_selected = float(self.number_each_bot_selected[self.player_name])/self.selectionsMade
            self.eval_voted = float(self.number_each_bot_voted_for[self.player_name])/self.votesMade

            #Evaluate each player's performance this game and add it to their previous score
            REBot.evaluation_meter[self.player_name] += float(self.eval_won[self.player_name] + ((self.eval_selected + self.eval_voted)/2))

        self.current_evaluation_meter = self.evaluationMeterToSortedList(REBot.evaluation_meter)
        self.log.debug("LOG: Evaluation list for bots in current game: \n")
        self.log.debug(str(self.current_evaluation_meter) + "\n\n")

        self.log.debug("LOG: Evaluation of all bots encountered so far: \n")
        self.log.debug(str(REBot.evaluation_meter) + "\n")


        self.log.debug("\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n")

        pass
