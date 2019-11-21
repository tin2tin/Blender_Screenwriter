import bpy

from .. import fountain
from pathlib import Path


class SCREENWRITER_OT_switch_to_scene(bpy.types.Operator):
    """Switch to Screenplay Scene"""
    bl_idname = "text.switch_to_scene"
    bl_label = "Switch to Scene"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        space = bpy.context.space_data
        try: 
            filepath = space.text.name
            if filepath.strip() == "": return False
            return ((space.type == 'TEXT_EDITOR')
                    and Path(filepath).suffix == ".fountain")
        except AttributeError: return False

    def execute(self, context):

        return {'FINISHED'}