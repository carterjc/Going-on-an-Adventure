import pygame
import random
import colorsys
import time
import constants
import mapGenerator
import pickle
from threading import Timer

pygame.mixer.pre_init(44100, 16, 2, 4096)
target = 'None'
pygame.init()
mainDisplay = pygame.display.set_mode((constants.mapColumns * constants.cellWidth, constants.mapRows * constants.cellHeight))
newGame = False
pygame.display.set_icon(constants.gameIcon)


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
    def __init__(self, row, column, name, sprite, classType, speed, strength, defense, health, currXP=0, neededXP=0, level=0, XPGiven=0, forestPos=0, enemiesKilled=0):
        # XP Given is for non-players
        super().__init__(row, column, name, sprite, classType)
        self.speed = speed
        self.strength = strength
        self.defense = defense
        self.maxhealth = health
        # .maxhealth won't change while health will
        self.health = health
        self.currXP = int(currXP)
        self.neededXP = int(neededXP)
        self.level = level
        self.XPGiven = XPGiven
        self.forestPos = forestPos
        self.enemiesKilled = enemiesKilled

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
            drawGame()
            if self.health <= 0:
                if self.classType == "enemy":
                    self.gainXP()
                    player.enemiesKilled += 1
                    self.death()
                if self.classType == "player":
                    print(self.name + " has perished in battle.")
                    deathScreen()
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
            if target.health > 0:
                # Damage is equal to target's strength
                # Could assign local var here and create formula
                self.takeDamage(target.strength)
        else:
            print(target.name + " dodged the attack.")
            if target.health > 0:
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
                print(self.name + " has perished in battle.")
                return

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
            return

    def levelUP(self):
        # Checks if the player can level up and does so if true
        if self.currXP >= self.neededXP:
            extraXP = self.currXP - self.neededXP
            self.level += 1
            self.currXP = 0
            self.currXP += extraXP
            self.neededXP = ((self.level/.5)**2)+96
            upgradeScreen()
        else:
            return

    def displayXPBar(self):
        width = constants.displaySize[0]*.5
        height = constants.displaySize[1]*.1
        xpos = (constants.displaySize[0]-width)/2
        ypos = constants.displaySize[1]*.1
        color = (0, 0, 0)
        # XPBar rect is drawn first so there is a black outline
        percentageFilled = self.currXP / self.neededXP
        XPcolor = (77, 170, 87)
        XPRect = pygame.draw.rect(mainDisplay, XPcolor, (xpos, ypos, min(width * percentageFilled, width), height))
        mainXPRect = pygame.draw.rect(mainDisplay, color, (xpos, ypos, width, height), 1)

    def gainXP(self):
        # Allows the player to gain XP from killing an enemy
        # Self refers to the enemy (called from the take damage procedure) - global player is also called
        player.currXP += int(self.XPGiven)
        print(str(player.name) + " received " + str(self.XPGiven) + " XP!")
#         TODO: Cool animation?

    def levelReset(self, mainStartRow):
        # for player to reset col pos, but not currXP
        self.column = 0
        self.row = mainStartRow
        self.health = self.maxhealth

    def upgradeSpeed(self):
        self.speed += 1
        print("You have upgraded your speed by one! You now have a speed of " + str(player.speed) + "!")
        upgradeScreen(False)

    def upgradeStrength(self):
        self.strength += 1
        print("You have upgraded your strength by one! You now have a strength of " + str(player.strength) + "!")
        upgradeScreen(False)

    def upgradeDefense(self):
        self.defense += 1
        print("You have upgraded your defense by one! You now have a defense of " + str(player.defense) + "!")
        upgradeScreen(False)

    def upgradeHealth(self):
        self.maxhealth += 3
        print("You have upgraded your health by three! You now have " + str(player.maxhealth) + " health!")
        upgradeScreen(False)


