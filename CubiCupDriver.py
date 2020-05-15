EMPTY = -2  # Empty cube spots are set to -2
BASE = -1  # Base cubes spots are set to -1
BLUE = 0  # Blue cubes spots are set to 0, this is also the array index for blue in pieces[]
GREEN = 1  # Blue cubes spots are set to 1, this is also the array index for green in pieces[]


# Fill board array with base cubes
def getInitialBoard(size, board):
    x = 0
    while x <= size:
        y = size - x
        z = 0
        while y >= 0:
            board[x][y][z] = BASE
            y -= 1
            z += 1
        x += 1


# Add move to board
def addMoveToBoard(board, x, y, z, turn, pieces):

    # this is commented out because moves are based on available ones, so they are
    # guaranteed to be legal, but I'll leave this in just in case we ever change that

    # cant play if top is full
    #if board[0][0][0] != EMPTY:
    #    return

    # cant play out of bounds
    #if x < 0 or y < 0 or z < 0:
    #    return

    # cant play if no cup to put piece in
    #if board[x + 1][y][z] == EMPTY or board[x][y + 1][z] == EMPTY or board[x][y][z + 1] == EMPTY:
    #    return

    # cant play unless open
    #if board[x][y][z] != EMPTY:
    #    return

    # move is legal, set board spot to whoever's turn it is
    board[x][y][z] = turn
    pieces[turn] -= 1


# Recursively fill cups, if any exist, until all are done or a player is out of pieces
def fill(board, x, y, z, lastTurnAdd, pieces):

    filled = False

    # Set fill value to opposite of last turn (BLUE = 0, GREEN = 1)
    thisTurnAdd = 1 - lastTurnAdd

    # If player filling cups has pieces remaining
    if pieces[thisTurnAdd] != 0:
        # If the piece added to x,y,z makes a valid cup in the -x direction
        if x > 0 and board[x - 1][y + 1][z] == board[x][y][z] and board[x - 1][y][z + 1] == board[x][y][z]:
            # Add the piece to fill the cup and decrement players pieces
            board[x - 1][y][z] = thisTurnAdd
            pieces[thisTurnAdd] -= 1
            filled = True

            # If other player still has pieces, see if adding this pieces created a cup they can fill
            if pieces[lastTurnAdd] != 0:
                fill(board, x - 1, y, z, thisTurnAdd, pieces)

    # If player filling cups has pieces remaining
    if pieces[thisTurnAdd] != 0:
        # If the piece added to x,y,z makes a valid cup in the -y direction
        if y > 0 and board[x + 1][y - 1][z] == board[x][y][z] and board[x][y - 1][z + 1] == board[x][y][z]:
            # Add the piece to fill the cup and decrement players pieces
            board[x][y - 1][z] = thisTurnAdd
            pieces[thisTurnAdd] -= 1
            filled = True

            # If other player still has pieces, see if adding this pieces created a cup they can fill
            if pieces[lastTurnAdd] != 0:
                fill(board, x, y - 1, z, thisTurnAdd, pieces)

    # If player filling cups has pieces remaining
    if pieces[thisTurnAdd] != 0:
        # If the piece added to x,y,z makes a valid cup in the -z direction
        if z > 0 and board[x + 1][y][z - 1] == board[x][y][z] and board[x][y + 1][z - 1] == board[x][y][z]:
            # Add the piece to fill the cup and decrement players pieces
            board[x][y][z - 1] = thisTurnAdd
            pieces[thisTurnAdd] -= 1
            filled = True

            # If other player still has pieces, see if adding this pieces created a cup they can fill
            if pieces[lastTurnAdd] != 0:
                fill(board, x, y, z - 1, thisTurnAdd, pieces)

    return filled


# Fill an array with the available moves, given a current board
def getAvailableMoves(board, size, moveList):
    depth = 0
    while depth <= size:    # Loop from top to bottom
        x = 0
        while x <= depth:   # Loop around x,y,z on each layer
            y = depth - x
            z = 0
            while y >= 0:
                # If all squares below are filled, and this one empty
                if board[x][y][z] == EMPTY and board[x + 1][y][z] != EMPTY \
                        and board[x][y + 1][z] != EMPTY and board[x][y][z + 1] != EMPTY:
                    # Add x,y,z to move list as tuple
                    moveList.append((x, y, z))
                y -= 1
                z += 1
            x += 1
        depth += 1


def updateAvailableMoves(board, moveList, lastMove):

    moveList.remove(lastMove)

    x = lastMove[0]
    y = lastMove[1]
    z = lastMove[2]

    # If the piece added to x,y,z makes a valid cup in the -x direction
    if x > 0 and board[x - 1][y + 1][z] != EMPTY and board[x - 1][y][z + 1] != EMPTY:
        # We created a cup, and therefore a move
        moveList.append((x-1, y, z))

    # If the piece added to x,y,z makes a valid cup in the -y direction
    if y > 0 and board[x + 1][y - 1][z] != EMPTY and board[x][y - 1][z + 1] != EMPTY:
        # We created a cup, and therefore a move
        moveList.append((x, y-1, z))

    # If the piece added to x,y,z makes a valid cup in the -z direction
    if z > 0 and board[x + 1][y][z - 1] != EMPTY and board[x][y + 1][z - 1] != EMPTY:
        # We created a cup, and therefore a move
        moveList.append((x, y, z-1))

