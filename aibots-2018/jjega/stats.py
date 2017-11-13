from util import Variable

class GameData():

    def __init__(self):
        # Variables that caputres how well you lead in context of pass/fail mission
        self.leadTeam=Variable()
        self.leadSucMission=Variable()
        self.leadFailMission=Variable()

        # Variables that capture how well you voted in context of pass/fail mission
        self.voted=Variable()
        self.votedYes=Variable()
        self.votedNo=Variable()
        self.votedYesPass=Variable()
        self.votedYesFail=Variable()
        self.votedNoPass=Variable()
        self.votedNoFail=Variable()

        # Variables that capture how well you perform when selected in context of pass/ fail mission
        self.selected=Variable()
        self.selectedPass=Variable()
        self.selectedFail=Variable()

        # Variables that capture how much sabotaging/passing you were involved in
        self.sabotages=Variable()
        self.passeds=Variable()

        # Label True/False either spy or not
        self.Label=None

    def attributes(self):
        return(list(self.__dict__.keys()))



