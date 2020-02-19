import sys

import CubiCupState

class Engine:

    # Initialize default values
    def __init__(self):
        self.randMove = ""          # No initial random move
        self.gameSize = 0           # Game size isn't known yet
        self.printReady = False     # We're not ready to print yet
        self.gameState = None       # No game started

    # Print the values we care about
    def printValues(self):
        output( "Random Move:" + str(self.randMove) )   # print "Random Move:(x,y,z)"
        output( "GameSize:" + str(self.gameSize) )      # print "GameSize:n"
        self.printReady = False                         # printing is complete, indicate no more printing is needed


    # "subscribe:x" is used to tell the interfacing program which values this program will output
    def printValueDefinitions(self):
        output( "subscribe:Random Move" )   # we will output "Random Move" values
        output( "subscribe:GameSize" )      # we will output "GameSize" values

    # Returns true if self.printReady = true
    def printIsReady(self):
        return self.printReady

    # Update the engine with some type of command
    # Currently implemented commands:
    #   newGame:x       -- start a new game with size x
    #   move:x,y,z      -- player has requested to place a piece at (x,y,z)
    def updateEngine(self,input):

        directives = input.split(":")   # split command string by ":"

        # If first part of command is "newGame"
        if directives[0] == "newGame":
            self.gameSize = int(directives[1])                  # Set self.gameSize to the second part of the command
            self.printReady = True                              # Set printReady to true, so we know we're ready to update our values, specifically self.gameSize

            self.gameState = CubiCupState.State(self.gameSize)  # Create a new CubiCupState.state object, this tracks the state of the game
                                                                # In the future, we will want this to update the MCTS, so that it knows
                                                                # a new game started, and it can change the root node of the tree

        # If first part of command is "move"
        if directives[0] == "move":
            coords = directives[1].split(",")   # Split the second part of the command by "," to get x,y,z

            self.randMove = self.gameState.takeTurn( int(coords[0]), int(coords[1]), int(coords[2]) )   # Update game state by calling the "takeTurn" function, which
                                                                                                        # returns a random move for testing puroses, in the future we
                                                                                                        # should send these coordinates to the MCTS so that it can update the
                                                                                                        # root node of the tree

            self.printReady = True  # Set printReady to true, so we know we're ready to update our values, specifically self.randMove


    # Does nothing for now, the plan for the future is:
    #   1. wait until a game size is specified
    #   2. start the MCTS
    #   3. start exploring the tree (eventually integrated with a machine learning algorithm)
    #   4. if a new best move is found, output it
    def runEngine(self):
        return

# Helper function to output a string. To interface with java, it seems we need the "sys.stdout.flush()",
# so using this function just makes the code a little prettier
def output(string):
    print( string )
    sys.stdout.flush()
