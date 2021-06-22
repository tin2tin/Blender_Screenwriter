# Blender Screenwriter
Screenplay formatting in Blender Text Editor of Fountain markup syntax.  

### Demo of Main Features
[![Img alt text](https://github.com/tin2tin/Blender_Screenwriter/blob/master/yt_thumb.jpg?raw=true)](https://www.youtube.com/watch?v=KIqQH_e8Hs4)

![](bsw_tut.gif)

### Features

- Write screenplays in Blender Text Editor.
- Get live preview of screenplay formatting.
- Use the simple fountain markup syntax.
- Export to fdx(Final Draft).
- Export to Html.
- Assign 3d objects to keywords.
- Script to Screen sequence generation.
- Save as Fountain.
- Extract screenplay data and timings.
- Auto create a sequence with 3D scenes and dialogue as subtitles. 

### How to Install

Use Blender 2.82 Beta or higher.

Download the repository as zip and use the normal Blender installation procedure.

In the Text Editor Sidebar you'll find the Screenwriting buttons. They'll be disabled until you save a text-block with a .fountain extention or open .fountain a file. 

To export the Screenplain[PDF] module https://github.com/vilcans/screenplain is needed. It should install automatic, but if installation fails on GNU/Linux, it can be installed with 2 commands in the terminal:
* '/INSTALLED_BLENDER_PATH/2.81/python/bin/python3.7m' -m ensurepip
* '/INSTALLED_BLENDER_PATH/2.81/python/bin/python3.7m' -m pip install screenplain[PDF]

Alternatively this add-on can be used for module installation in Blender: https://github.com/amb/blender_pip/releases

### Test Screenplay Files
https://fountain.io/_downloads/Big%20Fish.fountain

https://fountain.io/_downloads/Brick%20&%20Steel.fountain

https://fountain.io/_downloads/The%20Last%20Birthday%20Card.fountain

### Fountain Syntax
https://github.com/derickc/Fountainhead#fountain-syntax

### More Blender Fountain add-ons
Adding markers and writing timed script into the 3D View:
https://github.com/tin2tin/blender-fountain-addon

Improved timing and more info as text strips:
https://github.com/gabrielmontagne/blender-addon-unfurl-fountain

### About

This add-on utilizes a fountain script parser, which converts .fountain files to python object. The Fountain screenplay format is by Nima Yousefi & John August; original code for Objective-C at https://github.com/nyousefi/Fountain. It is ported to Python 3 by Colton J. Provias, improved by Manuel Senfft https://github.com/Tagirijus/fountain. The Screenplain module by Martin Vilcans is used for exports https://github.com/vilcans/screenplain. 
