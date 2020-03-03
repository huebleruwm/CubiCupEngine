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
        self.explore = 1
        self.terminalChild = None
        self.childrenUnexplored = len(self.children)
        self.actionFor = state.lastTurn()

        if self.state.gameOver:
            self.isTerminal = True
            self.terminalValue = state.endValue
            self.terminalScore = state.endValue[self.actionFor]
        else:
            self.isTerminal = False
            self.terminalValue = None
            self.terminalScore = -float("inf")

    # Create a child from the ith available move
    def createChildAt(self, i):
        # Copy current state
        newChildState = CubiCupState.State(self.state.boardSize, self.state)

        # Update the new state with the ith available move
        newChildState.takeTurn(self.state.availableMoves[i])

        # Create new node with new state, listing this node as parent
        self.children[i] = CubiCupNode.Node(self, newChildState)

        # This node has a child, it is no longer a leaf
        self.childrenUnexplored -= 1

    # Check to see if this node is terminal, terminal is defined by:
    #   1) A child can result in a forced win for this node, terminal win
    #   2) All children are terminal
    # This attempts to find the best win available, but this doesn't guarantee we find the
    # best win, we could get the greatest terminal score that is a win, but if a better move
    # has not been determined to be terminal yet, we can't find it.
    def checkForTerminal(self):

        allChildrenTerminal = True  # Assume all nodes are terminal

        # Loop through all children
        for child in self.children:
            if child is not None and child.isTerminal:
                # If child has better terminal value, save it
                if child.terminalValue[self.actionFor] >= self.terminalScore:
                    self.terminalChild = child
                    self.terminalValue = child.terminalValue
                    self.terminalScore = child.terminalValue[self.actionFor]
            else:
                # Non-existent child or non terminal child
                allChildrenTerminal = False

        # All child nodes are terminal or we found a terminal win
        if allChildrenTerminal or self.terminalScore >= 1:
            self.isTerminal = True

    def updateWith(self, sims, endValue):
        self.sims += sims
        self.score += endValue[self.actionFor]

    # This method finds the best available move for this node, attempts to maximize win chance
    def getBestChild(self):

        # If this node is terminal, the best option is a forced win child. Otherwise all children
        # are either forced losses or ties, in this case we want the tie
        if self.isTerminal:
            if self.terminalChild is not None:
                # A terminal win child exists, that's a winning move for sure, can't get better than that
                return self.terminalChild

        currentMaxWin = -float("inf")
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

    def getScore(self):

        if self.isTerminal:
            if self.terminalScore == 0.5:
                return 0
            elif self.terminalScore >= 1:
                if self.actionFor == BLUE:
                    return 1
                else:
                    return -1
            elif self.terminalScore <= 0:
                if self.actionFor == BLUE:
                    return -1
                else:
                    return 1

        if self.actionFor == BLUE:
            return 2 * self.getWinChance() - 1
        else:
            return - (2 * self.getWinChance() - 1)
