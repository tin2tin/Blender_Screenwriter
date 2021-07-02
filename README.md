# Blender Screenwriter
Screenplay formatting in Blender Text Editor of Fountain markup syntax.  

### Demo of Main Features
[![Img alt text](https://github.com/tin2tin/Blender_Screenwriter/blob/master/yt_thumb.jpg?raw=true)](https://www.youtube.com/watch?v=KIqQH_e8Hs4)

![](bsw_tut.gif)

### Features

## Screenwriter
- Write screenplays in Blender Text Editor.
- Get live preview of screenplay formatting.
- Use the simple fountain markup syntax.
- Open as Fountain.
- Save as Fountain.
- Change font(for preview).
- Insert Title Page.
- Insert scene numbers.
- Correct caps.
- Insert [[SHOT: ]] note/comment - will generate a camera in the scene. 
- ">my action<" will center action.
- ">" will force transition.
- "@" will force character(may not be supported by all fountain parsers).
- "." will force scene header.
- Export to pdf.
- Export to fdx(Final Draft).
- Export to Html.

## Screenplayer
- Script to Screen sequence generation.
- Assign 3d objects to screenplay keywords.
- Extract screenplay data and timings.
- Create a sequence with scene headings, action and dialogue as timed text strips.
- Generate scenes for each screenplay scene.
- Populated scenes with 3d objects assigned to words in the screenplay scene, where the words appear.
- If more cameras are assigned to a scene, scene strips pointing to cameras and a multicam strip will be added to the master edit.
- Generate cameras for each [[SHOT: ]] note/comment in the scenes where they appear. 
- Switch to the 3d scene based on the position of the screenplay scene.
- Switch back to the master edit scene.


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

### More Blender Screenwriter utility add-ons

Add searchable markers for outlining and navigating the text:
https://github.com/tin2tin/TextMarker-blender-addon

Adding markers and writing timed script into the 3D View:
https://github.com/philippe-lavoie/blender-fountain-addon

Switch cameras in 3D View from Sequencer:
https://github.com/tin2tin/scene_strip_tools

Switch to the scene of the Scene strip:
https://github.com/tin2tin/VSESwitchToScene

Link text from TExt strip to text in 3D View:
https://github.com/gabrielmontagne/blender-addon-link-text-to-vse-subtitle

Split text to node editor frames:
https://github.com/gabrielmontagne/blender-addon-split-frame-from-text

Link text to node editor frames:
https://github.com/gabrielmontagne/blender-addon-link-text-to-frame



### About

This add-on utilizes a fountain script parser, which converts .fountain files to python object. The Fountain screenplay format is by Nima Yousefi & John August; original code for Objective-C at https://github.com/nyousefi/Fountain. It is ported to Python 3 by Colton J. Provias, improved by Manuel Senfft https://github.com/Tagirijus/fountain. The Screenplain module by Martin Vilcans is used for exports https://github.com/vilcans/screenplain. 