def upgradeScreen(upgrade=True):
    while upgrade:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            upgrade_screenWidth = int(constants.displaySize[0]*.6)
            upgrade_screenHeight = int(constants.displaySize[1]*.4)
            xpos = (constants.displaySize[0] - upgrade_screenWidth)/2
            ypos = (constants.displaySize[1] - upgrade_screenHeight)/2
            color = (211, 211, 211)
            upgrade_screen = pygame.draw.rect(mainDisplay, color, (xpos, ypos, upgrade_screenWidth, upgrade_screenHeight))
            textColor = (0, 0, 0)
            button("Upgrade Speed", constants.menuButtonFont, 15, textColor, xpos + (upgrade_screenWidth*.1), ypos + (upgrade_screenHeight*.2), constants.menuButtonWidth, constants.menuButtonHeight, constants.menuButtonColorLight, constants.menuButtonColorDark, player.upgradeSpeed)
            button("Upgrade Strength", constants.menuButtonFont, 15, textColor, xpos + (upgrade_screenWidth/2) + (upgrade_screenWidth*.1), ypos + (upgrade_screenHeight*.2), constants.menuButtonWidth, constants.menuButtonHeight, constants.menuButtonColorLight, constants.menuButtonColorDark, player.upgradeStrength)
            button("Upgrade Defense", constants.menuButtonFont, 15, textColor, xpos + (upgrade_screenWidth*.1), ypos + ((upgrade_screenHeight*.8)-constants.menuButtonHeight), constants.menuButtonWidth, constants.menuButtonHeight, constants.menuButtonColorLight, constants.menuButtonColorDark, player.upgradeDefense)
            button("Upgrade Health", constants.menuButtonFont, 15, textColor, xpos + (upgrade_screenWidth/2) + (upgrade_screenWidth*.1), ypos + ((upgrade_screenHeight*.8)-constants.menuButtonHeight), constants.menuButtonWidth, constants.menuButtonHeight, constants.menuButtonColorLight, constants.menuButtonColorDark, player.upgradeHealth)
            pygame.display.flip()
    player.levelUP()
    characterReflection()


def deathScreen():
    darkenScreen()
    global target
    target = 'None'
    dead = True
    while dead:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.exit()
                exit()
            upgrade_screenWidth = int(constants.displaySize[0]*.6)
            upgrade_screenHeight = int(constants.displaySize[1]*.4)
            xpos = (constants.displaySize[0] - upgrade_screenWidth)/2
            ypos = (constants.displaySize[1] - upgrade_screenHeight)/2
            color = (211, 211, 211)
            upgrade_screen = pygame.draw.rect(mainDisplay, color, (xpos, ypos, upgrade_screenWidth, upgrade_screenHeight))
            textColor = (0, 0, 0)
            displayText("You Died!", constants.menuButtonFont, 35, (constants.displaySize[0] - getTextDimension("width", "You Died!", constants.menuButtonFont, 35)) / 2, ypos + (constants.displaySize[1] * .05), (0, 0, 0), constants.displaySize[0] / 2 + 100)
            button("I'm Going Back", constants.menuButtonFont, 15, textColor, xpos + (upgrade_screenWidth*.1), ypos + (upgrade_screenHeight*.5), constants.menuButtonWidth, constants.menuButtonHeight, constants.menuButtonColorLight, constants.menuButtonColorDark, continueLife)
            button("Take Me Home", constants.menuButtonFont, 15, textColor, xpos + (upgrade_screenWidth/2) + (upgrade_screenWidth*.1), ypos + (upgrade_screenHeight*.5), constants.menuButtonWidth, constants.menuButtonHeight, constants.menuButtonColorLight, constants.menuButtonColorDark, mainMenu)
            pygame.display.flip()


def continueLife():
    # Refers to when a player dies and continues playing
    if player.forestPos >= 2:
        player.forestPos -= 2
    else:
        player.forestPos = 0
    gameInitialize()


def darkenScreen(color=(211, 211, 211)):
    darkScreen = pygame.Surface((constants.displaySize[0], constants.displaySize[1]))
    # Each stage of the forest increases the alpha by 10
    alpha = player.forestPos * 5
    darkScreen.set_alpha(alpha)
    mainDisplay.blit(darkScreen, (0, 0))


def fadeIn(color=(211, 211, 211)):
    fadeSurface = pygame.Surface((constants.displaySize[0], constants.displaySize[1]))
    for alpha in range(0, 256):
        fadeSurface.set_alpha(alpha)
        pygame.draw.rect(mainDisplay, color, fadeSurface.get_rect())
        mainDisplay.blit(fadeSurface, (0, 0))
        pygame.display.flip()
        time.sleep(.001)


def displayText(text, myfont, fontSize, xpos, ypos, textColor, maxWidth, aa=False, bkg=None):
    font = pygame.font.SysFont(myfont, fontSize)
    rect = pygame.Rect(xpos, ypos, maxWidth, constants.displaySize[1])
    y = rect.top
    lineSpacing = -2
    fontHeight = font.size("Tg")[1]
    while text:
        i = 1
        if y + fontHeight > rect.bottom:  # determine if the row of text will be outside our area
            break
        while font.size(text[:i])[0] < rect.width and i < len(text):  # determine maximum width of line
            i += 1
        if i < len(text):  # if we've wrapped the text, then adjust the wrap to the last word
            i = text.rfind(" ", 0, i) + 1
        if bkg:  # adding background color to the text (optional)
            image = font.render(text[:i], 1, textColor, bkg)
            image.set_colorkey(bkg)
        else:  # render if bkg is None
            image = font.render(text[:i], aa, textColor)
        mainDisplay.blit(image, (rect.left, y))
        y += fontHeight + lineSpacing
        text = text[i:]


