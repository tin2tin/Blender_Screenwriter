import bpy

from .. import fountain
from pathlib import Path

class SCREENWRITER_OT_insert_titlepage(bpy.types.Operator):
    """Insert a title page"""
    bl_idname = "screenwriter.insert_title_page"
    bl_label = "Insert Title Page"
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
        space = bpy.context.space_data
        filepath = space.text.name
        if filepath.strip() == "": return {"CANCELLED"}
        txt = bpy.data.texts[filepath].as_string()
        bpy.data.texts[filepath].clear()
        bpy.data.texts[filepath].write("""Title:
    Title 1
    Title 2
Credit: Written by
Author: Author name
Source: Story by...
Draft date: 12/10/2014
Contact:
    Contact Info
    Address Line 1
    Address Line 2
Copyright: (c) 2019 Name of author


        """)
        bpy.data.texts[filepath].write(txt)
        bpy.ops.scene.preview_fountain()
        return {"FINISHED"}


class SCREENWRITER_OT_insert_scene_numbers(bpy.types.Operator):
    """Toggle scene numbers"""
    bl_idname = "screenwriter.insert_scene_numbers"
    bl_label = "Toggle Scene Numbers"
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
        space = bpy.context.space_data
        filepath = space.text.name
        if filepath.strip() == "": return {"CANCELLED"}

        script_body = bpy.data.texts[filepath].as_string()
        scene_nr = 1
        new_body = ""
        lines = str(script_body).splitlines()

        for line in lines:
            org_line = line
            line = line.lstrip()
            full_strip = line.strip()
            if (
                line[0:4].upper() in
                ['INT ', 'INT.', 'EXT ', 'EXT.', 'EST ', 'EST.', 'I/E ', 'I/E.'] or
                line[0:8].upper() in ['INT/EXT ', 'INT/EXT.'] or
                line[0:9].upper() in ['INT./EXT ', 'INT./EXT.']
            ):
                # remove exstisting scene numbers
                if full_strip[-1] == '#' and full_strip.count('#') > 1:
                    scene_number_start = len(full_strip) - \
                        full_strip[::-1].find('#', 1) - 1
                    no_number = full_strip[:scene_number_start].strip('#').strip() + "\n"
                    new_body = new_body + no_number
                # insert scene numbers
                else:
                    new_body = new_body + org_line + " #"+str(scene_nr)+"#" + "\n"
                    scene_nr +=1
            else:
                new_body = new_body + org_line + "\n"

        bpy.data.texts[filepath].clear()
        bpy.data.texts[filepath].write(new_body)
        bpy.ops.scene.preview_fountain()

        return {"FINISHED"}