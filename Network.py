
import CubiCupDriver
import time


def lr_schedule(epoch):
    lr = 1e-3
    if epoch > 180:
        lr *= 0.5e-3
    elif epoch > 160:
        lr *= 1e-3
    elif epoch > 120:
        lr *= 1e-2
    elif epoch > 80:
        lr *= 1e-1
    #print('Learning rate: ', lr)
    return lr


def conv_layer(x, filters=16, kernel_size=3):

    from tensorflow.keras.layers import Conv3D
    from tensorflow.keras.layers import BatchNormalization, LeakyReLU
    from tensorflow.keras.regularizers import l2

    x = Conv3D(filters=filters,
               kernel_size=kernel_size,
               data_format="channels_first",
               padding='same',
               use_bias=False,
               activation='linear',
               kernel_regularizer=l2(1e-4))(x)

    x = BatchNormalization(axis=1)(x)
    x = LeakyReLU()(x)

    return x


def residual_layer(input_block, filters, kernel_size):

    from tensorflow.keras.layers import Conv3D
    from tensorflow.keras.layers import BatchNormalization, LeakyReLU
    from tensorflow.keras.regularizers import l2
    from tensorflow.keras.layers import add

    x = conv_layer(input_block, filters, kernel_size)

    x = Conv3D(filters=filters,
               kernel_size=kernel_size,
               data_format="channels_first",
               padding='same',
               use_bias=False,
               activation='linear',
               kernel_regularizer=l2(1e-4))(x)

    x = BatchNormalization(axis=1)(x)
    x = add([input_block, x])
    x = LeakyReLU()(x)

    return x


def policy_head(x, policy_shape):

    from tensorflow.keras.layers import Conv3D, BatchNormalization, LeakyReLU, Flatten, Reshape
    from tensorflow.keras.regularizers import l2
    from tensorflow.keras.activations import softmax

    x = Conv3D(filters=1,
               kernel_size=3,
               data_format="channels_first",
               padding='same',
               use_bias=False,
               activation='linear',
               kernel_regularizer=l2(1e-4))(x)

    x = BatchNormalization(axis=1)(x)
    x = LeakyReLU()(x)

    x = Flatten()(x)
    x = softmax(x, axis=-1)
    x = Reshape(policy_shape)(x)

    return x


def build_model(res_layers, input_shape, policy_shape):

    from tensorflow.keras.layers import Input
    from tensorflow.keras.models import Model

    inputs = Input(input_shape)

    x = conv_layer(inputs, filters=16, kernel_size=3)

    for i in range(res_layers):
        x = residual_layer(x, filters=16, kernel_size=3)

    outputs = policy_head(x, policy_shape)

    model = Model(inputs=inputs, outputs=outputs)

    return model


def getModel(name, inputShape=None, policyShape=None):

    from tensorflow.keras.optimizers import Adam
    from tensorflow.keras.models import load_model
    from tensorflow import nn
    from os import path
    import tensorflow as tf

    # Make tensorflow gpu memory consumption grow, rather than greedy allocate
    gpus = tf.config.experimental.list_physical_devices('GPU')
    if gpus:
        try:
            for gpu in gpus:
                tf.config.experimental.set_memory_growth(gpu, True)
        except RuntimeError as e:
            print(e)

    res_layers = 10

    if path.exists(name):
        print("Loading model: ", name)
        model = load_model(name, compile=False)
    else:
        print("Model " + name + " not found. Creating it now.")
        # Create the neural network if no model given
        model = build_model(res_layers=res_layers, input_shape=inputShape, policy_shape=policyShape)

    model.compile(loss=nn.softmax_cross_entropy_with_logits,
                  optimizer=Adam(lr=lr_schedule(0)),
                  metrics=['accuracy'])

    return model


def trainResNet(xTrain, yTrain, xTest, yTest, model):

    from tensorflow.keras.callbacks import LearningRateScheduler
    from tensorflow.keras.callbacks import ReduceLROnPlateau
    import numpy as np
    import time

    # Training parameters
    BATCH_SIZE = 128
    EPOCHS = 100

    start_time = time.time()

    # Prepare callbacks for model saving and for learning rate adjustment.
    lr_scheduler = LearningRateScheduler(lr_schedule)

    lr_reducer = ReduceLROnPlateau(factor=np.sqrt(0.1),
                                   cooldown=0,
                                   patience=5,
                                   min_lr=0.5e-6)

    callbacks = [lr_reducer, lr_scheduler]

    model.fit(xTrain, yTrain,
              batch_size=BATCH_SIZE,
              epochs=EPOCHS,
              validation_data=(xTest, yTest),
              shuffle=True,
              callbacks=callbacks)

    elapsed_time = time.time() - start_time
    print("Elapsed time: ", elapsed_time)

    return model


def getOutputFunc(model):

    import keras.backend as K

    get_output = K.function([model.layers[0].input], [model.layers[-1].output])
    return get_output


def getMoveProbs(state, outputFunc):

    import numpy as np

    #start_time = time.time()

    size = state.boardSize+1
    boardInput = np.array(state.board).reshape(1, 1, size, size, size)

    movePredictions = outputFunc([boardInput])[0]
    #movePredictions = model.predict(boardInput)  # slow version, output func is obtained through getOutputFunc(model)

    availableMoveProbs = []
    for move in state.availableMoves:
        x = move[0]
        y = move[1]
        z = move[2]
        availableMoveProbs.append(movePredictions[0][0][x][y][z])

    #print("a: ", state.availableMoves)
    #print("p: ", availableMoveProbs)

    #elapsed_time = time.time() - start_time
    #print("Elapsed time: ", elapsed_time)

    return availableMoveProbs


def model_test(xTest, yTest, model):

    availableMoves = []
    CubiCupDriver.getAvailableMoves(xTest[0][0], 5, availableMoves)

    yPredict = model.predict(xTest)

    print("yPredict: ", yPredict)
    print("yTest: ", yTest)

    availableMoveProbs = []
    for move in availableMoves:
        x = move[0]
        y = move[1]
        z = move[2]
        availableMoveProbs.append(yPredict[0][0][x][y][z])

    print("a: ", availableMoves)
    print("p: ", availableMoveProbs)