def getTextDimension(valueFound, text, font, fontSize):
    surface = pygame.font.SysFont(font, fontSize)
    image = surface.render(text, True, (0, 0, 0))
    rect = image.get_rect()
    # If the text height is requested, return it
    if valueFound == "height":
        return rect.height
    elif valueFound == "width":
        return rect.width
    else:
        return "None"


def playerButton(playerName, image, xpos, ypos, width, height, text, maxWidth):
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
            playerSelection = playerName
    else:
        mainDisplay.blit(image, (xpos, ypos))
    #     TODO: make ypos the rect - text.height /2 so it is even
    displayText(text, constants.menuButtonFont, 20, xpos + (constants.characterImageSize[0] + (constants.characterImageSize[0]/15)), ypos, (0, 0, 0), maxWidth)


def chooseCharacter():
    global newGame
    newGame = True
    # TODO: Make screen based in percentages so it works with all screens
    global playerSelection
    time.sleep(.2)
    chooseCharacterOpen = True
    playerSelection = "None"
    while chooseCharacterOpen:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
        mainDisplay.fill(constants.defaultColor)
        # Inits a list of possible player images
        playerOptions = [constants.wizardRaw, constants.warriorRaw, constants.assassinRaw, constants.archerRaw]
        # Final list includes images that have been reformatted
        playerOptionsFinal = []
        for player in playerOptions:
            # for each player image, transform the size to the predetermined size
            player = pygame.transform.scale(player, constants.characterImageSize)
            playerOptionsFinal.append(player)
        # Creates 4 image buttons that check for mouse hovering and clicks
        # Creates a centered title
        displayText("Choose Your Character!", constants.menuButtonFont, 35, (constants.displaySize[0] - getTextDimension("width", "Choose Your Character!", constants.menuButtonFont, 35))/2, constants.displaySize[1]*.05, (0, 0, 0), constants.displaySize[0]/2+100)
        playerButton("Wizard", playerOptionsFinal[0], 0, 75, constants.characterImageSize[0], constants.characterImageSize[1], constants.wizard.introText, (int(constants.displaySize[1]/2.5)))
        playerButton("Warrior", playerOptionsFinal[1], 0, 275, constants.characterImageSize[0], constants.characterImageSize[1], constants.warrior.introText, (int(constants.displaySize[1]/2.5)))
        playerButton("Assassin", playerOptionsFinal[2], (constants.displaySize[1]/2) + constants.characterImageSize[0], 75, constants.characterImageSize[0], constants.characterImageSize[1], constants.assassin.introText, constants.displaySize[1] - (int(constants.displaySize[1]/2)))
        playerButton("Archer", playerOptionsFinal[3], (constants.displaySize[1]/2) + constants.characterImageSize[0], 275, constants.characterImageSize[0], constants.characterImageSize[1], constants.archer.introText, constants.displaySize[1] - (int(constants.displaySize[1]/2)))
        button("Home", constants.menuButtonFont, constants.menuButtonFontSize, (255, 255, 255), 0, 0, constants.menuButtonWidth, constants.menuButtonHeight, (0, 0, 0), (53, 54, 53), mainMenu)
        # TODO: Make the button a better color
        if playerSelection != "None":
            confirmOpen = True
            while confirmOpen:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        exit()
                    confirmX, confirmY = (constants.gameWidth - 300) / 2, (constants.gameHeight - 200) / 2
                    pygame.draw.rect(mainDisplay, (255, 255, 255), (confirmX, confirmY, 300, 100))
                    button("Confirm", constants.menuButtonFont, 15, (255, 255, 255), confirmX + 25, confirmY + 25, 100, 50, (0, 0, 0), (53, 54, 53), gameInitialize)
                    button("Take Me Back", constants.menuButtonFont, 15, (255, 255, 255), confirmX + 25 + 150, confirmY + 25, 100, 50, (0, 0, 0), (53, 54, 53), chooseCharacter)
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


