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
            return ((space.type == 'TEXT_EDITOR'))
                    #and Path(filepath).suffix == ".fountain")
        except AttributeError: return False

    def execute(self, context):
        bpy.ops.scene.preview_fountain() # update title_page_index
        fountain_script = bpy.context.area.spaces.active.text.as_string()

        if fountain_script.strip() == "": return {"CANCELLED"}
        F = fountain.Fountain(fountain_script)

        current_text = bpy.context.space_data.text.name
        if current_text.strip() == "": return

        current_scene = bpy.context.window.scene

        scene_name = ""
        scene_name_found = ""
        for fc, f in enumerate(F.elements):
            if f.element_type == 'Scene Heading':
                scene_name = f.element_text.title()
            if bpy.context.scene.title_page_index == f.original_line:
                scene_name_found = scene_name
                for s in bpy.data.scenes:
                    if scene_name == s.name:
                        bpy.context.window.scene = bpy.data.scenes[scene_name]
                        break
                break
        if current_scene.name == bpy.context.window.scene.name and scene_name_found:
            msg = "Scene not found: " + scene_name_found
            self.report({'INFO'}, msg)

        return {'FINISHED'}


class SCREENWRITER_OT_switch_to_master(bpy.types.Operator):
    """Switch to Master Sequence Scene"""
    bl_idname = "text.switch_to_master"
    bl_label = "Switch to Master"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        space = bpy.context.space_data
        try: 
            filepath = space.text.name
            if filepath.strip() == "": return False
            return ((space.type == 'TEXT_EDITOR'))
                    #and Path(filepath).suffix == ".fountain")
        except AttributeError: return False

    def execute(self, context):
        scene = bpy.context.scene
        if scene.master_sequence != "":
            bpy.context.window.scene = bpy.data.scenes[scene.master_sequence]

        return {'FINISHED'}