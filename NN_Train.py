
import NN_player
import CubiCupGame
import numpy as np
import multiprocessing
import Network
from multiprocessing import Process

simsPerMove = 400
trainingSetGames = 2400
trainingLoop = 1
evaluationGames = 100
gameSize = 5


def self_play_single(numGames=trainingSetGames, modelName=None):

    # Get model from name, then get output function so predicts can be done quickly
    if modelName is not None:
        inputShape = (1, gameSize + 1, gameSize + 1, gameSize + 1)
        policyShape = (1, gameSize + 1, gameSize + 1, gameSize + 1)
        model = Network.getModel(modelName, inputShape, policyShape)
        outputFunc = Network.getOutputFunc(model)
    else:
        outputFunc = None

    games = []
    for i in range(numGames):

        game = CubiCupGame.Game(gameSize)

        selfPlayer = NN_player.Player(game, -1, simsPerMove, outputFunc)
        selfPlayer.play()

        print("Saving game: ", len(games))
        games.append(game)

    return games


def self_play(gameQueue, numGames=trainingSetGames, modelName=None):

    # Get model from name, then get output function so predicts can be done quickly
    if modelName is not None:
        inputShape = (1, gameSize + 1, gameSize + 1, gameSize + 1)
        policyShape = (1, gameSize + 1, gameSize + 1, gameSize + 1)
        model = Network.getModel(modelName, inputShape, policyShape)
        outputFunc = Network.getOutputFunc(model)
    else:
        outputFunc = None

    for i in range(numGames):

        game = CubiCupGame.Game(gameSize)

        selfPlayer = NN_player.Player(game, -1, simsPerMove, outputFunc)
        selfPlayer.play()

        gameQueue.put(game.history)
        #print(len(gameQueue))


def self_play_threaded(modelName=None):

    threads = 24#multiprocessing.cpu_count()

    if threads > trainingSetGames:
        threads = 1

    gamesPerThread = int(trainingSetGames / threads)
    games = []

    print("Playing threaded")
    print("Threads: ", threads, "  gamesPerThread: ", gamesPerThread)

    gameQueue = multiprocessing.Queue()

    gameThreads = []
    for i in range(threads):
        gameThreads.append(Process(target=self_play, args=(gameQueue, gamesPerThread, modelName)))
        gameThreads[i].start()

    processesAlive = True
    while processesAlive:

        try:
            gameToAdd = gameQueue.get_nowait()
            if gameToAdd is not None:
                print("Saving game: ", len(games))
                games.append(gameToAdd)
        except:
            pass

        processesAlive = False
        for i in range(threads):
            if gameThreads[i].is_alive():
                processesAlive = True
                break

    return games


def createSets(games):

    xTrain = []
    yTrain = []
    xTest = []
    yTest = []

    for i in range(len(games)):

        game = games[i]

        #scoreList = [[[game.endValue for x in range(gameSize + 1)] for y in range(gameSize + 1)] for z in range(gameSize + 1)]

        if i < len(games)*4/5:
            for element in game:
                xTrain.append(element[0].board)
                yTrain.append(element[1])
        else:
            for element in game:
                xTest.append(element[0].board)
                yTest.append(element[1])

    #print("training sets")
    #for i in range(len(xTrain)):
    #    print("x: " + str(xTrain[i]))
    #    print("y: " + str(yTrain[i]))

    #print("testing sets")
    #for i in range(len(xTest)):
    #    print("x: " + str(xTest[i]))
    #    print("y: " + str(yTest[i]))

    xTrain = np.array(xTrain)
    yTrain = np.array(yTrain)
    xTest = np.array(xTest)
    yTest = np.array(yTest)

    xTrain = xTrain.reshape((xTrain.shape[0], 1, xTrain.shape[1], xTrain.shape[2], xTrain.shape[3]))
    yTrain = yTrain.reshape((yTrain.shape[0], 1, yTrain.shape[1], yTrain.shape[2], yTrain.shape[3]))
    xTest = xTest.reshape((xTest.shape[0], 1, xTest.shape[1], xTest.shape[2], xTest.shape[3]))
    yTest = yTest.reshape((yTest.shape[0], 1, yTest.shape[1], yTest.shape[2], yTest.shape[3]))

    return xTrain, yTrain, xTest, yTest