# From https://stackoverflow.com/questions/46390231/how-to-create-a-text-input-box-with-pygame
class optionsTextBox():
    def __init__(self, keyName, xpos, ypos, width, height, text=""):
        self.keyName = keyName
        self.rect = pygame.Rect(xpos, ypos, width, height)
        self.color = constants.inactiveColor
        self.text = text
        self.text_surface = constants.optionFont.render(text, True, constants.activeColor)
        self.active = False

    def handleEvents(self, event):
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Checks to see if the user clicked on the text box
                if self.rect.collidepoint(event.pos):
                    self.active = not self.active
                else:
                    self.active = False
                self.color = constants.activeColor if self.active else constants.inactiveColor
            if event.type == pygame.KEYDOWN:
                # If the text box is active
                if self.active:
                    if event.key == pygame.K_RETURN:
                        self.active = False
                    elif event.key == pygame.K_BACKSPACE:
                        self.text = ""
                    else:
                        self.text = pygame.key.name(event.key).capitalize()
                        if self.text == "Left" or self.text == "Right" or self.text == "Up" or self.text == "Down":
                            self.text += " Arrow"
                    # Renders the new text
                    self.text_surface = constants.optionFont.render(self.text, True, self.color)

    def update(self):
        # Resize the box if the text is too long
        width = max(self.text_surface.get_width(), self.text_surface.get_width()+10)
        self.rect.width = width

    def draw(self, screen):
        # Blit the text.
        screen.blit(self.text_surface, (self.rect.x+5, self.rect.y+5))
        # Blit the rect.
        pygame.draw.rect(screen, self.color, self.rect, 2)

    def save(self):
        if len(self.text) == 1:
            setattr(constants, self.keyName + "Key", (self.text, "K_" + self.text.lower()))
        else:
            setattr(constants, self.keyName + "Key", (self.text, "K_" + self.text.upper()))


def about():
    # About refers to about page being open
    about = True
    while about:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                about = False
        #         Fills the screen a calm blue color
        mainDisplay.fill((188, 212, 222))
        displayText(constants.aboutText, "Calibri", 25, constants.displaySize[0]*.1, constants.displaySize[1]*.2, (255, 255, 255), constants.displaySize[0]*.8)
        displayText("About the Dev Team", "Calibri-bold", 60, (constants.displaySize[0] - getTextDimension("width", "About the Dev Team", "Calibri-bold", 60))/2, constants.displaySize[1]*.05, (255, 255, 255), constants.displaySize[0])
        button("Home", constants.menuButtonFont, constants.menuButtonFontSize, (0, 0, 0), (constants.displaySize[0]-constants.menuButtonWidth)/2, constants.displaySize[1]*.85, constants.menuButtonWidth, constants.menuButtonHeight, constants.menuButtonColorLight, constants.menuButtonColorDark, mainMenu)
        pygame.display.flip()
    pygame.quit()
    exit()


def saveOptions():
    for box in inputBoxes:
        box.save()
    print("Options saved!")
    time.sleep(.3)


def options():
    global inputBoxes
    options = True
    # Generates first textbox 50 pixels down from the title
    width = 50
    height = 32
    textBoxSpacing = (constants.displaySize[1]*.1) + height
    firstYPos = (constants.displaySize[1]*.05 + getTextDimension("height", "Options", "Calibri-bold", 60)) + 50
    attackBox = optionsTextBox("attack", constants.displaySize[0]*.25, firstYPos, width, height, constants.attackKey[0])
    leftBox = optionsTextBox("left", constants.displaySize[0]*.25, firstYPos + textBoxSpacing, width, height, constants.leftKey[0])
    rightBox = optionsTextBox("right", constants.displaySize[0]*.25, firstYPos + textBoxSpacing + textBoxSpacing, width, height, constants.rightKey[0])
    downBox = optionsTextBox("down", constants.displaySize[0]*.75, firstYPos, width, height, constants.downKey[0])
    upBox = optionsTextBox("up", constants.displaySize[0]*.75, firstYPos + textBoxSpacing, width, height, constants.upKey[0])
    inputBoxes = [attackBox, leftBox, rightBox, downBox, upBox]
    while options:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                options = False
            for box in inputBoxes:
                box.handleEvents(event)
        for box in inputBoxes:
            box.update()
        mainDisplay.fill((242, 239, 199))
        for box in inputBoxes:
            box.draw(mainDisplay)
        displayText("Options", "Calibri-bold", 60, (constants.displaySize[0] - getTextDimension("width", "Options", "Calibri-bold", 60))/2, constants.displaySize[1]*.05, (0, 0, 0), constants.displaySize[0])
        # Text for attack textbox
        displayText("Attack Key:", "Calibri", 24, constants.displaySize[0]*.025, firstYPos + (32 - getTextDimension("height", "Attack Key:", "Calibri", 24))/2, (0, 0, 0), constants.displaySize[0]*.25)
        # Text for the left textbox
        displayText("Move Left Key:", "Calibri", 24, constants.displaySize[0]*.025, firstYPos + textBoxSpacing + (32 - getTextDimension("height", "Move Left Key:", "Calibri", 24))/2, (0, 0, 0), constants.displaySize[0]*.25)
        # Text for the right textbox
        displayText("Move Right Key:", "Calibri", 24, constants.displaySize[0]*.025, firstYPos + textBoxSpacing + textBoxSpacing + (32 - getTextDimension("height", "Move Right Key:", "Calibri", 24))/2, (0, 0, 0), constants.displaySize[0]*.25)
        # Text for down textbox
        displayText("Move Down Key:", "Calibri", 24, constants.displaySize[0] * .525, firstYPos + (32 - getTextDimension("height", "Move Down Key:", "Calibri", 24)) / 2, (0, 0, 0), constants.displaySize[0])
        # Text for up textbox
        displayText("Move Up Key:", "Calibri", 24, constants.displaySize[0] * .525, firstYPos + textBoxSpacing + (32 - getTextDimension("height", "Move Up Key:", "Calibri", 24)) / 2, (0, 0, 0), constants.displaySize[0])
        # Inits home button
        button("Home", constants.menuButtonFont, 25, (0, 0, 0), constants.displaySize[0]*.7 - constants.menuButtonWidth, constants.displaySize[1]*.8, constants.menuButtonWidth, constants.menuButtonHeight, constants.menuButtonColorLight, constants.menuButtonColorDark, mainMenu)
        # Inits save button
        button("Save", constants.menuButtonFont, 25, (0, 0, 0), constants.displaySize[0]*.3, constants.displaySize[1]*.8, constants.menuButtonWidth, constants.menuButtonHeight, constants.menuButtonColorLight, constants.menuButtonColorDark, saveOptions)
        pygame.display.flip()
    pygame.exit()
    exit()


