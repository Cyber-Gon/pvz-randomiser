<h1 align="center">Plants Vs. Zombies 1 Randomiser</h1>

## INSTALLING

Remember that you must be on the _non-GOTY_ edition of pvz. If you only have GOTY, DM a mod on [the pvz speedrunning discord server](https://discord.gg/R8tPmjs).

### Windows

Refer to [this video](https://www.youtube.com/watch?v=av51yBvRp2w).

Remember that you should start the randomiser script _after_ you've started the game.
If console writes "No module named 'pvz'", despite you installing pvz module (through pip install pvz command) that might mean that you have conflicting python versions: pvz module is installed in one version, while .py file is associated with different version. In that case it is recommended that you start randomizer through command line (python <path_to_randomiser.py> command in command line) instead of double-clicking .py file

### Linux

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
