
import CubiCupState
import copy

class Game:

    def __init__(self, size):
        self.size = size
        self.state = CubiCupState.State(size)
        self.players = []
        self.endValue = 0
        self.history = []

    def takeTurn(self, move, moveProbs):

        self.history.append((copy.deepcopy(self.state), moveProbs))

        self.state.takeTurn(move)

        if self.state.gameOver:
            self.endValue = self.convertEndValToScore(self.state.endValue)

        for player in self.players:
            player.update(move)

    def join(self, player):
        self.players.append(player)

    def convertEndValToScore(self, endValue):
        if endValue == (1, 0):
            return 1
        elif endValue == (0.5, 0.5):
            return 0
        else:
            return -1



