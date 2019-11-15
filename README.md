# Blender_Screenwriter
Screenplay formatting in Blender Text Editor of Fountain markup syntax.  

### How to

Download here: https://github.com/tin2tin/Blender_Screenwriter/releases and use the normal Blender installation procedure.

In the Text Editor Sidebar you'll find the Screenwriting buttons. They'll be disabled until you create a text-block with a .fountain extention or open .fountain a file. 

To export the Screenplain module is needed. It should install automatic, but if installation fails on GNU/Linux, it can be installed with 2 commands in the terminal:
* '/INSTALLED_BLENDER_PATH/2.81/python/bin/python3.7m' -m ensurepip
* '/INSTALLED_BLENDER_PATH/2.81/python/bin/python3.7m' -m pip install screenplain

### Test Screenplay Files
https://fountain.io/_downloads/Big%20Fish.fountain

https://fountain.io/_downloads/Brick%20&%20Steel.fountain

https://fountain.io/_downloads/The%20Last%20Birthday%20Card.fountain

### Fountain Syntax
https://github.com/derickc/Fountainhead#fountain-syntax

### About

This add-on utilizes a fountain script parser, which converts .fountain files to python object. The Fountain screenplay format is by Nima Yousefi & John August; original code for Objective-C at https://github.com/nyousefi/Fountain. It is ported to Python 3 by Colton J. Provias, improved by Manuel Senfft https://github.com/Tagirijus/fountain. The Screenplain module by Martin Vilcans is used for exports https://github.com/vilcans/screenplain. 
