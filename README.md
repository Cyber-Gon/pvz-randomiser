<h1 align="center">Plants Vs. Zombies 1 Randomiser</h1>

## INSTALLING

Remember that you must be on the original _non-GOTY_ edition of pvz (1.0.0.1051) which is not available on Steam. If you only have GOTY, use the [following guide](https://www.speedrun.com/pvz/guides/swt9q) to downpatch Steam version ([downpatch file](https://www.speedrun.com/pvz/resources/zbp50)), ([accompanying files](https://www.speedrun.com/pvz/resources/lc4qt)).

You need Python installed (3.10 or above).

Download latest release from Releases tab - zip file contains randomiser.py file and pvz folder. On Linux you don't need pvz folder. On Windows you need it only if you didn't install pvz package through pip. Place script wherever you want - pvz folder (if present) has to be together with randomiser.py.

### Windows

This project requires 'pvz' Python package - this repository supplies that package in 'pvz' folder, so you don't need to install anything - just keep pvz folder together with randomiser.py, and don't rename it. You can install pvz package manually with pip install pvz if you wish.

Refer to [this video](https://www.youtube.com/watch?v=av51yBvRp2w) - outdated.

### Linux

Linux doesn't require installing pvz package.

#### Install tkinter:

Debian/Ubuntu:
```
sudo apt install python3-tk
```
Fedora:
```
sudo dnf install python3-tkinter
```
Gentoo:
Add the `tk` USE flag for `dev-lang/python` and then run 
```
sudo emerge -avuDN @world
```

The script should then work with just ``python3 randomiser.py``

## PLAYING

Remember that you should start the randomiser script _after_ you've started the game. Also you need to make new profile in game for every randomiser session, even if you're continuing last playthrough.

When you start randomiser, settings menu will open. You input any settings you want (you can hover mouse over settings to see what they do) and click one of modes on the right. Adventure mode is recommended to play. After clicking game mode the settings window will close, but still will have console window open - don't close it. Then you can start playing (in Adventure most randomizations begin to work after you beat 1-1).

Randomizer supports continuing last playthrough - for that you do same workflow as for new game, but you click "Continue last run" button instead of game mode (rules for making new profile and beating 1-1 still apply).