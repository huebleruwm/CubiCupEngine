from math import sqrt
from math import log
import CubiCupState
import CubiCupNode
from CubiCupDriver import BLUE
from CubiCupDriver import GREEN


class Node:

    def __init__(self, parent, state):
        self.parent = parent
        self.children = [None for x in range(len(state.availableMoves))]
        self.state = state
        self.score = 0
        self.sims = 0
        self.explore = 1.41
        self.isLeaf = True

        if self.state.gameOver:
            self.isTerminal = True
            self.terminalScore = state.endValue
        else:
            self.isTerminal = False
            self.terminalScore = 0

    def createChildAt(self, i):
        # Copy current state
        newChildState = CubiCupState.State(self.state.boardSize, self.state)

        # Update the new state with the ith available move
        newChildState.takeTurn(self.state.availableMoves[i])

        # Create new node with new state, listing this node as parent
        self.children[i] = CubiCupNode.Node(self, newChildState)

        # This node has a child, it is no longer a leaf
        self.isLeaf = False

    def getBestChild(self):
        currentMaxWin = -1
        bestChild = None
        # Loop through all children to find the one with the greatest win chance
        for child in self.children:
            if child is not None and child.getWinChance() > currentMaxWin:
                currentMaxWin = child.getWinChance()
                bestChild = child

        return bestChild

    def getUCT(self):
        # UCT formula as specified by wikipedia
        return (self.score/self.sims) + self.explore * sqrt(log(self.parent.sims) / self.sims)

    def getWinChance(self):
        return self.score / self.sims

    def getScore(self):

        if self.isTerminal:
            if self.terminalScore == 0.5:
                # Node is terminal and is a tie
                return 0
            elif self.terminalScore == 1:
                # Node is terminal and blue wins
                return 1
            elif self.terminalScore == 0:
                # Node is terminal and green wins
                return -1

        # Take win chance and normalize it to be between -1 and 1, 1 indicates blue winning
        if self.state.turn == GREEN:
            return 2 * self.score / self.sims - 1
        else:
            return - (2 * self.score / self.sims - 1)

    def checkForTerminal(self):

        canTie = False

        # If this node is blue turn and there's a terminal child with score 1, that's a win
        # If this node is blue turn and all children are terminal with score 0, that's a loss
        if self.state.turn == BLUE:
            # Loop through all children
            for child in self.children:
                if child is not None:
                    # Child exists
                    if child.isTerminal:
                        # Child is terminal
                        if child.terminalScore == 1:
                            # Terminal child has win available for blue, declare this node terminal
                            self.isTerminal = True
                            self.terminalScore = 1
                            return
                        elif child.terminalScore == 0.5:
                            # Terminal child has tie available
                            canTie = True
                    else:
                        # Non-terminal child, this node isn't terminal
                        return
                else:
                    # Non-existent child, this node isn't terminal
                    return

            # All child nodes are terminal, but there are no wins for currently player
            if canTie:
                # Tie available
                self.isTerminal = True
                self.terminalScore = 0.5
            else:
                # No tie, so loss for blue
                self.isTerminal = True
                self.terminalScore = 0

        # If this node is green and there's a terminal child with score 0, that's a win
        # If this node is green turn and all children are terminal with score 1, that's a loss
        if self.state.turn == GREEN:
            # Loop through all children
            for child in self.children:
                if child is not None:
                    # Child exists
                    if child.isTerminal:
                        # Child is terminal
                        if child.terminalScore == 0:
                            # Terminal child has win available for green, declare this node terminal
                            self.isTerminal = True
                            self.terminalScore = 0
                            return
                        elif child.terminalScore == 0.5:
                            # Terminal child has tie available
                            canTie = True
                    else:
                        # Non-terminal child, this node isn't terminal
                        return
                else:
                    # Non-existent child, this node isn't terminal
                    return

            # All child nodes are terminal, but there are no wins for currently player
            if canTie:
                # Tie available
                self.isTerminal = True
                self.terminalScore = 0.5
            else:
                # No tie, so loss for green
                self.isTerminal = True
                self.terminalScore = 1



