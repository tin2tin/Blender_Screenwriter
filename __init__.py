bl_info = {
    "name": "Blender Screenwriter with Fountain Live Preview",
    "author": "Tintwotin, Samy Tichadou, Andrea Monzini, Colton J. Provias, Manuel Senfft, Martin Vilcans, Nima Yousefi & John August",
    "version": (0, 1),
    "blender": (2, 81, 0),
    "location": "Text Editor > Sidebar",
    "description": "Adds functions for editing of Fountain file with live screenplay preview",
    "warning": "",
    "wiki_url": "",
    "category": "Text Editor",
}

import bpy
from bpy.props import IntProperty, BoolProperty, PointerProperty, StringProperty, EnumProperty


# load and reload submodules
##################################

# import importlib, inspect
# from . import developer_utils
# importlib.reload(developer_utils)
# modules = developer_utils.setup_addon_modules(__path__, __name__, "bpy" in locals())
# classes = []
# for module in modules:
#     for name, obj in inspect.getmembers(module):
#         if debug: print("registered --- " + name)
#         if inspect.isclass(obj) and name != "persistent":
#             classes.append(obj)

from .operators.dual_view import *
from .operators.fountain_export import *
from .operators.preview_fountain import *
from .operators.scene_to_strip import *
from .operators.switch_to_scene import *
from .gui import *
from .properties import *

classes = (SCREENWRITER_PT_panel,
            SCREENWRITER_OT_preview_fountain,
            SCREENWRITER_OT_dual_view,
            SCREENWRITER_OT_export,
            TEXT_OT_scenes_to_strips,
            TextReplaceProperties, 
            SCREENWRITER_PT_sequencer_panel,
            SCREENWRITER_OT_switch_to_scene,          
            )

# import specific
##################################

# reg/unreg
##################################

def register():
    ### OPERATORS ###
    from bpy.utils import register_class
    for cls in classes :
        register_class(cls)

    ### MENU ###
    bpy.types.TEXT_MT_text.append(screenwriter_menu_export)

    ### PROPERTIES ###
    bpy.types.Scene.last_character = IntProperty(default=0)
    bpy.types.Scene.last_line = StringProperty(default="")
    bpy.types.Scene.last_line_index = IntProperty(default=0)
    bpy.types.Scene.text_replace = PointerProperty(type=TextReplaceProperties)
    bpy.types.Scene.title_page_index = IntProperty(default=0)

def unregister():
    ### OPERATORS ###
    from bpy.utils import unregister_class
    for cls in classes :
        unregister_class(cls)

    ### MENU ###
    bpy.types.TEXT_MT_text.remove(screenwriter_menu_export)

    ### PROPERTIES ###
    del bpy.types.Scene.last_character
    del bpy.types.Scene.last_line
    del bpy.types.Scene.last_line_index
    del bpy.types.Scene.text_replace
    del bpy.types.Scene.title_page_index
