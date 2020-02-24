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
        self.isLeaf = True

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
        for i in range(len(self.children)):
            if self.children[i] is not None and self.children[i].getWinChance() > currentMaxWin:
                currentMaxWin = self.children[i].getWinChance()
                bestChild = self.children[i]

        return bestChild

    def getUCT(self):
        # UCT formula as specified by wikipedia
        return (self.score/self.sims) + self.explore * sqrt(log(self.parent.sims) / self.sims)

    def getWinChance(self):
        return self.score / self.sims

    def getScore(self):

        # Take win chance and normalize it to be between -1 and 1, 1 indicates blue winning
        if self.state.turn == GREEN:
            return 2 * self.score / self.sims - 1
        else:
            return - (2 * self.score / self.sims - 1)

