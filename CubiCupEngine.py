import sys
import time
import CubiCupMCTS


class Engine:

    # Initialize default values
    def __init__(self):
        self.bestMove = ""  # No initial random move
        self.gameSize = 0  # Game size isn't known yet
        self.mcts = None

    # Print the values we care about
    def printValues(self):
        if self.mcts is not None and self.mcts.root.getBestChild() is not None:
            output("Best Move:" + str(self.mcts.root.getBestChild().state.lastMove))  # print "Random Move:(x,y,z)"
            output("Score:" + str(self.mcts.root.getBestChild().getScore()))
            output("Simulations:" + str(self.mcts.root.sims))
            output("Game Size:" + str(self.gameSize))
            self.printReady = False  # printing is complete, indicate no more printing is needed

    # "subscribe:x" is used to tell the interfacing program which values this program will output
    def printValueDefinitions(self):
        output("subscribe:Best Move")
        output("subscribe:Score")
        output("subscribe:Simulations")
        output("subscribe:Gamesize")

    # Update the engine with some type of command
    # Currently implemented commands:
    #   newGame:x       -- start a new game with size x
    #   move:x,y,z      -- player has requested to place a piece at (x,y,z)
    def updateEngine(self, command):

        directives = command.split(":")  # split command string by ":"

        # If first part of command is "newGame"
        if directives[0] == "newGame":
            self.gameSize = int(directives[1])  # Set self.gameSize to the second part of the command
            if self.mcts is not None:
                self.mcts.indicateReset(self.gameSize)

        # If first part of command is "move"
        if directives[0] == "move":
            coords = directives[1].split(",")  # Split the second part of the command by "," to get x,y,z
            self.mcts.updateWithTurn((int(coords[0]), int(coords[1]), int(coords[2])))

    def runEngine(self):

        # Do nothing until game size is specified
        while self.gameSize == 0:
            time.sleep(0.1)
            continue

        # Create new mcts and start running it
        self.mcts = CubiCupMCTS.MCTS(self.gameSize)
        self.mcts.run()
        return


# Helper function to output a string. To interface with java, it seems we need the "sys.stdout.flush()",
# so using this function just makes the code a little prettier
def output(string):
    print(string)
    sys.stdout.flush()
