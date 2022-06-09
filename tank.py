import pygame

import bullet
from sprite import Sprite

class Tank(Sprite):
    controls = [
        ['a', 'd', 'w', 's', 'q'],
        ['left', 'right', 'up', 'down', '/'],
        ['j', 'l', 'i', 'k', 'u'],
        ['Keypad 4', 'Keypad 6', 'Keypad 8', 'Keypad 5', 'Keypad 7']
    ]
    maxBullets = 4

    def __init__(self, i, pos, sprites):
        super().__init__('Tanks\\tank'+str(i), sprites)
        self.index = i
        self.points = 0
        self.rot = 0.0
        self.pos = {'x':pos[0], 'y':pos[1]}
        self.power = 'normal'
        self.bullets = {}
        self.bulletRot = -1
        self.bulletMov = -1
        self.bulletShoot = -1
        self.ammo = -1
        self.hp = self.sprites.level.settings['maxHP']
        self.turret = self.power
        self.canShoot = True
        self.nextShot = None
        self.inControl = True
        self.update()

    def update(self):
        if not self.dead:
            super().update()
            #Draw turret
            r = self.turret.get_rect()
            self.sprites.screen.blit(self.turret, (self.pos['x']-r.center[0], self.pos['y']-r.center[1]))
            #Check if the tank can shoot
            if not self.canShoot and self.nextShot <= self.sprites.level.FPS.currentTime():
                self.canShoot = True
            #Update bullets
            for key in list(self.bullets):
                self.bullets[key].update()
            #Check for death
            if self.hp <= 0:
                self.die()

    def getKeyCode(self, i):
        return pygame.key.key_code(Tank.controls[self.index][i])

    def processInput(self, keys):
        #Rotate left
        if keys[self.getKeyCode(0)]:
            self.rotate(-1)
        #Rotate right
        if keys[self.getKeyCode(1)]:
            self.rotate(1)
        #Rotate move forwards
        if keys[self.getKeyCode(2)]:
            self.move(1)
        #Rotate move backwards
        if keys[self.getKeyCode(3)]:
            self.move(-1)
        #Shoot
        if keys[self.getKeyCode(4)]:
            self.shoot()

    def move(self, Dir):
        if self.bulletMov != -1:
            #Move the bullet if it has control
            self.bullets[self.bulletMov].move(Dir)
        elif self.inControl:
            #Move self
            super().move(self.sprites.level.tankSpeed, Dir)

    def rotate(self, Dir):
        if self.bulletRot != -1:
            #Rotate the bullet if it has control
            self.bullets[self.bulletRot].rotate(Dir)
        elif self.inControl:
            #Rotate self
            super().rotate(self.sprites.level.tankRotSpeed, Dir)

    @property
    def turret(self):
        return pygame.transform.rotate(self._turret, 360-self.rot)

    @turret.setter
    def turret(self, t):
        self.power = t
        self._turret = pygame.image.load(self.sprites.imgPath+'Turrets\\'+t+str(self.index)+'.png').convert_alpha()

    def addBullet(self, Class, parent=None):
        for i in range(50):
            if i not in self.bullets:
                if parent == None:
                    self.bullets[i] = Class(self, i, self.sprites)
                else:
                    self.bullets[i] = Class(parent, i, self.sprites)
                    self.bullets[i].tank = self
                break

    def shoot(self):
        if self.canShoot:
            if self.bulletShoot == -1:
                if self.ammo >= 1:
                    self.ammo -= 1
                    #Shoot with a powerup
                    self.addBullet(bullet.classes[self.power])
                    #Shoot all shotgun shells at once
                    if self.ammo > 0 and self.power == 'Shotgun':
                        self.canShoot = True
                        self.shoot()
                elif self.ammo == -1 and len(self.bullets) < self.sprites.level.settings['maxBullets']:
                    #Shoot with a normal turret
                    self.addBullet(bullet.Bullet)
                #Reset powerup if the ammo has ran out
                if self.ammo == 0:
                    self.turret = 'normal'
                    self.ammo = -1
                    if self.nextShot - self.sprites.level.FPS.currentTime() < bullet.Bullet.configs['normal'][7] * 1.2:
                        self.nextShot = self.sprites.level.FPS.currentTime() + bullet.Bullet.configs['normal'][7] * 1.2
            else:
                self.bullets[self.bulletShoot].shoot()

    def die(self):
        self.dead = True
        self.sprites.level.activeTanks -= 1
        self.hp = 0

    def respawn(self):
        if self.dead:
            self.dead = False
        else:
            #If the tank respawns without dying the tank has won the round
            self.points += 1
        self.hp = self.sprites.level.settings['maxHP']
        self.pos = {
            'x' : self.sprites.level.settings['spawnPoints'][self.index][0],
            'y' : self.sprites.level.settings['spawnPoints'][self.index][1]
        }
