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
        self.terminalWinChild = None
        self.terminalTieChild = None

        if self.state.gameOver:
            self.isTerminal = True
            self.terminalScore = state.endValue
        else:
            self.isTerminal = False
            self.terminalScore = 0

    # Create a child from the ith available move
    def createChildAt(self, i):
        # Copy current state
        newChildState = CubiCupState.State(self.state.boardSize, self.state)

        # Update the new state with the ith available move
        newChildState.takeTurn(self.state.availableMoves[i])

        # Create new node with new state, listing this node as parent
        self.children[i] = CubiCupNode.Node(self, newChildState)

        # This node has a child, it is no longer a leaf
        self.isLeaf = False

    # Check to see if this node is terminal, terminal is defined by:
    #   1) A child can result in a forced win for this node, terminal win
    #   2) All children are terminal, but all are forced wins for opposite player, terminal loss
    #   3) All children are terminal, there's no forced wins, but there's at least one way to tie, terminal tie
    def checkForTerminal(self):

        canTie = False
        allChildrenTerminal = True  # Assume all nodes are terminal

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
                            self.terminalWinChild = child
                            return
                        elif child.terminalScore == 0.5:
                            # Terminal child has tie available
                            canTie = True
                            self.terminalTieChild = child
                    else:
                        # Non-terminal child
                        allChildrenTerminal = False
                else:
                    # Non-existent children can't be terminal
                    allChildrenTerminal = False

            # All child nodes are terminal, but there are no wins for currently player
            if allChildrenTerminal:
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
                            self.terminalWinChild = child
                            return
                        elif child.terminalScore == 0.5:
                            # Terminal child has tie available
                            canTie = True
                            self.terminalTieChild = child
                    else:
                        # Non-terminal child
                        allChildrenTerminal = False
                else:
                    # Non-existent children can't be terminal
                    allChildrenTerminal = False

            # All child nodes are terminal, but there are no wins for currently player
            if allChildrenTerminal:
                if canTie:
                    # Tie available
                    self.isTerminal = True
                    self.terminalScore = 0.5
                else:
                    # No tie, so loss for green
                    self.isTerminal = True
                    self.terminalScore = 1

    # This method finds the best available move for this node, attempts to maximize win chance
    def getBestChild(self):

        # If this node is terminal, the best option is a forced win child. Otherwise all children
        # are either forced losses or ties, in this case we want the tie
        if self.isTerminal:
            if self.terminalWinChild is not None:
                # A terminal win child exists, that's a winning move for sure, can't get better than that
                return self.terminalWinChild

            if self.terminalTieChild is not None:
                # If we get here, there's no terminal child with win, if terminal child with tie exists, that's the best
                return self.terminalTieChild

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
        return self.score / max(self.sims, 1)

    # Take win chance based on simulations and normalize it to be between -1 and 1, 1 indicates blue winning
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

        if self.state.turn == GREEN:
            return 2 * self.getWinChance() - 1
        else:
            return - (2 * self.getWinChance() - 1)
