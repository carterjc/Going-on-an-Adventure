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
forestBox = pygame.image.load('./GameAssets/TileFit/forestBox.png')
pathBox = pygame.image.load('./GameAssets/TileFit/pathBox.png')
riverBox = pygame.image.load('./GameAssets/TileFit/waterBox.png')
dirtBox = pygame.image.load('./GameAssets/TileFit/dirtBox.png')
# Player Sprites
wizardBox = pygame.image.load('./GameAssets/TileFit/wizardBox.png')
warriorBox = pygame.image.load('./GameAssets/TileFit/warriorBox.png')
assassinBox = pygame.image.load('./GameAssets/TileFit/assassinBox.png')
archerBox = pygame.image.load('./GameAssets/TileFit/archerBox.png')
# Enemy Sprites
skeletonBox = pygame.image.load('./GameAssets/TileFit/skeletonBox.png')
squirrelBox = pygame.image.load('./GameAssets/TileFit/squirrelBox.png')
ninjaBox = pygame.image.load('./GameAssets/TileFit/ninjaBox.png')
dragonPassiveBox = pygame.image.load('./GameAssets/TileFit/dragonPassiveBox.png')
dragonAggressiveBox = pygame.image.load('./GameAssets/TileFit/dragonAggressiveBox.png')
darkWarriorBox = pygame.image.load('./GameAssets/TileFit/darkwarriorBox.png')

# Colors
defaultColor = (100, 100, 100)


# Main Menu
displaySize = (mapColumns * cellWidth, mapRows * cellHeight)
menuBackground = pygame.image.load('./GameAssets/Background/menuBackground.jpg')
menuButtonWidth = 150
menuButtonHeight = 50
menuButtonColorLight = (214, 237, 255)
menuButtonColorDark = (179, 223, 255)
menuButtonFont = "Calibri"
menuButtonFontSize = 30

# Character Selection Menu
characterImageSize = (150, 150)
# Raw Player Sprites
wizardRaw = pygame.image.load('./GameAssets/RawImages/wizard.png')
warriorRaw = pygame.image.load('./GameAssets/RawImages/warrior.png')
archerRaw = pygame.image.load('./GameAssets/RawImages/archer.png')
assassinRaw = pygame.image.load('./GameAssets/RawImages/assassin.png')


class playerCharacters:
    def __init__(self, name, speed, strength, defense, health, imageRaw, imageBox, introText):
        self.name = name
        self.speed = speed
        self.strength = strength
        self.defense = defense
        self.health = health
        self.imageRaw = imageRaw
        self.imageBox = imageBox
        self.introText = introText


wizard = playerCharacters("Wizard", 3, 7, 5, 14, wizardRaw, wizardBox, "The wizard has been forged by the magical elements. One with magic, be wary of his power")
warrior = playerCharacters("Warrior", 2, 3, 7, 16, warriorRaw, warriorBox, "Birthed in a mighty castle, the warrior is accustomed to honor and has an impeccable hacking ability.")
archer = playerCharacters("Archer", 5, 3, 3, 10, archerRaw, archerBox, "Draw back, hold, release; her arrow always strikes true. The archer has trained for years, perfecting her craft. Her skill is unparalleled.")
assassin = playerCharacters("Assassin", 7, 4, 1, 12, assassinRaw, assassinBox, "To the left, to the right - there is no one. Yet, there is. Cloaked in the shadows, the assassin uses the environment to stay hidden until the time is right to strike.")

