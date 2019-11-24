import bpy

from .. import fountain


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

        return {"FINISHED"}
