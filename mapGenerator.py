# this program is designed to generate a random path on a x * y tile map

# 3rd party libraries
import random

# Homemade
import constants

prevPoints = []


def refreshMap(rowLen, colLen):
    global prevPoints
    prevPoints = []
    # allows map of rowLen x colLen to be generated
    global myMap
    myMap = []
    for i in range(0, rowLen):
        myMap.append([])
        for x in range(0, colLen):
            myMap[i].append(0)
        # 0 represents 'dead' tiles - i.e. not path tiles


def updateHistory(lastPos):
    prevPoints.append(lastPos)


def genNewPoint(currPoint):
    global nextColumn
    global nextRow
    nextRow = currPoint[0]
    nextColumn = currPoint[1]
    if random.randint(0, 2) == 0:
        # could add this determination into genNewPoint,
        # but then determination would be random every time a new value is generated
        # changes the row
        if currPoint[0] == 0:
            nextRow = currPoint[0]+1
        elif currPoint[0] == len(myMap) - 1:
            nextRow = currPoint[0]-1
        else:
            if random.randint(0, 2) == 0:
                nextRow = currPoint[0]+1
            else:
                nextRow = currPoint[0]-1
        while nextRow == prevPoints[len(prevPoints) - 2]:
            genNewPoint()
    else:
        # changes the column
        nextColumn = currPoint[1]+1


def genMap():
    for cord in prevPoints:
        myMap[cord[0]][cord[1]] = 1


def createPath(startRow, startCol, endRow, endCol, type):
    currPoint = (startRow, startCol) # the first point is the random row at column 0
    updateHistory(currPoint) # a ledger/history is created to make sure movement isn't undone and to generate the map after
    while currPoint[1] < endCol: # while current column is less than the max column
        genNewPoint(currPoint)
        currPoint = (nextRow, nextColumn)
        updateHistory(currPoint)
    if type == 'add_path': # AKA additional path
        if currPoint[0] < endRow:
            while currPoint[0] < endRow:
                currPoint = ((currPoint[0])+1, currPoint[1])
                updateHistory(currPoint)
        else:
            while currPoint[0] > endRow:
                currPoint = ((currPoint[0])-1, currPoint[1])
                updateHistory(currPoint)
    genMap()


def addPaths():
    global startRow
    startCol = random.randint(1, 5)
    endCol = random.randint(14, 18)
    loop = 0
    for item in prevPoints:
        loop += 1
        if item[1] == startCol:
            startRow = prevPoints[loop][0]
            break
    loop = 0
    for item in prevPoints:
        loop += 1
        if item[1] == endCol:
            endRow = prevPoints[loop][0]
            break
    firstPathLength = len(prevPoints)
    createPath(startRow, startCol, endRow, endCol, 'add_path')
    # generate second branch (could make a function)
    startCol = random.randint(1, 5)
    endCol = random.randint(14, 18)
    loop = 0
    for item in prevPoints[0:firstPathLength]:
        loop += 1
        if item[1] == startCol:
            startRow = prevPoints[loop][0]
            break
    for item in prevPoints:
        loop += 1
        if item[1] == endCol:
            endRow = prevPoints[loop][0]
            break
    createPath(startRow, startCol, endRow, endCol, 'add_path')


def pathBranch():
    k = 0


def largerPath():
    k = 0


def plotTrees():
    global grassTiles
    # Spawn trees for forest feel
    treePos = {}
    dictKey = 0
    coordGrid = []
    # Generates coordinate grid of all points on the map
    for row in range(0, len(myMap)):
        for column in range(0, len(myMap[0])):
            coordGrid.append((row, column))
    # Grass tiles is all tiles that are grass
    grassTiles = [x for x in coordGrid if not x in prevPoints]
    # For each coordinate in grass tiles
    # TODO: switch to coord in grassTiles, not in range
    for coord in range(0, len(grassTiles)):
        # If there is a tree
        if random.randint(0, 1) == 0:
            treeFits = True
            for point in range(0, len(prevPoints)):
                if prevPoints[point][1] == grassTiles[coord][1]:
                    # Checks if the end ypos of the tree is in between any of the tile ypos on the same column
                    if (prevPoints[point][0] * constants.cellHeight) <= ((grassTiles[coord][0] * constants.cellHeight) + 60) <= ((prevPoints[point][0] * constants.cellHeight) + constants.cellHeight):
                        treeFits = False
                        break
            if treeFits:
                treeNum = random.randint(1, 4)
                treePos[dictKey] = grassTiles[coord][0], grassTiles[coord][1], treeNum
                dictKey += 1
    return treePos


def initAnimals():
    global grassTiles
    animalPos = {}
    dictKey = 0
    for coord in range(0, len(grassTiles)):
        # If there is a tree
        if random.randint(0, 10) == 0:
            animalFits = True
            for point in range(0, len(prevPoints)):
                if prevPoints[point][1] == grassTiles[coord][1]:
                    # Checks if the end ypos of the tree is in between any of the tile ypos on the same column
                    if (prevPoints[point][0] * constants.cellHeight) <= ((grassTiles[coord][0] * constants.cellHeight) + 60) <= ((prevPoints[point][0] * constants.cellHeight) + constants.cellHeight):
                        animalFits = False
                        break
            if animalFits:
                animalNum = random.randint(1, 4)
                animalPos[dictKey] = grassTiles[coord][0], grassTiles[coord][1], animalNum
                dictKey += 1
    return animalPos


def main():
    refreshMap(constants.mapRows, constants.mapColumns)
    mainStartRow = random.randint(5, len(myMap)-5)
    createPath(mainStartRow, 0, 'null', len(myMap[0])-1, 'first_path') # starting now is picked at random
    if mainStartRow < len(myMap)/2:
        newStartRow = int(mainStartRow + ((len(myMap)/2)-(random.randint(0, mainStartRow+1))))
    else:
        newStartRow = int(mainStartRow - ((len(myMap)/2)-(random.randint(0, mainStartRow+1))))
    # createPath(newStartRow, 0, 'null', len(myMap[0])-1, 'another_path')
    # end Row is random for the first path, so the placeholder is 'null'
    # while current column is less than the max column
    addPaths()
    treePos = plotTrees()
    animalPos = initAnimals()
    return myMap, mainStartRow, treePos, animalPos