def mainMenu():
    time.sleep(.2)
    mainMenuOpen = True
    buttonSpacing = constants.displaySize[1] * .052
    while mainMenuOpen:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                mainMenuOpen = False
        # Takes the desired background image and stretches it to the screen size
        backgroundImage = pygame.transform.scale(constants.menuBackground, constants.displaySize)
        # Displays background image
        mainDisplay.blit(backgroundImage, (0, 0))
        # Creates four buttons, all with different text, functions, and y positions
        # Gets ypos of title + its height
        buttonYPos = (constants.displaySize[1]*.10 + getTextDimension("height", "Going on an Adventure", constants.menuButtonFont, 70)) + 25
        button("Start", constants.menuButtonFont, constants.menuButtonFontSize, (0, 0, 0), (constants.displaySize[0]-constants.menuButtonWidth)/2, buttonYPos, constants.menuButtonWidth, constants.menuButtonHeight, constants.menuButtonColorLight, constants.menuButtonColorDark, chooseCharacter)
        buttonYPos = buttonYPos + constants.menuButtonHeight + buttonSpacing
        button("Resume", constants.menuButtonFont, constants.menuButtonFontSize, (0, 0, 0), (constants.displaySize[0]-constants.menuButtonWidth)/2, buttonYPos, constants.menuButtonWidth, constants.menuButtonHeight, constants.menuButtonColorLight, constants.menuButtonColorDark)
        buttonYPos = buttonYPos + constants.menuButtonHeight + buttonSpacing
        button("Options", constants.menuButtonFont, constants.menuButtonFontSize, (0, 0, 0), (constants.displaySize[0]-constants.menuButtonWidth)/2, buttonYPos, constants.menuButtonWidth, constants.menuButtonHeight, constants.menuButtonColorLight, constants.menuButtonColorDark, options)
        buttonYPos = buttonYPos + constants.menuButtonHeight + buttonSpacing
        button("About", constants.menuButtonFont, constants.menuButtonFontSize, (0, 0, 0), (constants.displaySize[0]-constants.menuButtonWidth)/2, buttonYPos, constants.menuButtonWidth, constants.menuButtonHeight, constants.menuButtonColorLight, constants.menuButtonColorDark, about)
        # Creates title
        displayText("Going on an Adventure", "Garamond", 70, (constants.displaySize[0] - getTextDimension("width", "Going on an Adventure", constants.menuButtonFont, 70))/2, constants.displaySize[1]*.10, (255, 255, 255), constants.displaySize[0])
        # Updates the display
        pygame.display.flip()
    pygame.quit()
    exit()


def bridgeToInit():
    # In order to make sure the player does skip an upgrade screen, this small function makes sure
    # They cannot move on until they have leveled up completely (and upgraded)
    if player.currXP < player.neededXP:
        gameInitialize()


