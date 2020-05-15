
import CubiCupMCTS
import threading
import Network


class Player:

    def __init__(self, game, player=-1, simsPerMove=1600, outputFunc=None):

        self.game = game
        self.player = player  # -1 means all players, otherwise should be set to player number
        self.simsPerMove = simsPerMove

        # Join game
        self.game.join(self)

        gameSize = game.size




        self.mcts = CubiCupMCTS.MCTS(self.game.size, moveProbFunc=outputFunc)

        #print("creating player")

    def update(self, move):
        self.mcts.updateWithTurn(move)

    def play(self):

        #print("playing")

        # Start mcts in thread
        mctsThread = threading.Thread(target=self.mcts.run)
        mctsThread.daemon = True
        mctsThread.start()
        #print("starting mcts")

        # If sims number reached (or game is terminal) and it's this players turn, take turn
        while True:
            if (self.mcts.root.sims >= self.simsPerMove or self.mcts.root.isTerminal) \
                    and (self.mcts.root.state.turn == self.player or self.player == -1):

                # Pause mcts while we take turn and get move probabilities
                self.mcts.setPause()
                while True:
                    if self.mcts.isPaused:
                        break

                bestChild = self.mcts.root.getBestChild()
                bestMove = bestChild.state.lastMove
                #print("taking turn " + str(bestMove))
                self.game.takeTurn(bestMove, self.mcts.root.getMoveProbabilities())

                # Wait until mcts has updated root, then let it continue
                while True:
                    if not self.mcts.newRootReady:
                        break
                self.mcts.setPlay()

            # If game is over, stop the mcts and break out of loop
            if self.mcts.root.state.gameOver:
                self.mcts.end()
                mctsThread.join()
                #print("game over")
                break

        # return all info to be saved, moves

