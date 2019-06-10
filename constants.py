import pygame

gameHeight = 600
gameWidth = 800
cellWidth = 32
cellHeight = 32
maxMessages = 4

# Map variables
mapRows = 15
mapColumns = 25

# Sprites
spriteWidth = 32
# Game Sprites
forest = pygame.image.load('F:/carter/Pictures/GameAssets/forestBox.png')
path = pygame.image.load('F:/carter/Pictures/GameAssets/pathBox.png')
river = pygame.image.load('F:/carter/Pictures/GameAssets/waterBox.png')
dirt = pygame.image.load('F:/carter/Pictures/GameAssets/dirtBox.png')
# Player Sprites
wizard = pygame.image.load('F:/carter/Pictures/GameAssets/wizardBox.png')
warrior = pygame.image.load('F:/carter/Pictures/GameAssets/warriorBox.png')
assassin = pygame.image.load('F:/carter/Pictures/GameAssets/assassinBox.png')
# Enemy Sprites
skeleton = pygame.image.load('F:/carter/Pictures/GameAssets/skeletonBox.png')
squirrel = pygame.image.load('F:/carter/Pictures/GameAssets/squirrelBox.png')
ninja = pygame.image.load('F:/carter/Pictures/GameAssets/ninjaBox.png')
dragonPassive = pygame.image.load('F:/carter/Pictures/GameAssets/dragonPassiveBox.png')
dragonAggressive = pygame.image.load('F:/carter/Pictures/GameAssets/dragonAggressiveBox.png')
darkWarrior = pygame.image.load('F:/carter/Pictures/GameAssets/darkwarriorBox.png')

# Colors
defaultColor = (100, 100, 100)


# Main Menu
displaySize = (mapColumns * cellWidth, mapRows * cellHeight)
menuBackground = pygame.image.load('F:/carter/Pictures/GameAssets/menuBackground.jpg')
menuButtonWidth = 150
menuButtonHeight = 50
menuButtonColorLight = (214, 237, 255)
menuButtonColorDark = (179, 223, 255)
menuButtonFont = "Calibri"
menuButtonFontSize = 30