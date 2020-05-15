from math import sqrt
from math import log
import CubiCupState
import CubiCupNode
from CubiCupDriver import BLUE
from CubiCupDriver import GREEN
import Network


class Node:

    def __init__(self, parent, state, probability=1, moveProbFunc=None):
        self.parent = parent
        self.state = state
        self.score = 0
        self.sims = 0
        self.explore = 2
        self.terminalChild = None
        self.actionFor = state.lastTurn()
        self.probability = probability
        self.children = [None for x in range(len(state.availableMoves))]
        self.childrenUnexplored = len(self.children)
        self.moveProbFunc = moveProbFunc

        if moveProbFunc is not None:
            self.childProbs = Network.getMoveProbs(self.state, moveProbFunc)
        else:
            self.childProbs = None

        if self.state.gameOver:
            self.isTerminal = True
            self.terminalValue = state.endValue
            self.terminalScore = state.endValue[self.state.turn]
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
        if self.childProbs is None:
            self.children[i] = CubiCupNode.Node(self, newChildState, moveProbFunc=self.moveProbFunc)
        else:
            self.children[i] = CubiCupNode.Node(self, newChildState, probability=self.childProbs[i], moveProbFunc=self.moveProbFunc)

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
                if child.terminalValue[child.actionFor] >= self.terminalScore:
                    self.terminalChild = child
                    self.terminalValue = child.terminalValue
                    self.terminalScore = child.terminalValue[child.actionFor]
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

        # If this node is terminal, the terminal child maximizes our score, so if it is
        # greater than 0, it's either a forced win for this node, or there is a tie
        # with every other being either a tie or a loss. So if we are greater than 0,
        # that's the best we can do, otherwise just uses the win chance and hope
        # the other player doesn't see how to force their win
        if self.isTerminal and self.terminalScore > 0:
            return self.terminalChild

        currentMaxWin = -float("inf")
        bestChild = None
        # Loop through all children to find the one with the greatest win chance
        for child in self.children:
            if child is not None and child.getWinChance() > currentMaxWin:
                currentMaxWin = child.getWinChance()
                bestChild = child

        return bestChild

    # Get the child that has the highest UCT score, if child does not exist, create it
    def getChildToExpandIndex(self):

        maxUCT = -float("inf")
        bestChildIndex = None

        for i in range(len(self.children)):

            if self.children[i] is None:
                if self.childProbs is None:
                    # No child probs and child does not exist, just greedy explore
                    return i
                else:
                    # Use UCT without win percent, just explore/probability
                    UCT = self.explore * self.childProbs[i] * sqrt(log(self.sims))
            else:
                UCT = self.children[i].getUCT()

            if UCT >= maxUCT:
                maxUCT = UCT
                bestChildIndex = i

        return bestChildIndex

    def getUCT(self):
        # UCT formula as specified by wikipedia
        #return (self.score/self.sims) + self.explore * sqrt(log(self.parent.sims) / self.sims)

        # UCT based on Alpha Zero, using probability to scale the explore factor seems to make the mose sense
        return (self.score/self.sims) + self.explore * self.probability * sqrt(log(self.parent.sims) / self.sims)

    def getWinChance(self):
        return self.score / max(self.sims, 1)

    def getScore(self):

        if self.isTerminal:
            if self.terminalScore == 0.5:
                return 0
            elif self.terminalScore >= 1:
                if self.state.turn == BLUE:
                    return 1
                else:
                    return -1
            elif self.terminalScore <= 0:
                if self.state.turn == BLUE:
                    return -1
                else:
                    return 1

        if self.actionFor == BLUE:
            return 2 * self.getWinChance() - 1
        else:
            return - (2 * self.getWinChance() - 1)

    def getMoveProbabilities(self):

        size = self.state.boardSize

        moveProbs = [[[0 for x in range(size + 1)] for y in range(size + 1)] for z in range(size + 1)]

        for i in range(len(self.children)):

            child = self.children[i]
            move = self.state.availableMoves[i]

            # Get x,y,z from move tuple
            x = move[0]
            y = move[1]
            z = move[2]

            if child is None:
                #print("adding " + str(self.state.availableMoves[i]) + " : " + 0 + " : " + str((self.sims-1)))
                #moveProbs.append((self.state.availableMoves[i], 0))
                moveProbs[x][y][z] = 0
            else:
                #print("adding " + str(self.state.availableMoves[i]) + " : " + str(child.sims) + " : " + str((self.sims-1)))
                #moveProbs.append((self.state.availableMoves[i], child.sims/(self.sims-1)))
                moveProbs[x][y][z] = child.sims/(self.sims-1)

        return moveProbs

