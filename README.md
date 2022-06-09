# Tank Colosseum

A top down 2D game where 2-4 players battle each other in tanks.  
Inspired by Tank Trouble.

## Installation and Setup

- Download the [latest release](https://github.com/MSchmidt951/Tank-Colosseum/releases) and extract
- Run game.exe

### Building

- Install Python then run the command `pip install pyinstaller`.
- Clone the respository.
- In the directory of the respository run the command `pyinstaller --onefile -w "Tank Colosseum.py"`.
- This will create a file called `dist` with the exe file in it. Copy all non python files into this folder.

## How to play

The game is played in rounds where the last tank alive wins.

Each round the tanks will spawn in random locations on a random map.

### Controls

Tank Colour | Forward | Back  | Left  | Right | Shoot
----------- | ------- | ----- | ----- | ----- | -----
Red         | W       | S     | A     | D     | Q
Blue        | Up      | Down  | Left  | Right | /
Green       | I       | K     | J     | L     | U
Yellow      | Num 8   | Num 5 | Num 4 | Num 6 | Num 7

### Powerups

Random powerups spawn in random locations and can be picked up by moving over them.  
Powerups allow for the tank to temporarily gain a new turret which shoots special bullets.

### Bouncing bullets

Coming soon

## Configuration

### Adding or editing modes

This can be done in modes.json.

Edit the values in this file to change modes.  
To add a new mode add an item with the key being the mode name. Any item within the mode will change the default.  

In order to change the mode change the line in `Tank Colosseum.py` from `currLvl = Level(screen, imgPath)` to `currLvl = Level(screen, imgPath, 'modeName')` where modeName is the name of the mode to be played.

### Adding or editing levels

Levels are found in `Images\Levels`.  
The png image makes up the walls, where any black pixel is a wall.  
Each level needs a one pixel wide boundry wall going all around the edge of the level.  
Currently only 500x500 levels supported.  
An optional JSON file can be added with the same name as the level name.  
This file can be used to set per level settings. This is normally used to set spawn points (minimum 4).  

### Editing bullet characteristics

Bullet configuration is found in the Bullet class in bullet.py.

Bullet characteristics
- `speed` : The speed of the bullet, uses the same scale as the tank movement
- `rotSpeed` : The rotation speed of the bullet, uses the same scale as the tank rotation
- `ctrlRot` : Whether the user controls the rotation of the bullet or tank when shooting
- `ctrlMov` : Whether the user controls the movement of the bullet or tank when shooting
- `ctrlShoot` : Whether the shooting button is used by the the bullet or tank
- `damage` : The damage of the bullet
- `collide` : Whether the bullet collides with the walls
- `shotDelay` : The time between shots with the current powerup
- `autoMove` : Whether the bullet automatically moves
- `lifetime` : The time before the bullet is despawned
- `blockMov` : Whether the tank movement is blocked when the bullet is spawned in

To edit the powerup ammunition, change the value of the ammo variable at the bottom of bullet.py.

### Adding a new powerup

#### Class

- Add a new class in bullet.py that inherits from the Bullet (or Bullet_Controller) class.  
- No code is required in the class but can be used for extra functionality.  
- To keep consistency with other classes start the name with `B_` (or `BC_` if it inherits from the Bullet_Controller class).  

#### Config

- Add a new item to Bullet.configs where the key is the name of the powerup.  
- Add a new item to the classes and ammo variables (found at the bottom of bullet.py). Use the same string as in the config for the key.  

#### Images

- Add a png file inside `Images\Bullet` with the file name the same as the name of the powerup.  
- Add a png file inside `Images\Powerup` with the file name the same as the name of the powerup.
  - The image should be 17x17 pixels big, use `Images\Powerup\blank.png` as a base.  
- Add four png files inside `Images\Turrets` with the files name the same as the name of the powerup followed by a number.
  - The number should be 0-3 where 0 is for the red tank, 1 for the blue, 2 for the green and 3 for the yellow.
