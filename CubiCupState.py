import CubiCupDriver

from CubiCupDriver import BLUE
from CubiCupDriver import GREEN
from CubiCupDriver import EMPTY
from CubiCupDriver import addMoveToBoard
from CubiCupDriver import fill
from CubiCupDriver import getAvailableMoves
import copy


class State:

    def __init__(self, size, stateToCopy=None):

        if stateToCopy is not None:
            # If state to copy is specified, copy all the stuff from it
            self.board = copy.deepcopy(stateToCopy.board)
            self.pieces = copy.deepcopy(stateToCopy.pieces)
            self.turn = stateToCopy.turn
            self.gameOver = stateToCopy.gameOver
            self.endValue = stateToCopy.endValue
            self.boardSize = stateToCopy.boardSize
            self.availableMoves = copy.deepcopy(stateToCopy.availableMoves)
            self.lastMove = stateToCopy.lastMove
        else:
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
            self.endValue = None
            self.boardSize = size  # Set board size
            self.lastMove = None
            self.availableMoves = []  # Create array for available moves

            # Determine which moves are available, given the current board state
            getAvailableMoves(self.board, self.boardSize, self.availableMoves)

        self.checkForEnd()

    # Take a turn, adding a cube to position x,y,z
    def takeTurn(self, move):

        # Don't do anything if game is over
        if self.gameOver:
            return

        # Get x,y,z from move tuple
        x = move[0]
        y = move[1]
        z = move[2]

        # Add move to the board
        addMoveToBoard(self.board, x, y, z, self.turn, self.pieces)

        # Fill cups that may have been created
        fill(self.board, x, y, z, self.turn, self.pieces)

        # Change turn, since someone just moved
        if self.turn == BLUE:
            self.turn = GREEN
        else:
            self.turn = BLUE

        self.checkForEnd()

        # Clear the available moves array, and fill it with the new available moves
        self.availableMoves = []
        getAvailableMoves(self.board, self.boardSize, self.availableMoves)

        self.lastMove = move

    def checkForEnd(self):

        if self.board[0][0][0] != EMPTY:
            if self.board[1][0][0] == self.board[0][1][0] and self.board[1][0][0] == self.board[0][0][1] \
                    and self.board[0][0][0] != self.board[1][0][0]:

                # this is a tie
                self.endValue = 0.5
            else:
                if self.board[0][0][0] == BLUE:
                    # blue wins
                    self.endValue = 1
                else:
                    # green wins
                    self.endValue = 0
            self.gameOver = True
        else:

            if self.pieces[BLUE] == 0 and self.turn == BLUE:
                # green wins
                self.endValue = 0
                self.gameOver = True
            elif self.pieces[GREEN] == 0 and self.turn == GREEN:
                # blue wins
                self.endValue = 1
                self.gameOver = True
