from random import choice, randint

import bullet
from sprite import Sprite

class Powerup(Sprite):
    nextPowerup = 4

    @staticmethod
    def createPowerup(sprites):
        #If it is time for the next powerup, spawn one
        if Powerup.nextPowerup <= sprites.level.FPS.currentTime():
            if len(sprites['powerups']) < sprites.level.settings['maxPowerup']:
                #Get a random location for the powerup
                x = randint(5, sprites.level.settings['screenSize'][0]-5)
                y = randint(5, sprites.level.settings['screenSize'][1]-5)
                #Spawn in the powerup
                sprites.add(Powerup(choice(sprites.level.settings['powerups']), {'x':x, 'y':y}, sprites), 'powerups')

            #Get a time for the next powerup
            spawnRate = sprites.level.settings['powerupSpawnRate']
            Powerup.nextPowerup = sprites.level.FPS.currentTime() + randint(spawnRate[0], spawnRate[1])

    def __init__(self, power, pos, sprites):
        super().__init__('Powerups\\'+power, sprites)
        self.pos = pos
        self.power = power
        self.ammo = bullet.ammo[power] * sprites.level.settings['ammoMultiplier']
        self.update()

    def update(self):
        super().update()
        self.isColliding()
        self.rotate(1)

    def rotate(self, Dir):
        super().rotate(1, Dir)

    def isColliding(self):
        for sprite in super().isColliding():
            if sprite != -1:
                self.tankCollision(sprite)
                yield sprite

    def tankCollision(self, tank): #On collision with tank add powerup to it
        tank.turret = self.power
        tank.ammo = self.ammo
        self.sprites.remove(self)