def characterReflection():
    forestDistance = int(player.forestPos*(constants.cellWidth*constants.mapRows)+random.randint(0, 200))
    open = True
    while open:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                open = False
            mainDisplay.fill(constants.reflectionBackgroundColor)
            # gets constant.(desiredplayer), then constants.desiredplayer.imageRaw
            playerChar = getattr(constants, str.lower(player.name))
            playerImage = pygame.transform.scale(getattr(playerChar, "imageRaw"), (150, 150))
            player.displayXPBar()
            mainDisplay.blit(playerImage, (0, 0))
            # Note: these values are based off the position of the XP bar in displayXPBar()
            barXpos = (constants.displaySize[0] - (constants.displaySize[0]*.5))/2
            displayText("You are level " + str(player.level) + "!", "Calibri", 20, barXpos, constants.displaySize[1]*.25, (0, 0, 0), constants.displaySize[0]/2)
            displayText("You have " + str(int(player.currXP)) + "/" + str(int(player.neededXP)) + " XP", "Calibri", 20, (barXpos + (constants.displaySize[0]*.5)) - getTextDimension("width", "You have " + str(player.currXP) + "/" + str(player.neededXP) + " XP", "Calibri", 20), constants.displaySize[1]*.25, (0, 0, 0), constants.displaySize[0])
            border = pygame.draw.rect(mainDisplay, (0, 0, 0), (constants.displaySize[0]*.1, constants.displaySize[1]*.35, constants.displaySize[0]*.8, 4))
            displayText("You have traveled " + str(forestDistance) + " meters into the forest!", "Calibri", 20, barXpos, constants.displaySize[1]*.4, (0, 0, 0), constants.displaySize[0])
            if player.enemiesKilled == 1:
                display_text = "You have killed one enemy!"
            elif player.enemiesKilled == 0:
                display_text = "You have not killed any enemies."
            else:
                display_text = "You have killed " + str(player.enemiesKilled) + " enemies!"
            displayText(display_text, "Calibri", 20, barXpos, constants.displaySize[1]*.5, (0, 0, 0), constants.displaySize[0])
            button("Continue On!", constants.menuButtonFont, 25, (0, 0, 0), constants.displaySize[0]*.3, constants.displaySize[1]*.8, constants.menuButtonWidth, constants.menuButtonHeight, constants.menuButtonColorLight, constants.menuButtonColorDark, bridgeToInit)
            button("Home", constants.menuButtonFont, 25, (0, 0, 0), constants.displaySize[0]*.7 - constants.menuButtonWidth, constants.displaySize[1]*.8, constants.menuButtonWidth, constants.menuButtonHeight, constants.menuButtonColorLight, constants.menuButtonColorDark, mainMenu)
            pygame.display.flip()
            player.levelUP()
            player.displayXPBar()
    pygame.quit()
    exit()


# def resumeGame():
#     global gameObjects
#
#     with open('./GameAssets/Data/saveGame', 'rb') as file:
#         gameObjects = pickle.load(file)


def endLevel():
    global newGame
    newGame = False
    if player.column == constants.mapColumns-1:
        endLevel = True
        # rt.stop()
        fadeIn()
        characterReflection()
    #     Call new screen that showcases XP, etc
    else:
        return


# From https://stackoverflow.com/questions/474528/what-is-the-best-way-to-repeatedly-execute-a-function-every-x-seconds-in-python
class RepeatedTimer(object):
    def __init__(self, interval, function, *args, **kwargs):
        self._timer     = None
        self.interval   = interval
        self.function   = function
        self.args       = args
        self.kwargs     = kwargs
        self.is_running = False
        self.start()

    def _run(self):
        self.is_running = False
        self.start()
        self.function(*self.args, **self.kwargs)

    def start(self):
        if not self.is_running:
            self._timer = Timer(self.interval, self._run)
            self._timer.start()
            self.is_running = True

    def stop(self):
        self._timer.cancel()
        self.is_running = False


def checkAnimalFit(value):
    animalFits = True
    for point in range(0, len(mapGenerator.prevPoints)):
        if mapGenerator.prevPoints[point][1] == value[1]:
            # Checks if the end ypos of the tree is in between any of the tile ypos on the same column
            if (mapGenerator.prevPoints[point][0] * constants.cellHeight) <= (
                    (value[0] * constants.cellHeight) + 60) <= (
                    (mapGenerator.prevPoints[point][0] * constants.cellHeight) + constants.cellHeight):
                animalFits = False
                break
    return animalFits


def moveAnimals():
    for key, value, in animalPos.items():
        if random.randint(0, 100) <= 1:
            row, column, animalNum = value
            direction = random.randint(0, 3)
            if direction == 0:
                # Go down
                if row+1 <= constants.mapRows-1 and checkAnimalFit(value):
                    row += 1
            elif direction == 1:
                # Go up
                if row - 1 >= 0 and checkAnimalFit(value):
                    row -= 1
            elif direction == 2:
                # Go right
                if column + 1 <= constants.mapColumns - 1 and checkAnimalFit(value):
                    column += 1
            else:
                # Go left
                if column - 1 >= 0 and checkAnimalFit(value):
                    column -= 1
            animalPos[key] = row, column, animalNum


