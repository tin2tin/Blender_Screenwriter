bl_info = {
    "name": "Screenwriter",
    "author": "Tintwotin, Samy Tichadou, Gabriel Montagné, Andrea Monzini, Colton J. Provias, Manuel Senfft, Martin Vilcans, Nima Yousefi & John August",
    "version": (0, 1),
    "blender": (2, 81, 0),
    "location": "Text Editor > Sidebar",
    "description": "Write screenplays and convert to them 3D scenes or export to PDF, Final Draft or HTML",
    "warning": "",
    "wiki_url": "",
    "category": "Text Editor",
}

import bpy, subprocess, pip
import sys
from bpy.types import Panel, PropertyGroup, UIList, Operator, OperatorFileListElement
from bpy.props import IntProperty, BoolProperty, PointerProperty, StringProperty, EnumProperty, CollectionProperty

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
from .operators.insert import *
from .operators.assign_keyword_to_objects import *
#from .operators.screenwriter_fountain import *
from .gui import *
from .properties import *


# screenplain
pybin = sys.executable#bpy.app.binary_path_python
try:
    import pip
except ImportError:
    try:
        import ensurepip
        ensurepip.bootstrap(upgrade=True, default_pip=True)
    except ImportError:
        try:
            subprocess.call([pybin, "-m", "ensurepip"])
        except ImportError:
            pass
try:
    import screenplain.parsers.fountain as fountain
except ImportError:
    subprocess.check_call([pybin, '-m', 'pip', 'install', 'screenplain[PDF]'])
    import screenplain.parsers.fountain as fountain


class ObjectProperties(PropertyGroup):
    objectname: StringProperty(name="Name")
    objecttype: StringProperty(name="Type")
    runnable: BoolProperty(name="Visible", default=True)


class KeywordProperties(PropertyGroup):
    name: StringProperty(name="Name")
    objects: CollectionProperty(type=ObjectProperties)
    object_index: IntProperty(update=on_object_index_change)


class AssignKeywordsProperties(PropertyGroup):
    keywords: CollectionProperty(type=KeywordProperties)
    keyword_index: IntProperty(update=on_object_index_change)

    new_keyword: StringProperty(name="Name")


classes = (SCREENWRITER_PT_panel,
            #SCREENWRITER_PT_keywords,
            #SCREENWRITER_PT_objects,
            SCREENWRITER_OT_preview_fountain,
            SCREENWRITER_OT_dual_view,
            SCREENWRITER_OT_export,
            #TEXT_OT_scenes_to_strips,
            TextReplaceProperties,
            SCREENWRITER_PT_sequencer_panel,
            SCREENWRITER_OT_switch_to_scene,
            SCREENWRITER_OT_insert_titlepage,
            SCREENWRITER_OT_insert_scene_numbers,

            RenameKeyword,
            AddKeyword,
            RemoveKeyword,
            MoveKeywordUp,
            MoveKeywordDown,

            AddObjects,
            RemoveObject,
            MoveObjectUp,
            MoveObjectDown,

            #SCREENWRITER_PT_keywords,
            #SCREENWRITER_PT_objects,

            OBJECT_UL_screenwriter_keywords,
            OBJECT_UL_screenwriter_objects,

            ObjectProperties,
            KeywordProperties,
            AssignKeywordsProperties,

            SCREENWRITER_OT_to_strips,
            SCREENWRITER_OT_specific_to_strips,
            SCREENWRITER_OT_strips_to_markers,
            SCREENWRITER_OT_clear_markers
            )

# import specific
##################################

# reg/unreg
##################################

def register():
    ### OPERATORS ###
    from bpy.utils import register_class
    from bpy.types import Scene

    for cls in classes :
        register_class(cls)

    Scene.keywords_assigner = PointerProperty(type=AssignKeywordsProperties)
    bpy.types.Scene.screenwriter_channel = bpy.props.IntProperty(default=0, min=0)

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
    from bpy.types import Scene
    for cls in classes :
        unregister_class(cls)

    del Scene.keywords_assigner
    del bpy.types.Scene.screenwriter_channel

    ### MENU ###
    bpy.types.TEXT_MT_text.remove(screenwriter_menu_export)

    ### PROPERTIES ###
    del bpy.types.Scene.last_character
    del bpy.types.Scene.last_line
    del bpy.types.Scene.last_line_index
    del bpy.types.Scene.text_replace
    del bpy.types.Scene.title_page_index
