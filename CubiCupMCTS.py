import CubiCupState
import CubiCupNode
import random
from CubiCupDriver import BLUE
from CubiCupDriver import GREEN


class MCTS:

    def __init__(self, size):
        newGameState = CubiCupState.State(size)
        self.root = CubiCupNode.Node(None, newGameState)
        self.newRoot = None
        self.newRootReady = False
        self.reset = False
        self.gameSize = size

    def indicateReset(self, size):
        # Indicate that we are ready to reset the MCTS
        self.gameSize = size
        self.reset = True

    def resetMCTS(self):
        # Reset all parameters
        newGameState = CubiCupState.State(self.gameSize)
        self.root = CubiCupNode.Node(None, newGameState)
        self.newRoot = None
        self.newRootReady = False
        self.reset = False

    def selectNodeToExpand(self, node):

        # If node is a game over, return it
        if node.state.gameOver:
            return node

        # If node is a leaf, just choose first child
        if node.isLeaf:
            node.createChildAt(0)
            return node.children[0]

        maxUCT = 0
        bestNode = node
        currentNode = node

        # Loop through all children for specified node
        for i in range(len(currentNode.children)):

            # If a child node has not been created, create it and return it
            if currentNode.children[i] is None:
                currentNode.createChildAt(i)
                return currentNode.children[i]

            # Get UCT of current child node we're looking at
            currentUCT = currentNode.children[i].getUCT()

            # If child node has best yet UCT then save the value and child
            if currentUCT >= maxUCT:
                maxUCT = currentUCT
                bestNode = currentNode.children[i]

        return self.selectNodeToExpand(bestNode)

    def simulate(self, node):

        # Copy the state so that we have one we can update without changing anything we need
        state = CubiCupState.State(self.gameSize, node.state)

        # Loop until game is over, choosing random move each time
        while not state.gameOver:
            randomMove = state.availableMoves[random.randint(0, len(state.availableMoves) - 1)]
            state.takeTurn(randomMove)

        return state.endValue

    def backPropagate(self, endValue, node):

        # Determine the win value to propagate back up. Child win values indicate the win chance for the
        # node who owns those children, so the values are reversed
        if node.state.turn == BLUE and endValue == 1:
            valueForThisNode = 0
        elif node.state.turn == GREEN and endValue == 0:
            valueForThisNode = 0
        elif endValue == 0.5:
            valueForThisNode = 0.5
        else:
            valueForThisNode = 1

        # Traverse tree by calling parents, incremented simulations and score
        while node is not self.root:
            node.sims += 1
            node.score += valueForThisNode
            node = node.parent
            valueForThisNode = 1 - valueForThisNode

        # Update root values to finish
        self.root.sims += 1
        self.root.score += valueForThisNode

    def updateWithTurn(self, move):

        # Find node with move in children list, then set the new root to that child
        for i in range(len(self.root.children)):
            if self.root.children[i].state.lastMove == move:
                self.newRoot = self.root.children[i]
                self.newRootReady = True

    # Debugging routine, used to print the tree, called recursively
    def printNodeChildren(self, node, header):

        header = header + "--"

        for i in range(len(node.children)):

            if node.children[i] is not None:
                print(header + str(node.children[i].state.lastMove) + " " +\
                      " Blue:" + str(node.children[i].state.pieces[BLUE]) + \
                      " Green:" + str(node.children[i].state.pieces[GREEN]) )
                self.printNodeChildren(node.children[i], header)

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

            # Run for a max of a million simulations, just because
            if 10000000 > self.root.sims:

                # Select most promising node to expand upon
                nodeToExpand = self.selectNodeToExpand(self.root)

                # Simulate game starting from that node, recording who won
                endValue = self.simulate(nodeToExpand)

                # Back propagate the result of that simulation through the tree
                self.backPropagate(endValue, nodeToExpand)

                # Just debugging code, leaving in for now but setting to False so it doesn't run
                if False:
                    for i in range(len(self.root.children)):

                        if self.root.children[i] is None:
                            continue

                        node = self.root.children[i]

                        print( str(node.state.lastMove) + \
                               " -- score:" + str(node.score) + \
                               " -- sims: " + str(node.sims) + \
                               " -- win%: " + str(node.getWinChance()) + \
                               " -- UCT: " + str(node.getUCT()) )

                    print("Best Move: " + str(self.root.getBestChild().state.lastMove) + \
                          " win%: " + str(self.root.getWinChance()) + \
                          " Turn: " + str(self.root.state.turn) + \
                          " Score: " + str(self.root.getScore()))
                    print("")

                #self.printNodeChildren(self.root, "")
                #print("")





