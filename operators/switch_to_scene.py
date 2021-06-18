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
        bpy.ops.scene.preview_fountain() # update title_page_index
        fountain_script = bpy.context.area.spaces.active.text.as_string()

        if fountain_script.strip() == "": return {"CANCELLED"}
        F = fountain.Fountain(fountain_script)

        current_text = bpy.context.space_data.text.name
        if current_text.strip() == "": return

        Nscene = -1
        for fc, f in enumerate(F.elements):
            if f.element_type == 'Scene Heading':
                Nscene = Nscene + 1
            if bpy.context.scene.title_page_index == f.original_line:
                bpy.context.window.scene = bpy.data.scenes[Nscene]
                break

        return {'FINISHED'}
