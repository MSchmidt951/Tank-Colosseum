import pygame
from os import getcwd
from time import sleep

from level import Level, tankCols
from sprite import SpriteHandler
from powerup import Powerup

###Init
pygame.init()

screen = pygame.display.set_mode((1, 1))
imgPath = getcwd()+'\\Images\\'

currLvl = Level(screen, imgPath)
sprites = SpriteHandler(screen, currLvl, imgPath)
currLvl.firstRound(sprites)

###Main loop
run = True
while run:
    currLvl.FPS.update()
    if currLvl.FPS.get():
        #Handle events
        for e in pygame.event.get():
            if e.type == pygame.QUIT or (e.type == pygame.locals.KEYDOWN and e.key == pygame.K_ESCAPE):
                run = False
        #Process inputs
        keys = pygame.key.get_pressed()
        for t in sprites['tanks']:
            t.processInput(keys)
        #Updates
        Powerup.createPowerup(sprites)
        sprites.update()
    currLvl.update()

###Exit code
pygame.quit()
print('\nFinal scores:')
for t in sprites['tanks']:
    print(' {}\t - {}'.format(tankCols[t.index], t.points))
sleep(5)
print('\nExiting...')
sleep(1)
