import pygame
import random
import colorsys

import constants
import mapGenerator
from mapGenerator import prevPoints


target = 'None'
pygame.init()
mainDisplay = pygame.display.set_mode((constants.mapColumns * constants.cellWidth, constants.mapRows * constants.cellHeight))
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
        if target == "None":
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


def playerButton(playerName, image, xpos, ypos, width, height):
    global playerSelection
    # This function provides the code for the buttons and their text for the select character page
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    if xpos + width > mouse[0] > xpos and ypos + height > mouse[1] > ypos:
        mainDisplay.blit(image, (xpos, ypos))
        # Creates a rectangle with the same dimensions of the image (with an alpha) to show that it is being hovered over
        rect = pygame.Surface((width, height), pygame.SRCALPHA, 32)
        rect.fill((211, 211, 211, 100))
        mainDisplay.blit(rect, (xpos, ypos))

        if click[0] == 1:
            # confirmOpen = True
            # Updates the playerSelection, if the user goes back, selection is reset to None in chooseCharacter
            playerSelection = playerName
            # while confirmOpen:
            #     for event in pygame.event.get():
            #         if event.type == pygame.QUIT:
            #             pygame.quit()
            #             exit()
            #         confirmX, confirmY = (constants.gameWidth-300)/2, (constants.gameHeight-200)/2
            #         pygame.draw.rect(mainDisplay, (255, 255, 255), (confirmX, confirmY, 300, 100))
            #         button("Confirm", constants.menuButtonFont, 15, (255, 255, 255), confirmX + 25, confirmY + 25, 100, 50, (0,0,0), (0,0,0), gameInitialize)
            #         button("Take Me Back", constants.menuButtonFont, 15, (255, 255, 255), confirmX + 25 + 150, confirmY + 25, 100, 50, (0,0,0), (0,0,0), chooseCharacter)
            #         pygame.display.flip()
    else:
        mainDisplay.blit(image, (xpos, ypos))


def chooseCharacter():
    global playerSelection
    chooseCharacter = True
    playerSelection = "None"
    while chooseCharacter:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
        mainDisplay.fill(constants.defaultColor)
        # Inits a list of possible player images
        playerOptions = [constants.wizardRaw, constants.archerRaw]
        # Final list includes images that have been reformatted
        playerOptionsFinal = []
        for player in playerOptions:
            # for each player image, transform the size to the predetermined size
            player = pygame.transform.scale(player, constants.characterImageSize)
            playerOptionsFinal.append(player)
        # Creates 2 image buttons that check for mouse hovering and clicks
        playerButton("Wizard", playerOptionsFinal[0], 0, 75, constants.characterImageSize[0], constants.characterImageSize[1])
        playerButton("Archer", playerOptionsFinal[1], 0, 275, constants.characterImageSize[0], constants.characterImageSize[1])
        # Runs loop if player was selected
        if playerSelection != "None":
            confirmOpen = True
            while confirmOpen:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        exit()
                    confirmX, confirmY = (constants.gameWidth - 300) / 2, (constants.gameHeight - 200) / 2
                    pygame.draw.rect(mainDisplay, (255, 255, 255), (confirmX, confirmY, 300, 100))
                    button("Confirm", constants.menuButtonFont, 15, (255, 255, 255), confirmX + 25, confirmY + 25, 100, 50,(0, 0, 0), (0, 0, 0), gameInitialize)
                    button("Take Me Back", constants.menuButtonFont, 15, (255, 255, 255), confirmX + 25 + 150, confirmY + 25, 100, 50, (0, 0, 0), (0, 0, 0), chooseCharacter)
                    pygame.display.flip()
        pygame.display.flip()
        if playerSelection != "None":
            # When a player is selected and confirmed, initialize game
            gameInitialize()


def button(text, font, textSize, textColor, xpos, ypos, width, height, colorL, colorD, action=None):
    # colorL is the idle button color, colorD is when it is hovered over
    # action refers to the function that the button calls
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    # Checks to see if the cursor is in the button's confines
    if xpos + width > mouse[0] > xpos and ypos + height > mouse[1] > ypos:
        pygame.draw.rect(mainDisplay, colorD, (xpos, ypos, width, height))

        if click[0] == 1 and action is not None:
            action()
    else:
        pygame.draw.rect(mainDisplay, colorL, (xpos, ypos, width, height))

    myFont = pygame.font.SysFont(font, textSize)
    textSurf = myFont.render(text, False, textColor)
    textRect = textSurf.get_rect()
    textRect = textRect.move((xpos + ((width-textRect.width)/2)), (ypos + (height-textRect.height)/2))
    mainDisplay.blit(textSurf, textRect)


def mainMenu():
    mainMenu = True
    while mainMenu:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                mainMenu = False
        # Takes the desired background image and stretches it to the screen size
        backgroundImage = pygame.transform.scale(constants.menuBackground, constants.displaySize)
        # Displays background image
        mainDisplay.blit(backgroundImage, (0, 0))
        # Creates four buttons, all with different text, functions, and y positions
        button("Start", constants.menuButtonFont, constants.menuButtonFontSize, (0, 0, 0), (constants.displaySize[0]-constants.menuButtonWidth)/2, 175, constants.menuButtonWidth, constants.menuButtonHeight, constants.menuButtonColorLight, constants.menuButtonColorDark, chooseCharacter)
        button("Resume", constants.menuButtonFont, constants.menuButtonFontSize, (0, 0, 0), (constants.displaySize[0]-constants.menuButtonWidth)/2, 250, constants.menuButtonWidth, constants.menuButtonHeight, constants.menuButtonColorLight, constants.menuButtonColorDark)
        button("Options", constants.menuButtonFont, constants.menuButtonFontSize, (0, 0, 0), (constants.displaySize[0]-constants.menuButtonWidth)/2, 325, constants.menuButtonWidth, constants.menuButtonHeight, constants.menuButtonColorLight, constants.menuButtonColorDark)
        button("About", constants.menuButtonFont, constants.menuButtonFontSize, (0, 0, 0), (constants.displaySize[0]-constants.menuButtonWidth)/2, 400, constants.menuButtonWidth, constants.menuButtonHeight, constants.menuButtonColorLight, constants.menuButtonColorDark)
        # Updates the display
        pygame.display.flip()
    pygame.quit()
    exit()


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


def selectPlayer(mainStartRow):
    if playerSelection == "Wizard":
        # Generates wizard as player if that is selected
        return Creatures(mainStartRow, 0, "Wizard", constants.wizard, 'player', 3, 7, 5, 14)
    elif playerSelection == "Warrior":
        # Generates warrior as player if that is selected
        return Creatures(mainStartRow, 0, "Warrior", constants.warrior, 'player', 3, 7, 5, 14)
    elif playerSelection == "Assassin":
        # Generates assassin as player if that is selected
        return Creatures(mainStartRow, 0, "Assassin", constants.assassin, 'player', 3, 7, 5, 14)
    elif playerSelection == "Archer":
        # Generates archer as player if that is selected
        return Creatures(mainStartRow, 0, "Archer", constants.archer, 'player', 3, 7, 5, 14)


def gameInitialize():
    global mainDisplay, gameMap, player, gameObjects
    gameMap, mainStartRow = mapGenerator.main() # returns map and mainStartRow (initial path start row)
    gameObjects = []
    # TODO: Factor in the selected player
    player = selectPlayer(mainStartRow)
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
    gameMain()


if __name__ == '__main__':
    mainMenu()