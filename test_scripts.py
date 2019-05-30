from ultimateboard import UTTTBoard, UTTTBoardDecision
from player import RandomTTTPlayer, RLTTTPlayer
from ultimateplayer import HumanUTTTPlayer, RandomUTTTPlayer, RLUTTTPlayer
from learning import NNUltimateLearning, TableLearning
from plotting import drawXYPlotByFactor
import os, csv
os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'
from game import GameSequence, SingleGame
import getpass
from time import gmtime, asctime

LEARNING_FILE = 'ultimate_player-' + getpass.getuser()+'-'+ '.h5'
WIN_PCT_FILE = 'win_pct_player-'+ getpass.getuser()+'-'+ asctime(gmtime())+ '.csv'

def playTTTAndPlotResults():
    learningPlayer = RLTTTPlayer()
    randomPlayer = RandomTTTPlayer()
    results = []
    numberOfSetsOfGames = 50
    for i in range(numberOfSetsOfGames):
        games = GameSequence(100, learningPlayer, randomPlayer)
        results.append(games.playGamesAndGetWinPercent())
    plotValues = {'X Win Fraction': zip(range(numberOfSetsOfGames), map(lambda x: x[0], results)),
                  'O Win Fraction': zip(range(numberOfSetsOfGames), map(lambda x: x[1], results)),
                  'Draw Fraction': zip(range(numberOfSetsOfGames), map(lambda x: x[2], results))}
    drawXYPlotByFactor(plotValues, 'Number of Sets (of 100 Games)', 'Fraction', title='RL Player (X) vs. Random Player (O)')

def playUltimateAndPlotResults():
    learningModel = NNUltimateLearning(UTTTBoardDecision)
    learningPlayer = RLUTTTPlayer(learningModel)
    randomPlayer = RandomUTTTPlayer()
    results = []
    numberOfSetsOfGames = 200
    if os.path.isfile(LEARNING_FILE):
        learningPlayer.loadLearning(LEARNING_FILE)
    for i in range(numberOfSetsOfGames):
        print "-----------------starting iteration ", str(i)
        games = GameSequence(100, learningPlayer, randomPlayer, BoardClass=UTTTBoard, BoardDecisionClass=UTTTBoardDecision)
        winpercent = games.playGamesAndGetWinPercent()
        results.append(winpercent)
    learningPlayer.saveLearning(LEARNING_FILE)
    writeResultsToFile(results)
    plotValues = {'X Win Fraction': zip(range(numberOfSetsOfGames), map(lambda x: x[0], results)),
                  'O Win Fraction': zip(range(numberOfSetsOfGames), map(lambda x: x[1], results)),
                  'Draw Fraction': zip(range(numberOfSetsOfGames), map(lambda x: x[2], results))}
    drawXYPlotByFactor(plotValues, 'Number of Sets (of 100 Games)', 'Fraction',title='RL Player (X) vs. Random Player (O)')

def playAgainstAgent():
    learningModel = NNUltimateLearning(UTTTBoardDecision)
    learningPlayer = RLUTTTPlayer(learningModel)
    humanPlayer = HumanUTTTPlayer()
    results = []
    numberOfSetsOfGames = 200
    if os.path.isfile(LEARNING_FILE):
        learningPlayer.loadLearning(LEARNING_FILE)
    else:
        print 'ERROR: no model found'
        return

    game = SingleGame(learningPlayer, humanPlayer, UTTTBoard, UTTTBoardDecision)
    game.playAGame()

def playUltimateForTraining():
    learningModel = TableLearning()
    learningPlayer = RLUTTTPlayer(learningModel)
    randomPlayer = RandomUTTTPlayer()
    results, tempFileName = [], 'temp_learning.json'
    for i in range(40):
        games = GameSequence(1000, learningPlayer, randomPlayer, BoardClass=UTTTBoard, BoardDecisionClass=UTTTBoardDecision)
        games.playGamesAndGetWinPercent()
        learningPlayer.saveLearning(tempFileName)
        results.append(os.path.getsize(tempFileName))
    print '\n'.join(map(str, results))
    os.remove(tempFileName)

def writeResultsToFile(results):
    with open(WIN_PCT_FILE, 'a') as outfile:
        for result in results:
            outfile.write('%s,%s,%s\n'%(result[0], result[1], result[2]))

def plotResultsFromFile(resultsFile):
    results = []
    with open(resultsFile, 'r') as infile:
        reader = csv.reader(infile)
        results = map(tuple, reader)
    numberOfSetsOfGames = len(results)
    plotValues = {'X Win Fraction': zip(range(numberOfSetsOfGames), map(lambda x: x[0], results)),
                  'O Win Fraction': zip(range(numberOfSetsOfGames), map(lambda x: x[1], results)),
                  'Draw Fraction': zip(range(numberOfSetsOfGames), map(lambda x: x[2], results))}
    drawXYPlotByFactor(plotValues, 'Number of Sets (of 100 Games)', 'Fraction', title='RL Player (X) vs. Random Player (O)')

def plotMemoryUsageFromFile(memoryFile):
    results = []
    with open(memoryFile, 'r') as infile:
        reader = csv.reader(infile)
        results = map(tuple, reader)
    plotValues = {'Memory Usage': zip(map(lambda x: x[1], results), map(lambda x: x[2], results))}
    drawXYPlotByFactor(plotValues, 'Number of Simulations', 'Memory Usage (MB)')

if __name__ == '__main__':
    #playTTTAndPlotResults()
    #playUltimateForTraining()
    #playUltimateAndPlotResults()
    playAgainstAgent()
    #plotResultsFromFile('win_pct_player_1.csv')
    #plotMemoryUsageFromFile('results/memory_scaling.csv')