def drawAnimals():
    # moveAnimals()
    for key, value in animalPos.items():
        row, column, animalNum = value
        # mainDisplay.blit(getattr(constants, "tree" + str(animalNum)), (column * constants.cellWidth, row * constants.cellHeight))
        mainDisplay.blit(getattr(constants, "animal" + str(animalNum)), (column * constants.cellWidth, row * constants.cellHeight))


def spawnTrees():
    for key, value in treePos.items():
        row, column, treeNum = value
        mainDisplay.blit(getattr(constants, "tree" + str(treeNum)), (column * constants.cellWidth, row * constants.cellHeight))


def initMap(gameMap):
    for row in range(0, constants.mapRows):
        for column in range(0, constants.mapColumns):
            if gameMap[row][column] == 1:  # checks if there is a path
                mainDisplay.blit(constants.pathBox, (column * constants.cellWidth, row * constants.cellHeight))
            else:
                mainDisplay.blit(constants.forestBox, (column * constants.cellWidth, row * constants.cellHeight))


def drawGame():
    global mainDisplay
    # clear the surface
    mainDisplay.fill(constants.defaultColor)
    initMap(gameMap)
    drawAnimals()
    spawnTrees()
    # draw all objects
    for object in gameObjects:
        object.draw()
    player.createHealthBar()
    if not (target == 'None'):
        target.createHealthBar()
    # player.createHealthBar()


def gameMain():
    # global rt
    # rt = RepeatedTimer(3, drawAnimals)
    gameQuit = False
    while not gameQuit:
        playerAction = handleKeys()
        if playerAction == "quit":
            gameQuit = True
        drawGame()
        # Checks if the player has reached the final tile
        endLevel()
        darkenScreen()
        # update the display
        pygame.display.flip()
    # rt.stop()
    pygame.quit()
    exit()


# def saveGame():
#     with open('data/saveGame', 'wb') as file:
#         pickle.dump([gameObjects], file)


def handleKeys():
    # get player input
    events_list = pygame.event.get()
    for event in events_list:  # loop through all events that have happened
        if event.type == pygame.QUIT:
            # quit attribute - someone closed window
            return "quit"
        if event.type == pygame.KEYDOWN:
            if event.key == getattr(pygame, constants.upKey[1]):
                player.move(-1, 0)
                return "player-moved"
            if event.key == getattr(pygame, constants.downKey[1]):
                player.move(1, 0)
                return "player-moved"
            if event.key == getattr(pygame, constants.rightKey[1]):
                player.move(0, 1)
                return "player-moved"
            if event.key == getattr(pygame, constants.leftKey[1]):
                player.move(0, -1)
                return "player-moved"
            if event.key == getattr(pygame, constants.attackKey[1]):
                player.attack(player.strength)
                return "player-attacked"
    return "no-action"


def selectPlayer(mainStartRow):
    if playerSelection == "Wizard":
        # Generates wizard as player if that is selected
        return Creatures(mainStartRow, 0, constants.wizard.name, constants.wizardBox, 'player', constants.wizard.speed, constants.wizard.strength, constants.wizard.defense, constants.wizard.health, 0, 100, 1)
    elif playerSelection == "Warrior":
        # Generates warrior as player if that is selected
        return Creatures(mainStartRow, 0, constants.warrior.name, constants.warriorBox, 'player', constants.warrior.speed, constants.warrior.strength, constants.warrior.defense, constants.warrior.health, 0, 100, 1)
    elif playerSelection == "Assassin":
        # Generates assassin as player if that is selected
        return Creatures(mainStartRow, 0, constants.assassin.name, constants.assassinBox, 'player', constants.assassin.speed, constants.assassin.strength, constants.assassin.defense, constants.assassin.health, 0, 100, 1)
    elif playerSelection == "Archer":
        # Generates archer as player if that is selected
        return Creatures(mainStartRow, 0, constants.archer.name, constants.archerBox, 'player', constants.archer.speed, constants.archer.strength, constants.archer.defense, constants.archer.health, 0, 100, 1)