def train():

    inputShape = (1, gameSize + 1, gameSize + 1, gameSize + 1)
    policyShape = (1, gameSize + 1, gameSize + 1, gameSize + 1)

    currentModelName = "currentModel_"+str(gameSize)+".h5"

    # Create self play games
    selfPlayGamesSave = self_play_threaded(modelName=None)
    #selfPlayGamesSave = self_play_single(modelName=currentModelName)

    # Creating sets from games
    xTrain, yTrain, xTest, yTest = createSets(selfPlayGamesSave)

    # Load current model, train it, then save it
    currentModel = Network.getModel(currentModelName, inputShape, policyShape)
    model = Network.trainResNet(xTrain, yTrain, xTest, yTest, currentModel)
    currentModel.save(currentModelName)

    xTestS = xTest[0].reshape(1, 1, xTest.shape[2], xTest.shape[3], xTest.shape[4])
    yTestS = yTest[0].reshape(1, 1, yTest.shape[2], yTest.shape[3], yTest.shape[4])
    Network.model_test(xTestS, yTestS, currentModel)


def evaluate():

    currentModelName = "currentModel_" + str(gameSize) + ".h5"
    bestModelName = "bestModel_" + str(gameSize) + ".h5"

    currentModel = Network.getModel(currentModelName)
    bestModel = Network.getModel(bestModelName)

    outputFuncCurrent = Network.getOutputFunc(currentModel)
    outputFuncBest = Network.getOutputFunc(bestModel)

    currentPlayerScore = 0

    # Half with current as blue
    for i in range(evaluationGames/2):
        game = CubiCupGame.Game(gameSize)

        currentPlayer = NN_player.Player(game, 0, simsPerMove, outputFuncCurrent)
        bestPlayer = NN_player.Player(game, 1, simsPerMove, outputFuncBest)
        currentPlayer.play()
        bestPlayer.play()

        if game.endValue == 1:
            currentPlayerScore = currentPlayerScore + 1
        elif game.endValue == 0:
            currentPlayerScore = currentPlayerScore + 0.5

    # Half with current as green
    for i in range(evaluationGames / 2):
        game = CubiCupGame.Game(gameSize)

        currentPlayer = NN_player.Player(game, 1, simsPerMove, outputFuncCurrent)
        bestPlayer = NN_player.Player(game, 0, simsPerMove, outputFuncBest)
        currentPlayer.play()
        bestPlayer.play()

        if game.endValue == -1:
            currentPlayerScore = currentPlayerScore + 1
        elif game.endValue == 0:
            currentPlayerScore = currentPlayerScore + 0.5

    if currentPlayerScore > evaluationGames/2:
        # Current player has won majority of games, they are the new best player
        currentModel.save(bestModelName)
        bestModel.save(currentModelName)


def main():

    for i in range(trainingLoop):
        # Create process that self plays and trains model, so this main process doesn't setup and tensorflow stuff
        trainProcess = Process(target=train)
        trainProcess.start()
        trainProcess.join()





# Call main()
main()


# evaluate network

# use new network against old one
# run a game with nn_current and the same game with nn_best
# take best predicted from game based on turn
# if new wins more than 55% of the time, it is considered the new best player


def notmain():

    import tensorflow as tf

    inputShape = (1, gameSize+1, gameSize+1, gameSize+1)
    policyShape = (1, gameSize+1, gameSize+1, gameSize+1)

    bestModelName = "bestModel_"+str(gameSize)+".h5"
    currentModelName = "currentModel_"+str(gameSize)+".h5"

    #bestModel = Network.getModel(bestModelName, inputShape, policyShape)

    for i in range(trainingLoop):

        # Gather self play games
        selfPlayGamesSave = self_play_threaded(modelName=currentModelName)
        #selfPlayGamesSave = self_play_single(modelName=currentModelName)
        #selfPlayGamesSave = self_play_single()

        # Create training and set test from those games, and train them with current network
        #xTrain, yTrain, xTest, yTest = createSets(selfPlayGamesSave)
        #currentModel = Network.getModel(currentModelName, inputShape, policyShape)
        #model = Network.trainResNet(xTrain, yTrain, xTest, yTest, currentModel)
        #currentModel.save(currentModelName)
        #tf.compat.v1.reset_default_graph()


    #currentModel.save(currentModelName)

    #xTestS = xTest[0].reshape(1, 1, xTest.shape[2], xTest.shape[3], xTest.shape[4])
    #yTestS = yTest[0].reshape(1, 1, yTest.shape[2], yTest.shape[3], yTest.shape[4])
    #Network.model_test(xTestS, yTestS, currentModel)