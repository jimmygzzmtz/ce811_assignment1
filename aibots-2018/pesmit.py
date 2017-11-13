"""
    This bot was created by Patrick Elliot Smith (pesmit@essex.ac.uk) 07-11-2017
    This bot uses the 'Three Rules to Resistance Strategy' (Adapated from Avalon Resistance)
"""

from player import Bot 
from game import State
import random

class pesmit(Bot):
    """
    ======================================================================================
    INFO:
    ======================================================================================
    THIS BOT IS BASED ON THE 'THREE RULES TO RESISTANCE STRATEGY' - "A common sense stategy used by many Reistance players"
    The THREE RULES are as follows:
        1) Always select yourself and others, (the others you choose are up to your own preference)
        2) Always vote to REJECT missions that you are NOT ON, unless (See 2A)
            2A) It is the HAMMER ROUND (Fifth Round of Voting) Always accept/approve HAMMER ROUND selection.
        3) Determine an order of sabotage, given the -slight- limitations of this version of Resistance.
            3A) This means that this bot will typically -defer- to the other spy to sabotage.
                3B) if they are both on a mission.
                3C) If however, this bot is alone as a spy on a mission, they will only sabotage if:
                    3D) The SPIES are behind in score. Or the score is even at 2-2.

    All other functionality, is additional features to the SIMPLE THREE RULES of this bot.

    ======================================================================================
    FUNCTION INFO:
    ======================================================================================
    ON GAME REVEALED:
        - If BOT is SPY then instantiate list of ALL SPIES.
        - Use list of ALL SPIES to seperate OTHER SPY.
        - Instantiate list of PLAYERS.
        - Instantiate an empty list of 'TEAM1' (Used for annoucing/selection)
        - Instantiate an empty list of 'TEAM2' (Used for annoucing/selection)
        - Instantiate an int total of all SABOTAGE VOTES. (Used for Annoucing/On Mission Complete)
        - Instantiate an int total of all REJECT VOTES. (Used in onVoteComplete)
        - Instantiate an int total of all APPROVAL votes. (Used in onVoteComplete)
        
    SELECTION:
        - IF BOT is SPY
            - Create a list of all spies.
            - Create a list of all RESI (based on spies list)
            - Return [Self] + 'Other Spy' + Random Selection of Resistance
        - ELSE IF:
            - If the last mission was sabotaged.
            - Pick the ANTI version of that team.
                - (i.e. if P1 and P2 were on a team that sabotaged.)
                - (Then pick P3 and P4)
                - Developer Note: (Self.Team1 and Self.Team2)
                    - are used as distinctions between 2 person and 3 person groups
        - ELSE:
            - Return [Self] + Random Selection of all players.

    VOTING:
        - As per the SECOND RULE:
            - If it is the HAMMER ROUND (Fifth Round of Voting)
                - APPROVE/RETURN TRUE
            - if BOT is on the team (As per the First Rule)
                - APPROVE/RETURN TRUE
            - Otherwise
                - REJECT/RETURN FALSE
        
    ON VOTE COMPLETE:
        - Store values of REJ and APP votes in SELF.

    SABOTAGE:
        - Assume that BOT is SPY (Only Spies can Sabotage)
        - If the OTHER SPY is in the team and I am also in the team.
            - Return FALSE/DON'T SABOTAGE (As per RULE 3. This BOT will assume the other will sabotage)
        - If SPIES are currently behind in score (0-1 / 0-2 / 1-2) or need one more win (2-2) and this bot is the only SPY.
            - Return TRUE/SABOTAGE.
        - Otherwise, if I am the only spy, but the team size is TWO.
            - Return FALSE/DON'T SABOTAGE
        - Otherwise, if I am the only spy, but the team size is THREE.
            - Return TRUE/SABOTAGE
        - IN ALL OTHER CASES:
            - Return FALSE/DON'T SABOTAGE
        
    ON MISSION COMPLETE: (Mission Stage):
        - Keep track of team that sabotaged, record the total team in self.team
            - self.team1 used when the size of the team is (2)
            - self.team2 used when the size of the team is (3)
        - If they didn't sabotage, reset self.team1 and self.team2 to NONE
        
    ANNOUNCE:
        - If I have saved a SABOTAGE team into self.team:
            - Create SUBSET of TEAM up to the amount of Sabotage Votes
            ie. (If 1 person sabotaged, then pick 1 team member at random)
            - If the sabotaged team, matches the last team, and I was in that team:
                - If I am a SPY:
                    - Change SUBSET to equal the OTHER SPY if that team sabotaged (saboVote >= 1)
                    - Return a 0.2 (Out of 1.0) suspicion of the other SPY.
                - If I am not a SPY:
                    - Change SUBSET to equal a random choice of the OTHERS up to the amount of SABOTAGE VOTES.
                    ie. (If one person on the sabotage team, sabotaged. Then suspect -anyone-)
                    - Return a 0.6 (Out of 1.0) suspicion of that/those bots.
                - Otherwise:
                    - RETURN BLANK
            - Otherwise:
                - RETURN BLANK
        
    ON GAME COMPLETE:
        - Reset self.team1/2 to None
    """
    def onGameRevealed(self, players, spies):
        self.spies = spies
        self.otherSpies = random.sample(self.spies, len(self.spies))
        if(self in self.otherSpies and self.spy == True):
            self.otherSpies.remove(self)
        self.players = players
        self.team1 = None
        self.team2 = None
        self.saboVotes = 0
        self.rejVotes = 0
        self.appVotes = 0
        
    def select(self, players, count):
        if(self.spy):
            iAndSpy = []
            iAndSpy.extend(self.spies)
            resiList = []
            resiList.extend(s for s in self.others() if s not in self.spies)
            return iAndSpy + random.sample(resiList, count - 2)
        elif self.game.turn > 1 and self.team1 != None and self.team2 != None:
            if(self.game.turn < 3):
                antiTeam = [p for p in self.others() if p not in self.team1]
                return [self] + random.sample(antiTeam, count - 1)
            else:
                antiTeam = [p for p in self.others() if p not in self.team2]
                return [self] + random.sample(antiTeam, count - 1)
        else:
            return [self] + random.sample(self.others(), count -1)
        
    def vote(self, team):
        self.say("Is it the final vote?")
        if(self.game.tries == 5):
            return True
        elif self in self.game.team:
            return True
        else:
            return False

    def onVoteComplete(self, votes):
        self.rejVotes = 0
        self.rejVotes = len([s for s in votes if s == False])
        self.appVotes = 0
        self.appVotes = len([s for s in votes if s == True])
        
    def sabotage(self):
        if len([p for p in self.game.team if p in self.otherSpies]) == 1 and self in self.game.team:
            return False
        elif(self.game.losses <= self.game.wins or self.game.losses == 2
             and len([p for p in self.game.team if p in self.otherSpies]) == 0):
            return True
        elif len(self.game.team) == 2 and len([p for p in self.game.team if p in self.otherSpies]) == 0:
            return False
        elif len(self.game.team) == 3 and len([p for p in self.game.team if p in self.otherSpies]) == 0:
            return True
        else:
            return False
    
    def onMissionComplete(self, sabotaged):
        if sabotaged:
            if(self.game.turn < 3):
                self.team1 = self.game.team
                self.saboVotes = sabotaged
            else:
                self.team2 = self.game.team
                self.saboVotes = sabotaged
        if not sabotaged:
            self.team1 = None
            self.team2 = None
        return

    def announce(self):
        if(self.team1 != None):
            subset = (random.sample(self.team1, self.saboVotes))
            if(self.team1 == self.game.team and self not in self.team1):
                return({p: 0.3 for p in subset})
            elif(self.team1 == self.game.team and self in self.team1):
                if(self.spy):
                    subset = (random.sample(self.otherSpies, self.saboVotes))
                    return({p: 0.2 for p in subset})
                else:
                    subset = (random.sample(self.others(), self.saboVotes))
                    return({p: 0.6 for p in subset})
            else:
                return
        else:
            if(self.team2 != None):
                subset = (random.sample(self.team2, self.saboVotes))
                if(self.team2 == self.game.team and self not in self.team2):
                    return({p: 0.3 for p in subset})
                elif(self.team2 == self.game.team and self in self.team2):
                    if(self.spy):
                        subset = (random.sample(self.otherSpies, self.saboVotes))
                        return({p: 0.2 for p in subset})
                    else:
                        subset = (random.sample(self.others(), self.saboVotes))
                        return({p: 0.6 for p in subset})
                else:
                    return
            else:
                return

    def onGameComplete(self, win, spies):
        self.team1 = None
        self.team2 = None
        return
    
