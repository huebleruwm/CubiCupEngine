import CubiCupDriver

from CubiCupDriver import BLUE
from CubiCupDriver import GREEN
from CubiCupDriver import EMPTY
from CubiCupDriver import addMoveToBoard
from CubiCupDriver import fill
from CubiCupDriver import getAvailableMoves
import random

"""
We probably want to change a lot of this. The nodes in the MCTS algorithm need a state, which is what this
is supposed to be. But currently, when the state is created, it's as if a new game is created.

A better way of doing this might be to use a state to create a new state after a move is made. So we 
would need a function like "getStateAfter( move )" which returns a new state. So we could use it like 
newState = currentState.getStateAfter( x, y, z ). This would require the __init__ fuction to be different, 
and we would need another function such as newGame to set the state up as a new game, since that
functionality is still needed. 
"""


class State:

    def __init__(self, size):

        # Create (size+1)^3 array
        self.board = [[[EMPTY for x in range(size + 1)] for y in range(size + 1)] for z in range(size + 1)]

        # Use the driver(rules) to set the initial board values, just filling in the base cubes
        CubiCupDriver.getInitialBoard(size, self.board)

        # Calculate the total number of pieces for the game
        totalPieces = size * (size + 1) * (size + 2) / 6

        # Create array to specify each players remaining pieces
        self.pieces = [0, 0]

        # Set the initial number of pieces for each player
        if totalPieces % 2 == 0:
            # If even total pieces, split evenly
            self.pieces[BLUE] = totalPieces / 2
            self.pieces[GREEN] = totalPieces / 2
        else:
            # If odd total pieces, give blue the extra
            self.pieces[BLUE] = (totalPieces + 1) / 2
            self.pieces[GREEN] = (totalPieces - 1) / 2

        self.turn = BLUE  # Blue gets first turn
        self.gameOver = False  # Game doesn't start out over
        self.boardSize = size  # Set board size
        self.availableMoves = []  # Create array for available moves

        # Determine which moves are available, given the current board state
        getAvailableMoves(self.board, self.boardSize, self.availableMoves)

    # Take a turn, adding a cube to position x,y,z
    def takeTurn(self, x, y, z):

        # Don't do anything if game is over
        if self.gameOver:
            return

        # Add move to the board
        addMoveToBoard(self.board, x, y, z, self.turn)

        # Fill cups that may have been created
        fill(self.board, x, y, z, self.turn, self.pieces)

        # Change turn, since someone just moved
        if self.turn == BLUE:
            self.turn = GREEN
        else:
            self.turn = BLUE

        # Clear the available moves array, and fill it with the new available moves
        self.availableMoves = []
        getAvailableMoves(self.board, self.boardSize, self.availableMoves)

        # Return a random available move
        return self.availableMoves[random.randint(0, len(self.availableMoves) - 1)]
