from random import randint

from sprite import Sprite

class Bullet(Sprite):
    def __init__(self, tank, ID, sprites):
        self.center = None
        super().__init__('Bullets\\'+tank.power, sprites)
        self.pos = dict(tank.pos)
        self.rot = float(tank.rot)
        self.type = str(tank.power)
        self.id = ID
        
        self.tank = tank
        tank.canShoot = False
        
        self.setConfig()

    def setConfig(self):
        #Get the bullet config of the current type
        config = self.sprites.level.bulletConfig[self.type]
        
        #Set the configuration of the bullet according to which class it is
        self.speed = config['speed'] * self.sprites.level.settings['bSpeedMultiplier']
        self.rotSpeed = config['rotationSpeed'] * self.sprites.level.settings['bSpeedMultiplier']
        self.ctrlRot = config['controlRotation']
        self.ctrlMov = config['controlMovement']
        self.ctrlShoot = config['controlShoot']
        self.damage = config['damage']
        self.collide = config['collide']
        self.shotDelay = config['shotDelay']
        self.autoMove = config['autoMove']
        self.lifetime = self.sprites.level.FPS.currentTime() + config['lifetime']
        self.blockMov = config['blockTankMovement']

        #Set the state of the tank
        if self.ctrlRot:
            self.tank.bulletRot = self.id
        if self.ctrlMov:
            self.tank.bulletMov = self.id
        if self.ctrlShoot:
            self.tank.bulletShoot = self.id
        self.tank.nextShot = self.sprites.level.FPS.currentTime() + self.shotDelay
        self.tank.inControl = not self.blockMov

    def update(self):
        if self.lifetime <= self.sprites.level.FPS.currentTime():
            self.__del__()
        super().update()
        if self.autoMove:
            self.move(1)

    def move(self, Dir):
        super().move(self.speed, Dir, self.collide)

    def rotate(self, Dir):
        super().rotate(self.rotSpeed, Dir, self.collide)

    def isColliding(self):
        for o in super().isColliding():
            if o == -1:
                self.wallCollision()
                yield o
            else:
                if o != self.tank:
                    self.tankCollision(o)

    def wallCollision(self):
        if self.collide:
            self.__del__()

    def tankCollision(self, enemyTank):
        #Apply damage to tank
        enemyTank.hp -= self.damage
        #Check if tank is dead
        if enemyTank.hp <= 0:
            enemyTank.die()
        #Delete self
        self.__del__()

    def shoot(self):
        self.isColliding()
        self.__del__()

    def __del__(self):
        #Resore control to tank
        if self.ctrlRot:
            self.tank.bulletRot = -1
        if self.ctrlMov:
            self.tank.bulletMov = -1
        if self.ctrlShoot:
            self.tank.bulletShoot = -1
            self.tank.nextShot = self.sprites.level.FPS.currentTime() + 0.5
        if self.blockMov:
            self.tank.inControl = True
        #Remove bullet from the tank
        if self.id in self.tank.bullets:
            del self.tank.bullets[self.id]

class B_Drone(Bullet):
    Str = 'B_Drone'

class B_Minigun(Bullet):
    def __init__(self, t, i, sprites):
        super().__init__(t, i, sprites)
        self.rot += randint(-10, 10)

class B_RC(Bullet):
    pass

class B_Ghost(Bullet):
    pass

class B_Mine(Bullet):
    def __init__(self, t, i, sprites):
        super().__init__(t, i, sprites)
        self.spawn = float(self.sprites.level.FPS.currentTime())
    
    def isColliding(self):
        selfPos = (int(self.pos['x']-self.center[0]), int(self.pos['y']-self.center[1]))
        for t in self.sprites['tanks']:
            offset = (int((t.pos['x']-t.center[0])-selfPos[0]), int((t.pos['y']-t.center[1])-selfPos[1]))
            #Check tank collision
            if self.mask.overlap(t.mask, offset):
                if not t.dead:
                    if t != self.tank or self.spawn+3 <= self.sprites.level.FPS.currentTime():
                        self.tankCollision(t)
                    yield t.index
            #Check bullet collision
            for bullet in t.bullets:
                b = t.bullets[bullet]
                if b.__class__ != self.__class__ and b.center != None:
                    offset = (int((b.pos['x']-b.center[0])-selfPos[0]), int((b.pos['y']-b.center[1])-selfPos[1]))
                    if self.mask.overlap(b.mask, offset) and b.tank == self.tank:
                        self.__del__()
                        b.__del__()
                        break

class B_Sniper(Bullet):
    pass

class B_Shotgun(Bullet):
    def __init__(self, tank, ID, sprites):
        super().__init__(tank, ID, sprites)
        self.rot += randint(-20, 20)

class Bullet_Controller(Bullet):
    info = {'Drone':(2, B_Drone)}
    
    def __init__(self, tank, ID, sprites):
        super().__init__(tank, ID, sprites)
        self.ammo = Bullet_Controller.info[self.type][0]
        self.bulletClass = Bullet_Controller.info[self.type][1]
        self.power = self.bulletClass.Str
        self.canShoot = True
        self.nextShot = self.sprites.level.FPS.currentTime() + .1

    def update(self):
        super().update()
        #If ammo delpleted delete self
        if self.ammo == 0:
            self.__del__()
        #Ready weapon if enough time passed
        if self.canShoot == False and self.nextShot <= self.sprites.level.FPS.currentTime():
            self.canShoot = True
    
    def shoot(self):
        if self.ammo >= 0 and self.canShoot:
            self.ammo -= 1
            self.tank.addBullet(self.bulletClass, self)
            #Add shot delay
            self.canShoot = False
            self.nextShot = self.sprites.level.FPS.currentTime() + self.shotDelay

    def __del__(self):
        self.tank.canShoot = False
        self.tank.nextShot = self.sprites.level.FPS.currentTime() + self.shotDelay
        super().__del__()

class BC_Drone(Bullet_Controller):
    pass


classes = {
    'RC' : B_RC,
    'Drone' : BC_Drone,
    'Mine' : B_Mine,
    'Ghost' : B_Ghost,
    'Minigun' : B_Minigun,
    'Shotgun' : B_Shotgun,
    'Sniper' : B_Sniper
}
ammo = {
    'RC' : 1,
    'Drone' : 1,
    'Mine' : 3,
    'Ghost' : 1,
    'Minigun' : 15,
    'Shotgun' : 6,
    'Sniper' : 1
}
