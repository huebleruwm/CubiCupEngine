#!/usr/bin/python

import time
import threading
import CubiCupEngine
import sys
import CubiCupMCTS

# Create engine object
engine = CubiCupEngine.Engine()


# Function to handle input to python program
def inputHandler():

    # Loop forever
    while True:
        command_input = input()                 # Get input, should be a command we recognize
        engine.updateEngine(command_input)      # Send command to engine


# Function to handle output from python program
def outputHandler():

    engine.printValueDefinitions()      # Start by outputting definitions, which are the names of
                                        # values we care about (ie. bestMove:x,y,z)

    # Loop forever
    while True:
        time.sleep(.1)                 # Sleep for a little bit to not suck processor time
        #if engine.printIsReady():       # If the engine is ready to output something
        engine.printValues()        # output whatever the engine wants to


# Main function to start the python code
def main():

    # Create a thread to handle input sent to the program
    inputThread = threading.Thread(target=inputHandler)     # Tell the new thread to call "inputHandler"
    inputThread.daemon = True                               # Tell the thread to stop once the program is killed
    inputThread.start()                                     # Start the new thread

    outputThread = threading.Thread(target=outputHandler)   # Tell the new thread to call "outputHandler"
    outputThread.daemon = True                              # Tell the thread to stop once the program is killed
    outputThread.start()                                    # Start the new thread

    engine.runEngine()

    # The main thread only sleeps for now.
    # In the future, the main thread should run the engine by calling engine.run(), or something similar
    while True:
        print("Sleeping")
        time.sleep(5)


# Call "main()"
main()
