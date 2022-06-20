import pygame
from math import sin, cos, pi

#This class holds sprites and variable references used across multiple classes
class SpriteHandler:
    def __init__(self, screen, level, imgPath):
        self.screen = screen
        self.level = level
        self.imgPath = imgPath
        self.sprites = []
        self.groups = []

    def add(self, sprite, group, collisionCheck=False):
        self.sprites.append([sprite, group, collisionCheck])
        #Add sprite gruop if group does not yet exist
        if group not in self.groups:
            self.groups.append(group)

    def remove(self, sprite):
        for s in self.sprites:
            if s[0] == sprite:
                spriteGroup = s[1]
                self.sprites.remove(s)
                break
        else:
            return

        #Check if there is any sprites left with the same group
        removeGroup = True
        for s in self.sprites:
            if s[1] == spriteGroup:
                removeGroup = False
        #If there are no sprites in the group, remove it
        if removeGroup:
            self.groups.remove(spriteGroup)

    def removeGroup(self, group):
        if group in self.groups:
            for s in self[group]:
                self.remove(s)

    def getColliders(self): #Get all sprites with collision enabled
        sprites = []
        for s in self.sprites:
            if s[2]:
                sprites.append(s[0])
        return sprites

    def update(self):
        for s in self.sprites:
            s[0].update()

    def __getitem__(self, group): #Get all sprites within a group
        sprites = []
        for s in self.sprites:
            if s[1] == group:
                sprites.append(s[0])
        return sprites

class Sprite:
    def __init__(self, image, sprites):
        self.image = pygame.image.load(sprites.imgPath+image+'.png').convert_alpha()
        self.sprites = sprites
        self.timesCollided = 0
        self.dead = False
        self.rot = 0
        self.pos = {'x':0, 'y':0}

    def update(self):
        #Draw sprite on the screen with the correct position and rotation
        img = pygame.transform.rotate(self.image, 360-self.rot)
        self.mask = pygame.mask.from_surface(img)
        r = img.get_rect()
        self.center = tuple(r.center)
        self.sprites.screen.blit(img, (self.pos['x']-r.center[0], self.pos['y']-r.center[1]))

    def move(self, speed, Dir, collide=True, stuck=0):
        oldPos = dict(self.pos)
        #Claculate distances according to rotation
        r = self.rot % 90
        a = sin(r*(pi/180))*speed*Dir*self.sprites.level.FPS.lossPercent()
        b = cos(r*(pi/180))*speed*Dir*self.sprites.level.FPS.lossPercent()

        #Update the new position
        if self.rot < 90:
            self.pos['x'] += a
            self.pos['y'] -= b
        elif self.rot < 180:
            self.pos['x'] += b
            self.pos['y'] += a
        elif self.rot < 270:
            self.pos['x'] -= a
            self.pos['y'] += b
        elif self.rot < 360:
            self.pos['x'] -= b
            self.pos['y'] -= a

        #Check collisions
        if list(self.isColliding()) and collide:
            self.timesCollided += 1
            self.pos = dict(oldPos)
            if self.timesCollided >= 100 and stuck < 5:
                Sprite.move(self, speed*1.25, Dir, collide, stuck+1)
        else:
            self.timesCollided = 0

    def rotate(self, speed, Dir, collide=True, stuck=0):
        oldRot = float(self.rot)
        #Calculate new rotation
        self.rot += speed*Dir*self.sprites.level.FPS.lossPercent()

        #Get new collision mask and center
        img = pygame.transform.rotate(self.image, 360-self.rot)
        self.mask = pygame.mask.from_surface(img)
        r = img.get_rect()
        self.center = tuple(r.center)

        #Check collisions
        if list(self.isColliding()) and collide:
            self.timesCollided += 1
            self.rot = oldRot
            if self.timesCollided >= 100 and stuck < 5:
                if self.timesCollided >= 2000:
                    self.timesCollided = 0
                Sprite.rotate(self, speed+1, Dir, collide, stuck+1)
        else:
            self.timesCollided = 0

    @property
    def rot(self):
        return self._rot

    @rot.setter
    def rot(self, newRot):
        self._rot = newRot % 360

    def isColliding(self):
        selfPos = (
            int(self.pos['x'] - self.center[0]),
            int(self.pos['y'] - self.center[1])
        )
        #Check each sprite that has collision enabled
        for s in self.sprites.getColliders():
            #Get offset between the two sprites
            offset = (
                int((s.pos['x']-s.center[0]) - selfPos[0]),
                int((s.pos['y']-s.center[1]) - selfPos[1])
            )
            #If the masks overlap and the other sprite is not dead yield the sprite
            if self.mask.overlap(s.mask, offset):
                if s != self and not s.dead:
                    yield(s)
        #Check collision with the level
        if self.sprites.level.mask.overlap(self.mask, selfPos):
            yield(-1)
