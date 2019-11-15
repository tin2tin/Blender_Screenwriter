bl_info = {
    "name": "Blender Screenwriter with Fountain Live Preview",
    "author": "Tintwotin,  Andrea Monzini, Fountain Module by Colton J. Provias & Manuel Senfft, Export Module by Martin Vilcans. Fountain Format by Nima Yousefi & John August",
    "version": (0, 1),
    "blender": (2, 81, 0),
    "location": "Text Editor > Sidebar",
    "description": "Adds functions for editing of Fountain file with live screenplay preview",
    "warning": "",
    "wiki_url": "",
    "category": "Text Editor",
}

debug = 1

import bpy
from bpy.props import IntProperty, BoolProperty, PointerProperty, StringProperty, EnumProperty


# load and reload submodules
##################################

import importlib, inspect
from . import developer_utils
importlib.reload(developer_utils)
modules = developer_utils.setup_addon_modules(__path__, __name__, "bpy" in locals())
classes = []
for module in modules:
    for name, obj in inspect.getmembers(module):
        if debug: print("registered --- " + name)
        if inspect.isclass(obj) and name != "persistent":
            classes.append(obj)


# import specific
##################################

from .gui import screenwriter_menu_export
from .properties import TextReplaceProperties


# reg/unreg
##################################

def register():
    bpy.types.TEXT_MT_text.append(screenwriter_menu_export)

    bpy.types.Scene.last_character = IntProperty(default=0)
    bpy.types.Scene.last_line = StringProperty(default="")
    bpy.types.Scene.last_line_index = IntProperty(default=0)
    bpy.types.Scene.text_replace = PointerProperty(type=TextReplaceProperties)


def unregister():
    bpy.types.TEXT_MT_text.remove(screenwriter_menu_export)

    del bpy.types.Scene.last_character
    del bpy.types.Scene.last_line
    del bpy.types.Scene.last_line_index
    del bpy.types.Scene.text_replace