import CubiCupState
import CubiCupNode
import random
import time
from CubiCupDriver import BLUE
from CubiCupDriver import GREEN


class MCTS:

    def __init__(self, size, moveProbFunc=None):
        newGameState = CubiCupState.State(size)
        self.root = CubiCupNode.Node(None, newGameState, moveProbFunc=moveProbFunc)
        self.root.sims = 1  # First node needs to start at 1, otherwise sum of child sims is parent sims-1, no idea why, this is just a hacky fix
        self.newRoot = None
        self.newRootReady = False
        self.reset = False
        self.gameSize = size
        self.simsSinceLastMove = 0
        self.kill = False
        self.pause = False
        self.isPaused = False
        self.moveProbFunc = moveProbFunc

    def resetMCTS(self):
        # Reset all parameters
        newGameState = CubiCupState.State(self.gameSize)
        self.root = CubiCupNode.Node(None, newGameState, self.moveProbFunc)
        self.newRoot = None
        self.newRootReady = False
        self.reset = False
        self.simsSinceLastMove = 0
        self.pause = False
        self.kill = False
        self.isPaused = False

    def indicateReset(self, size):
        # Indicate that we are ready to reset the MCTS
        self.gameSize = size
        self.reset = True

    def end(self):
        self.kill = True

    def setPause(self):
        self.pause = True

    def setPlay(self):
        self.pause = False

    def updateWithTurn(self, move):

        # Find node with move in children list, then set the new root to that child
        for i in range(len(self.root.children)):
            child = self.root.children[i]
            if child is not None:
                if child.state.lastMove == move:
                    self.newRoot = self.root.children[i]
                    self.newRootReady = True
                    self.simsSinceLastMove = 0

    def selectNodeToExpand(self, node):

        # If node is a game over, return it
        if node.isTerminal:
            return node

        """
        # If there are any unexplored children, choose one of them
        # This should be replaced by a neural network call,
        if node.childrenUnexplored > 0:
            newChildIndex = len(node.children) - node.childrenUnexplored
            node.createChildAt(newChildIndex)
            return node.children[newChildIndex]

        maxUCT = -float("inf")
        bestNode = node

        # Loop through all children for specified node
        for child in node.children:

            # Ignore terminal children, only make a wish cares about them
            if not child.isTerminal:
                # Get UCT of current child node we're looking at
                currentUCT = child.getUCT()

                # If child node has best yet UCT then save the value and child
                if currentUCT >= maxUCT:
                    maxUCT = currentUCT
                    bestNode = child
        """

        expandIndex = node.getChildToExpandIndex()

        # If child to expand is new, return it
        if node.children[expandIndex] is None:
            node.createChildAt(expandIndex)
            return node.children[expandIndex]

        return self.selectNodeToExpand(node.children[expandIndex])

    def simulate(self, node):

        # Copy the state so that we have one we can update without changing anything we need
        state = CubiCupState.State(self.gameSize, node.state)

        # Loop until game is over, choosing random move each time
        while not state.gameOver:
            randomMove = state.availableMoves[random.randint(0, len(state.availableMoves) - 1)]
            state.takeTurn(randomMove)

        return state.endValue

    def backPropagate(self, endValue, node):

        # Traverse tree by calling parents, incremented simulations and score
        while node is not self.root:

            if node.isTerminal:
                # If this node is terminal, check to see if the parent is as well
                node.parent.checkForTerminal()

            node.updateWith(1, endValue)
            node = node.parent

        # Update root values to finish
        self.root.updateWith(1, endValue)

    def run(self):

        while True:

            # If move is made, we want to update the root node
            if self.newRootReady:
                self.root = self.newRoot    # Change root node
                self.root.parent = None     # Delete parent, since it is now irrelevant, this saves memory
                self.newRootReady = False

            # If reset has been indicated, for something like the start of a new game, do a reset
            if self.reset:
                self.resetMCTS()

            if self.kill:
                break

            if self.pause:
                self.isPaused = True
            else:

                # Run for a max of a million simulations, or until the root node is determined to be terminal
                if not self.root.isTerminal and self.root.sims < 1000000:

                    self.simsSinceLastMove = self.simsSinceLastMove + 1

                    # Select most promising node to expand upon
                    nodeToExpand = self.selectNodeToExpand(self.root)

                    # Using the most promising node as determined by the MCTS algorithm, determine
                    # the value and policy heads as predicted by the neural network.
                    # This should update the probabilities, telling us which move to explore, then
                    # we should back propagate the value during that step
                    # call neuralNet( bestNode )

                    # Simulate game starting from that node, recording who won
                    endValue = self.simulate(nodeToExpand)

                    # Back propagate the result of that simulation through the tree
                    self.backPropagate(endValue, nodeToExpand)

                else:
                    # No more searching being done, just sleep to be courteous to cpu
                    time.sleep(0.1)



            #print("SIM: " + str(self.root.sims))
            #self.printNodeChildren(self.root, "")
            #print("")

    # Debugging routine, used to print the tree, called recursively
    def printNodeChildren(self, node, header):

        header = header + "--"

        for child in node.children:

            if child is not None:
                print(header + str(child.state.lastMove) + " " + \
                      " Blue:" + str(child.state.pieces[BLUE]) + \
                      " Green:" + str(child.state.pieces[GREEN]) + \
                      " UCT: " + str(child.getUCT()))

                if child.isTerminal:
                    print(header + "Terminal Value: " + str(child.terminalValue) + " Score: " + str(child.terminalScore))

                self.printNodeChildren(child, header)






