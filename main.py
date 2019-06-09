import pygame
import random
import colorsys

import constants
import mapGenerator
from mapGenerator import prevPoints


target = 'None'
# TODO

class ObjActor:
    def __init__(self, row, column, name, sprite, classType):
        self.row = row
        self.column = column
        self.name = name
        self.sprite = sprite
        self.classType = classType
        # Class type can be enemy or player

    def draw(self):
        mainDisplay.blit(self.sprite, (self.column*constants.cellWidth, self.row*constants.cellHeight))

    def move(self, dr, dc):
        canMove = True
        if 0 <= (self.row + dr) < (len(gameMap)) and 0 <= (self.column + dc) < len(gameMap[0]):
            if gameMap[self.row + dr][self.column + dc] == 1:
                nextTile = (self.row + dr, self.column + dc)
                for object in gameObjects[1:]:
                    if nextTile == (object.row, object.column):
                        canMove = False
                        break
                if canMove:
                    self.row += dr
                    self.column += dc


class Creatures(ObjActor):
    # creatures have speed, strength, defense, and health
    # they can receive and dish damage and can die
    # sub class of actor
    def __init__(self, row, column, name, sprite, classType, speed, strength, defense, health):
        super().__init__(row, column, name, sprite, classType)
        self.speed = speed
        self.strength = strength
        self.defense = defense
        self.maxhealth = health
        # .maxhealth won't change while health will
        self.health = health

    def dodge(self, speed):
        speed = self.speed
        if random.randint(0, 101) <= (speed*5):
            # dodge = True
            return True
        else:
            # dodge = False
            return False

    def takeDamage(self, damage):
        defense = self.defense
        dodge = self.dodge(self.speed)
        if not dodge:
            self.health -= damage
            if self.health <= 0:
                self.death()
                print(self.name + " has perished in battle.")
            else:
                print(self.name + " took " + str(damage)+" damage.")
                print(self.name + " has " + str(self.health) + " health remaining.")
        else:
            print(self.name + " dodged the attack.")
        # TODO: implement way to consider defense/give defense an effect

    def attack(self, strength):
        global target
        target = 'None'
        # TODO: Refactor this (below)
        for object in gameObjects[1:]:
            # checks enemy to the bottom
            if (self.row+1, self.column) == (object.row, object.column):
                target = object
                break
            # checks enemy above
            elif (self.row-1, self.column) == (object.row, object.column):
                target = object
                break
            # checks enemy to the right
            elif (self.row, self.column+1) == (object.row, object.column):
                target = object
                break
            # checks enemy to the left
            elif (self.row, self.column-1) == (object.row, object.column):
                target = object
                break
            else:
                return
        damage = strength
        # FOR NOW: damage = strength
        dodge = target.dodge(target.speed)
        if not dodge:
            target.takeDamage(damage)
            if target.health >= 0:
                # Damage is equal to target's strength
                # Could assign local var here and create formula
                self.takeDamage(target.strength)
        else:
            print(target.name + " dodged the attack.")
            if target.health >= 0:
                self.takeDamage(target.strength)
        # TODO: implement way to consider defense/give defense an effect

    def death(self):
        # maybe add player and enemy death functions (separate)
        count = -1
        for object in gameObjects:
            count += 1
            if object.health <= 0:
                deadIndex = count
                del gameObjects[deadIndex]
                break
        for object in gameObjects:
            object.draw()

    def createHealthBar(self):
        # creates health bar using maxhealth, health, and position (row, column)
        if self.health > 0:
            maxHealth = self.maxhealth
            currentHealth = self.health
            width = int(constants.spriteWidth * (currentHealth/maxHealth))
            percentage = width/constants.spriteWidth
            # pixel = row, column
            creatureLocation = (self.column * constants.cellHeight, self.row * constants.cellWidth)
            lineStart = (creatureLocation[0], creatureLocation[1]-constants.cellHeight/3)
            lineEnd = (creatureLocation[0]+width, lineStart[1])
            # gets pixel location of creature
            h, s, v = 0.33 * percentage, 1, 1
            r, g, b = colorsys.hsv_to_rgb(h, s, v)
            color = [int(255*r), int(255*g), int(255*b)]
            pygame.draw.line(mainDisplay, color, lineStart, lineEnd, 10)
        else:
            k=0


def initMap(gameMap):
    for row in range(0, constants.mapRows):
        for column in range(0, constants.mapColumns):
            if gameMap[row][column] == 1:  # checks if there is a path
                mainDisplay.blit(constants.path, (column * constants.cellWidth, row * constants.cellHeight))
            else:
                mainDisplay.blit(constants.forest, (column * constants.cellWidth, row * constants.cellHeight))


def drawGame():
    global mainDisplay
    # clear the surface
    mainDisplay.fill(constants.defaultColor)
    initMap(gameMap)
    # draw all objects
    for object in gameObjects:
        object.draw()
    player.createHealthBar()
    if not (target == 'None'):
        target.createHealthBar()
    # player.createHealthBar()
    # update the display
    pygame.display.flip()


def gameMain():
    gameQuit = False
    while not gameQuit:
        playerAction = "no-action"
        playerAction = handleKeys()
        if playerAction == "quit":
            gameQuit = True
        drawGame()
    pygame.quit()
    exit()


def handleKeys():
    # get player input
    events_list = pygame.event.get()
    for event in events_list:  # loop through all events that have happened
        if event.type == pygame.QUIT:
            # quit attribute - someone closed window
            return "quit"
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                player.move(-1, 0)
                return "player-moved"
            if event.key == pygame.K_DOWN:
                player.move(1, 0)
                return "player-moved"
            if event.key == pygame.K_RIGHT:
                player.move(0, 1)
                return "player-moved"
            if event.key == pygame.K_LEFT:
                player.move(0, -1)
                return "player-moved"
            if event.key == pygame.K_a:
                player.attack(player.strength)
                return "player-attacked"
    return "no-action"


def gameInitialize():
    global mainDisplay, gameMap, player, gameObjects
    pygame.init()
    mainDisplay = pygame.display.set_mode((constants.mapColumns * constants.cellWidth, constants.mapRows * constants.cellHeight))
    results = mapGenerator.main() # returns map and mainStartRow (initial path start row)
    gameMap = results[0] # saves map to gameMap
    gameObjects = []
    player = Creatures(results[1], 0, "Wizard", constants.wizard, 'player', 3, 7, 5, 14)
    gameObjects.append(player)
    # starts the player at (mainStartRow, 0)
    # TODO: refactor spawning
    adjacent = False
    for cord in prevPoints[3:]:
        # spawns skeleton with a 10% chance per tile
        if not adjacent:
            if random.randint(0, 101) <= 10:
                adjacent = True
                # sets adjacent to True so enemies cannot spawn next to directly next to each other
                # (technically can since only works for one tile)
                gameObjects.append(Creatures(cord[0], cord[1], "Skeleton", constants.skeleton, 'enemy', 2, 2, 5, 8))
                # adds enemy to object list (will be drawn in gameDraw())
                continue
        if adjacent:
            adjacent = False
            # TODO spawn other enemies
            # figure out leveling sometime (enemies depend on level)


if __name__ == '__main__':
    gameInitialize()
    gameMain()