def spawnEnemies():
    adjacent = False
    # point cap = 1/2 of path tiles
    pointCap = int(len(mapGenerator.prevPoints)/2)
    currentPoints = 0
    level = player.forestPos
    skeletonSpawnChance = constants.skeleton.spawnPercent
    if level <= 3:
        skeletonSpawnChance = 10
    elif 3 < level <= 10:
        skeletonSpawnChance = (level * -1) + 13
    elif level > 10:
        skeletonSpawnChance = 3
    squirrelSpawnChance = constants.squirrel.spawnPercent
    if level < 5:
        squirrelSpawnChance = 0
    elif 5 <= level < 11:
        squirrelSpawnChance = int(-1 * abs(2 * (level - 9))+10)
    elif level >= 11:
        squirrelSpawnChance = 6
    ninjaSpawnChance = constants.ninja.spawnPercent
    if level <= 6:
        ninjaSpawnChance = 0
    elif 7 < level <= 12:
        ninjaSpawnChance = 2 * (level - 6)
    elif 12 < level <= 16:
        ninjaSpawnChance = (-1 * 2) * (level - 18)
    elif level > 16:
        ninjaSpawnChance = 4
    darkWarriorSpawnChance = constants.darkWarrior.spawnPercent
    if level < 12:
        darkWarriorSpawnChance = 0
    elif 12 <= level <= 30:
        darkWarriorSpawnChance = int(((1/5) * level) ** 2)
    elif level > 30:
        darkWarriorSpawnChance = 20
    while not (pointCap - 5 < currentPoints < pointCap + 15):
        for cord in mapGenerator.prevPoints:
            if not cord[1] == 0:
                if pointCap - 5 < currentPoints < pointCap + 5:
                    return
                # Spawn number allows each enemy to have a chance to be spawned at the same time
                spawnNumber = random.randint(0, 101)
                if not adjacent:
                    # spawns skeleton with a 10% chance per tile
                    if spawnNumber <= skeletonSpawnChance:
                        adjacent = True
                        # sets adjacent to True so enemies cannot spawn next to directly next to each other
                        # (technically can since only works for one tile)
                        gameObjects.append(Creatures(cord[0], cord[1], constants.skeleton.name, constants.skeletonBox, 'enemy', constants.skeleton.speed, constants.skeleton.strength, constants.skeleton.defense, constants.skeleton.health, XPGiven=constants.skeleton.xpGiven))
                        # adds enemy to object list (will be drawn in gameDraw())
                        currentPoints += constants.skeleton.pointValue
                        continue
                    # Checks to spawn squirrel
                    elif skeletonSpawnChance < spawnNumber <= squirrelSpawnChance + skeletonSpawnChance:
                        adjacent = True
                        gameObjects.append(Creatures(cord[0], cord[1], constants.squirrel.name, constants.squirrelBox, 'enemy', constants.squirrel.speed, constants.squirrel.strength, constants.squirrel.defense, constants.squirrel.health, XPGiven=constants.squirrel.xpGiven))
                        currentPoints += constants.squirrel.pointValue
                        continue
                    # Checks to spawn ninja
                    elif squirrelSpawnChance + skeletonSpawnChance < spawnNumber <= ninjaSpawnChance + squirrelSpawnChance + skeletonSpawnChance:
                        adjacent = True
                        gameObjects.append(Creatures(cord[0], cord[1], constants.ninja.name, constants.ninjaBox, 'enemy', constants.ninja.speed, constants.ninja.strength, constants.ninja.defense, constants.ninja.health, XPGiven=constants.ninja.xpGiven))
                        currentPoints += constants.ninja.pointValue
                        continue
                    # Checks to spawn dark warrior
                    elif ninjaSpawnChance + squirrelSpawnChance + skeletonSpawnChance < spawnNumber <= darkWarriorSpawnChance + ninjaSpawnChance + squirrelSpawnChance + skeletonSpawnChance:
                        adjacent = True
                        gameObjects.append(Creatures(cord[0], cord[1], constants.darkWarrior.name, constants.darkWarriorBox, 'enemy', constants.darkWarrior.speed, constants.darkWarrior.strength, constants.darkWarrior.defense, constants.darkWarrior.health, XPGiven=constants.darkWarrior.xpGiven))
                        currentPoints += constants.darkWarrior.pointValue
                        continue
                if adjacent:
                    adjacent = False
                    # figure out leveling sometime (enemies depend on level)


def gameInitialize():
    fadeIn()
    global mainDisplay, gameMap, player, gameObjects, treePos, animalPos
    gameMap, mainStartRow, treePos, animalPos = mapGenerator.main()  # returns map and mainStartRow (initial path start row)
    gameObjects = []
    if newGame:
        player = selectPlayer(mainStartRow)
    try:
        player.levelReset(mainStartRow)
    except NameError:
        player = selectPlayer(mainStartRow)
    gameObjects.append(player)
    # Every time the player passes through a section, the player ventures further into the forest
    player.forestPos += 1
    spawnEnemies()
    gameMain()


if __name__ == '__main__':
    pygame.mixer.music.load(constants.backgroundMusic)
    pygame.mixer.music.set_volume(.1)
    pygame.mixer.music.play(-1)
    mainMenu()
