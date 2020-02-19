import CubiCupDriver

from CubiCupDriver import BLUE
from CubiCupDriver import GREEN
from CubiCupDriver import EMPTY
from CubiCupDriver import addMoveToBoard
from CubiCupDriver import fill
from CubiCupDriver import getAvailableMoves

import pprint
import random

class State:

    def __init__(self,size):
        self.board = [[[EMPTY for x in range(size+1)] for y in range(size+1)] for z in range(size+1)]
        CubiCupDriver.getInitialBoard(size,self.board)

        totalPieces = size * (size+1) * (size+2) / 6;

        self.pieces = [0,0]

        if totalPieces%2 == 0:
           self.pieces[BLUE] = totalPieces / 2;
           self.pieces[GREEN] = totalPieces / 2;
        else:
           self.pieces[GREEN] = (totalPieces+1) / 2;
           self.pieces[GREEN] = (totalPieces-1) / 2;

        self.turn = BLUE
        self.gameOver = False
        self.boardSize = size
        self.availableMoves = []

        getAvailableMoves(self.board,self.boardSize,self.availableMoves)

    def takeTurn(self,x,y,z):

        if self.gameOver:
            return

        addMoveToBoard(self.board,x,y,z,self.turn)

        fill(self.board,x,y,z,self.turn,self.pieces)

        if self.turn == BLUE:
            self.turn = GREEN
        else:
            self.turn = BLUE

        self.availableMoves = []
        getAvailableMoves(self.board,self.boardSize,self.availableMoves)

        return self.availableMoves[random.randint(0,len(self.availableMoves)-1)]

        #pprint.pprint( self.availableMoves )
