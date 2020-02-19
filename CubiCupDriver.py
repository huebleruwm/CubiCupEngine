
import pprint

EMPTY = -2;
BASE = -1;
BLUE = 0;
GREEN = 1;

def getInitialBoard(size,board):
    x = 0
    while x <= size:
        y = size-x
        z = 0
        while y >= 0:
            board[x][y][z] = BASE
            y -= 1
            z += 1
        x += 1


def addMoveToBoard(board,x,y,z,turn):

    # cant play if top is full
    if board[0][0][0] != EMPTY:
        return

    # cant play out of bounds
    if x < 0 or y < 0 or z < 0:
        return

    # cant play if no cup to put piece in
    if board[x+1][y][z] == EMPTY or board[x][y+1][z] == EMPTY or board[x][y][z+1] == EMPTY:
        return

    # cant play unless open
    if board[x][y][z] != EMPTY:
        #print("spot in use")
        return

    # move is legal
    board[x][y][z] = turn


#recursively fill cups, if any exist, until all are done or a player is out of pieces
def fill(board,x,y,z,lastTurnAdd,pieces):

    # set fill value to opposide of last turn
    thisTurnAdd = 1-lastTurnAdd

    if pieces[thisTurnAdd] != 0:
        if x > 0 and board[x-1][y+1][z] == board[x][y][z] and board[x-1][y][z+1] == board[x][y][z]:
            board[x - 1][y][z] = thisTurnAdd
            pieces[thisTurnAdd] -= 1

            if pieces[lastTurnAdd] != 0:
                #other player can still fill
                fill(board,x-1,y,z,thisTurnAdd,pieces)

    if pieces[thisTurnAdd] != 0:
        if y > 0 and board[x+1][y-1][z] == board[x][y][z] and board[x][y-1][z+1] == board[x][y][z]:
            board[x][y-1][z] = thisTurnAdd
            pieces[thisTurnAdd] -= 1

            if pieces[lastTurnAdd] != 0:
                #other player can still fill
                fill(board,x, y - 1, z, thisTurnAdd,pieces)

    if pieces[thisTurnAdd] != 0:
        if z > 0 and board[x+1][y][z-1] == board[x][y][z] and board[x][y+1][z-1] == board[x][y][z]:
            board[x][y][z - 1] = thisTurnAdd
            pieces[thisTurnAdd] -= 1

            if pieces[lastTurnAdd] != 0:
                #other player can still fill
                fill(board,x, y, z - 1, thisTurnAdd,pieces);


def getAvailableMoves(board,size,moveList):

    depth = 0
    while depth <= size:
        x = 0
        while x <= depth:
            y = depth-x
            z = 0
            while y >= 0:
                # if all squares below are filled, and this one empty
                if board[x][y][z] == EMPTY and board[x+1][y][z] != EMPTY \
                   and board[x][y+1][z] != EMPTY and board[x][y][z+1] != EMPTY:
                   moveList.append( (x,y,z) )
                   #print("move " + str((x,y,z)) + " allowed")
                y -= 1
                z += 1
            x += 1
        depth += 1















    #
