import pygame
from pygame.locals import Rect
import json
from random import choice, shuffle
from os import listdir, path
from time import perf_counter, sleep
from sys import exit

import bullet
from tank import Tank

#Set colours
col = {
  'black' : (0, 0, 0),
  'white' : (255, 255, 255),
  'grey' : (160, 160, 160),
  'red' : (255, 0, 0),
  'green' : (0, 255, 0),
  'blue' : (0, 0, 255),
  'purple' : (255, 0, 255),
  'yellow' : (255, 255, 0),
  'orange' : (255, 125 ,0)
}
tankCols = ['Red', 'Blue', 'Green', 'Yellow']

class FPS_Handler:
    def __init__(self, m):
        self.max = int(m)
        self.FPS = 0
        self.clock = pygame.time.Clock()

    def update(self):
        self.FPS = self.clock.get_fps()

    def get(self):
        return int(self.FPS)

    #This makes sure the movement and rotation is consistent no matter the FPS
    def lossPercent(self):
        return 60/self.FPS

    def currentTime(self):
        return perf_counter()

    def tick(self):
        self.clock.tick(self.max)

class Level:
    def __init__(self, screen, imgPath, mode='default', lvl=None):
        self.screen = screen
        self.imgPath = imgPath
        self.cols = ['red', 'blue', 'green', 'yellow']
        self.round = 0
        self.newRoundTimerSet = False

        #Get mode settings
        if path.exists('Config\\modes.json'):
            with open('Config\\modes.json') as f:
                allModes = json.load(f)
                #Use the default settings as a base for the custom settings
                self.customSettings = dict(allModes['default'])
                #Replace any default settings with custom settings
                for key in allModes[mode]:
                    self.customSettings[key] = allModes[mode][key]
        else:
            print('ERROR: Config\\modes.json not found!')
            exit()

        #Get bullet configuration
        if path.exists('Config\\bullets.json'):
            with open('Config\\bullets.json') as f:
                self.bulletConfig = json.load(f)
        else:
            print('ERROR: Config\\bullets.json not found!')
            exit()

        #FPS setup
        self.FPS = FPS_Handler(self.customSettings['maxFPS'])

        #Level setup
        if lvl == None:
            lvl = choice(self.getAllLevels())
        self.setupLvl(lvl)

    def update(self):
        #Draw to window
        pygame.display.flip()
        self.FPS.tick()
        #Check for a new round
        if self.activeTanks <= 1 and not self.newRoundTimerSet:
            self.newRoundTimerSet = True
            self.newRoundTimer = self.FPS.currentTime()
        if (self.newRoundTimerSet and self.newRoundTimer+2 < self.FPS.currentTime()) or self.activeTanks == 0:
            self.newRound()

        #Draw level
        self.screen.fill(self.bgCol)
        self.screen.blit(self.image, self.center)
        #Draw scores
        self.writeScores()
        self.drawHP()

    def writeText(self, pos, text, colour='black', size=25):
        font = pygame.font.SysFont('Calibri', size, True)
        label = font.render(text, 1000, col[colour])
        self.screen.blit(label, pos)

    def writeScores(self):
        for i, t in enumerate(self.sprites['tanks']):
            pos = (int((i*self.settings['screenSize'][0])/self.playerCount), self.settings['screenSize'][1]+2)
            self.writeText(pos, '  {} - {}'.format(tankCols[t.index], t.points), self.cols[i])

    def drawHP(self):
        for i, t in enumerate(self.sprites['tanks']):
            pos = (int((i*self.settings['screenSize'][0])/self.playerCount)+13, self.settings['screenSize'][1]+32)
            pygame.draw.rect(self.screen, (130,130,130), Rect(pos[0], pos[1], 100, 10))
            pygame.draw.rect(self.screen, col[self.cols[i]], Rect(pos[0], pos[1], int(100 * t.hp/self.settings['maxHP']), 10))

    def setupLvl(self, name):
        #Get level path
        levelPath = self.imgPath+'Levels\\'+name

        #Load the custom settings
        newSettings = dict(self.customSettings)
        #Add level specific settings
        if path.exists(levelPath+'.json'):
            with open(levelPath+'.json') as f:
                levelSettings = json.load(f)
                for key in levelSettings:
                    newSettings[key] = levelSettings[key]
        #Save settings
        self.settings = newSettings

        #Get background colour
        if self.settings['bgCol'] in col:
            self.bgCol = col[self.settings['bgCol']]
        else:
            self.bgCol = self.settings['bgCol']

        #Set powerups
        if self.settings['powerups'] == 'ALL':
            self.settings['powerups'] = list(bullet.classes.keys())
        
        #Set level vars
        self.tankSpeed = self.settings['tMovSpeed']
        self.tankRotSpeed = self.settings['tRotSpeed']
        screenSize = self.settings['screenSize']
        center = screenSize[0]/2, screenSize[1]/2
        self.screen = pygame.display.set_mode((screenSize[0], screenSize[1]+50))
        pygame.display.set_caption(self.settings['caption'])
        
        #Set level image
        self.image = pygame.image.load(levelPath+'.png').convert_alpha()
        self.mask = pygame.mask.from_surface(self.image)
        r = self.image.get_rect()
        self.center = (center[0]-r.center[0], center[1]-r.center[1])

    def firstRound(self, sprites):
        #Save settings
        self.sprites = sprites
        self.playerCount = self.settings['playerCount']
        self.activeTanks = self.playerCount
        #Spawn tanks
        shuffle(self.settings['spawnPoints'])
        for i in range(self.playerCount):
            sprites.add(Tank(i, self.settings['spawnPoints'][i], sprites), 'tanks', True)

    def newRound(self):
        #Get and set up new level
        if self.settings['rndMap']:
            newLvl = choice(self.getAllLevels())
            self.setupLvl(newLvl)
        self.newRoundTimerSet = False
        #Output scores
        self.screen.fill(self.bgCol)
        self.writeScores()
        self.round += 1
        print('Round {} complete!'.format(self.round))
        pygame.display.flip()
        #Remove unnecessary sprites
        for t in self.sprites['tanks']:
            t.bullets = {}
        self.sprites.removeGroup('powerups')
        sleep(.6)
        #Reset tanks
        self.activeTanks = self.playerCount
        shuffle(self.settings['spawnPoints'])
        for t in self.sprites['tanks']:
            t.respawn()

    def getAllLevels(self): #Returns a list including all level names
        l = []
        for f in listdir(self.imgPath+'Levels'):
            f = path.basename(f)
            if '.png' in f:
                l.append(f.replace('.png', ''))
        return l
