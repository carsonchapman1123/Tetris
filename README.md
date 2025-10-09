# Tetris

This is a Tetris implementation done in Python using the Tkinter module. It can be run using the following commands:

```bash
git clone https://github.com/carsonchapman1123/Tetris
cd Tetris
python tetris.py
```

You might need to use a package manager such as pip to install required modules if you do not have them installed already.

### Controls
Move piece left/right: left/right arrow keys or A/D\
Rotate piece: up arrow key or W\
Move down faster: down arrow key or S\
Move piece all the way down: space bar\
Pause: P\
Reset after losing: R

### Changing the Difficulty
The difficulty can be changed by updating the `FRAMES_PER_SECOND` constant. Higher numbers are more difficult and lower numbers are easier.

### Gameplay
Below is a screenshot of this Tetris game following a loss. The right side of the screen contains the piece queue.

![Model](https://github.com/carsonchapman1123/Tetris/blob/main/images/tetris.png)

### Game Design
The game is implemented using a list of currently active blocks called `active_blocks` and a list of inactive blocks called `inactive_blocks`. Blocks are spawned in and added to the active blocks. Once any of the active blocks collide with the bottom of the game window or an inactive block they will be deactivated.

A state machine handles different behaviors in the game, such as `spawn_shape`, `shape_moving`, and `clearing_rows` so that the appropriate functions are called during each game tick.

Rotation of the blocks is handled by a rotation point for each type of block, which is the (x, y) coordinate that the shape will rotate about using the rotation matrix formula.

Most of the game's variables are defined in constants at the top of `tetris.py`. These variables can be changed to update the size of the game window as well as other features described in comments next to each variable. Some variables will need to be edited simultaneously in order for things to look correct on the screen, for example the title tile width will need to shrink if the game window is shrunken to the point where the logo will block the score or gameplay window.