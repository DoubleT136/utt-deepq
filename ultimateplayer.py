from __future__ import division
from ultimateboard import UTTTBoardDecision, UTTTBoard
from learning import TableLearning
import random

class UTTTPlayer(object):
    def __init__(self):
        self.board = None
        self.player = None

    def setBoard(self, board, player):
        self.board = board
        self.player = player   # X or O

    def isBoardActive(self):
        return (self.board is not None and self.board.getBoardDecision() == UTTTBoardDecision.ACTIVE)

    def makeNextMove(self):
        raise NotImplementedError

    def learnFromMove(self, prevBoardState):
        raise NotImplementedError

    def startNewGame(self):
        pass

    def finishGame(self):
        pass

class RandomUTTTPlayer(UTTTPlayer):
    def makeNextMove(self):
        previousState = self.board.getBoardState()
        if self.isBoardActive():
            nextBoardLocation = self.board.getNextBoardLocation()
            if None in nextBoardLocation:
                activeBoardLocations = self.board.getActiveBoardLocations()
                nextBoardLocation = random.choice(activeBoardLocations)
            emptyPlaces = self.board.getEmptyBoardPlaces(nextBoardLocation)
            pickOne = random.choice(emptyPlaces)
            self.board.makeMove(self.player, nextBoardLocation, pickOne)
        return previousState

    def learnFromMove(self, prevBoardState):
        pass  # Random player does not learn from move

class RLUTTTPlayer(UTTTPlayer):
    def __init__(self, learningModel):
        self.learningAlgo = learningModel
        super(RLUTTTPlayer, self).__init__()
        self.epsilon = 1
        self.ep_step = 1/18000
        self.counter = 0

    def printValues(self):
        self.learningAlgo.printValues()

    def testNextMove(self, state, boardLocation, placeOnBoard):
        loc = 27*boardLocation[0] + 9*boardLocation[1] + 3*placeOnBoard[0] + placeOnBoard[1]
        boardCopy = list(state)
        boardCopy[loc] = self.player
        return ''.join(boardCopy)

    def startNewGame(self):
        self.learningAlgo.resetForNewGame()

    def finishGame(self):
        # update epsilon
        self.epsilon -= self.ep_step
        if(self.epsilon < 0):
            self.epsilon = 0
        self.counter += 1
        if self.counter == 200:
            print 'epsilon is ', self.epsilon
            self.counter = 0
        self.learningAlgo.gameOver()

    def makeNextMove(self):
        previousState = self.board.getBoardState()
        if self.isBoardActive():
            nextBoardLocation = self.board.getNextBoardLocation()
            activeBoardLocations = [nextBoardLocation]
            if None in nextBoardLocation:
                activeBoardLocations = self.board.getActiveBoardLocations()
            if random.uniform(0, 1) > self.epsilon:      # Make a random move with probability 0.2
                moveChoices = {}
                for boardLocation in activeBoardLocations:
                    emptyPlaces = self.board.getEmptyBoardPlaces(boardLocation)
                    for placeOnBoard in emptyPlaces:
                        possibleNextState = self.testNextMove(previousState, boardLocation, placeOnBoard)
                        moveChoices[(tuple(boardLocation), placeOnBoard)] = self.learningAlgo.getBoardStateValue(self.player, self.board, possibleNextState)
                (chosenBoard, pickOne) = max(moveChoices, key=moveChoices.get)
            else:
                chosenBoard = random.choice(activeBoardLocations)
                emptyPlaces = self.board.getEmptyBoardPlaces(chosenBoard)
                pickOne = random.choice(emptyPlaces)
            self.board.makeMove(self.player, chosenBoard, pickOne)

            #Update epsilon
        return previousState

    def learnFromMove(self, prevBoardState):
        self.learningAlgo.learnFromMove(self.player, self.board, prevBoardState)

    def saveLearning(self, filename):
        self.learningAlgo.saveLearning(filename)

    def loadLearning(self, filename):
        self.learningAlgo.loadLearning(filename)

if __name__  == '__main__':
    board = UTTTBoard()
    player1 = RandomUTTTPlayer()
    player2 = RLUTTTPlayer(TableLearning(UTTTBoardDecision))
