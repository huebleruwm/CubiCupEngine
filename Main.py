#!/usr/bin/python

import time
import threading
import CubiCupEngine

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
        time.sleep(.2)                 # Sleep for a little bit to not suck processor time
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


# Call "main()"
main()
