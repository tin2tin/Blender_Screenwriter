from bpy.types import Panel, PropertyGroup, UIList, Operator, OperatorFileListElement
from bpy.props import StringProperty, CollectionProperty, IntProperty, PointerProperty, BoolProperty
from pathlib import Path
import bpy
from bpy_extras.io_utils import ImportHelper
from os import path

# ---------------------------------------------------------------------------------------------
# MISC FUNCTIONS
# ---------------------------------------------------------------------------------------------
def on_object_index_change(_, context):
    props = context.scene.keywords_assigner

    if props.keywords:
        keyword = props.keywords[props.keyword_index]

        if keyword.objects:
            file = keyword.objects[keyword.object_index]


# ---------------------------------------------------------------------------------------------
# PROJECT OPERATORS
# ---------------------------------------------------------------------------------------------
class AddKeyword(Operator):
    """Add a new keyword with the content of the text box"""
    bl_idname = "ops.add_keyword"
    bl_label = "Add Keyword"
    bl_options = {"UNDO", "INTERNAL"}

    def execute(self, context):
        props = context.scene.keywords_assigner

        if props.new_keyword:
            keyword = set([x.name for x in props.keywords])

            if props.new_keyword not in keyword:
                keyword = props.keywords.add()
                keyword.name = props.new_keyword
                props.keyword_index = len(props.keywords) - 1
            else:
                self.report({"INFO"}, "A keyword already exists with the name {}".format(props.new_keyword))
        else:
            self.report({"INFO"}, "No keyword name entered.")
        return {"FINISHED"}


class RemoveKeyword(Operator):
    """Remove Keyword"""
    bl_idname = "ops.sw_remove_keyword"
    bl_label = "Remove Keyword"
    bl_options = {"UNDO", "INTERNAL"}

    def execute(self, context):
        props = context.scene.keywords_assigner

        if props.keywords:
            # remove objects
            for file in props.keywords[props.keyword_index].objects:
                block = bpy.data.texts.get(file.name, None)

                if block is not None:
                    context.space_data.text = block
                    bpy.ops.text.unlink()

            props.keywords.remove(props.keyword_index)
            props.keyword_index = max(0, props.keyword_index - 1)

        return {"FINISHED"}


class MoveKeywordUp(Operator):  # "UP" = closer to 0
    """Move Keyword Up"""
    bl_idname = "ops.sw_move_keyword_up"
    bl_label = "Move Keyword Up"
    bl_options = {"UNDO", "INTERNAL"}

    def execute(self, context):
        props = context.scene.keywords_assigner

        if props.keyword_index > 0:  # do we have room to move towards 0 by one unit?
            props.keywords.move(props.keyword_index, props.keyword_index-1)
            props.keyword_index = max(0, props.keyword_index-1)

        return {"FINISHED"}


class MoveKeywordDown(Operator):  # "DOWN" = closer to len(list)
    """Move Keyword Down"""
    bl_idname = "ops.sw_move_keyword_down"
    bl_label = "Move Keyword Down"
    bl_options = {"UNDO", "INTERNAL"}

    def execute(self, context):
        props = context.scene.keywords_assigner

        if props.keyword_index < len(props.keywords):  # do we have room to move towards the end?
            props.keywords.move(props.keyword_index, props.keyword_index+1)
            props.keyword_index = min(len(props.keywords)-1, props.keyword_index+1)

        return {"FINISHED"}


class RenameKeyword(Operator):
    """Renames selected keyword to the name in the text box"""
    bl_idname = "ops.rename_keyword"
    bl_label = "Rename Keyword"
    bl_options = {"UNDO", "INTERNAL"}

    def execute(self, context):
        props = context.scene.keywords_assigner

        if props.keywords and props.new_keyword != "":
            keyword = set([x.name for x in props.keywords])

            if props.new_keyword not in keyword:
                props.keywords[props.keyword_index].name = props.new_keyword
            else:
                self.report({"INFO"}, "A keyword already exists with the name {}".format(props.new_keyword))

        return {"FINISHED"}


class GetKeyword(Operator):
    """Add selected text as keyword"""
    bl_idname = "ops.get_keyword"
    bl_label = "Get Keyword"
    bl_options = {"UNDO", "INTERNAL"}
       
    s: StringProperty(default='')

    def execute(self, context): 
        
        s=self.s        

        if context.area.type == 'TEXT_EDITOR' and context.space_data.text:  
            
            text = context.space_data.text
            s = self.get_selected_text(text)
            
            if s is None:
                bpy.ops.text.select_word()
                s = self.get_selected_text(text)

            props = context.scene.keywords_assigner
            props.new_keyword = s

        return {'FINISHED'}


    def get_selected_text(self, text):

        current_line = text.current_line
        select_end_line = text.select_end_line

        current_character = text.current_character
        select_end_character = text.select_end_character

        # if there is no selected text return None
        if current_line == select_end_line:
            if current_character == select_end_character:
                return None
            else:
                return current_line.body[min(current_character, select_end_character):max(current_character, select_end_character)]

        text_return = None
        writing = False
        normal_order = True  # selection from top to bottom

        for line in text.lines:
            if not writing:
                if line == current_line:
                    text_return = current_line.body[current_character:] + "\n"
                    writing = True
                    continue
                elif line == select_end_line:
                    text_return = select_end_line.body[select_end_character:] + "\n"
                    writing = True
                    normal_order = False
                    continue
            else:
                if normal_order:
                    if line == select_end_line:
                        text_return += select_end_line.body[:select_end_character]
                        break
                    else:
                        text_return += line.body + "\n"
                        continue
                else:
                    if line == current_line:
                        text_return += current_line.body[:current_character]
                        break
                    else:
                        text_return += line.body + "\n"
                        continue

        return text_return


# ---------------------------------------------------------------------------------------------
# FILE OPERATORS
# ---------------------------------------------------------------------------------------------
class AddObjects(Operator):
    bl_idname = "ops.sw_add_objects"
    bl_label = "Add Objects(s)"
    bl_options = {"UNDO", "INTERNAL"}

    def invoke(self, context, event):
        props = context.scene.keywords_assigner

        if props.keywords:
            keyword = props.keywords[props.keyword_index]
            scn = context.scene
        
            keyword_objects = set([x.objectname for x in keyword.objects])

            if context.object:
                for obj in bpy.context.selected_objects:
                    if obj.name not in keyword_objects:                   
                        new_file = keyword.objects.add()
                        new_file.objectname = obj.name
                        new_file.objecttype = obj.type
                    else:
                        self.report({"INFO"}, "This keyword already has an object named {}".format(obj.name))

        return {"FINISHED"}

 
class RemoveObject(Operator):
    bl_idname = "ops.sw_remove_file"
    bl_label = "Remove Object"
    bl_options = {"UNDO", "INTERNAL"}

    def execute(self, context):
        props = context.scene.keywords_assigner

        if props.keywords:
            keyword = props.keywords[props.keyword_index]

            if keyword.objects:
                block = bpy.data.texts.get(keyword.objects[keyword.object_index].name, None)
                if block is not None:
                    context.space_data.text = block
                    bpy.ops.text.unlink()

                keyword.objects.remove(keyword.object_index)
                keyword.object_index = max(0, keyword.object_index - 1)

        return {"FINISHED"}


class MoveObjectUp(Operator):  # "UP" = closer to 0
    """Move Object Up"""
    bl_idname = "ops.sw_move_file_up"
    bl_label = "Move Object Up"
    bl_options = {"UNDO", "INTERNAL"}

    def execute(self, context):
        props = context.scene.keywords_assigner

        if props.keywords:
            keyword = props.keywords[props.keyword_index]

            if keyword.object_index > 0:  # do we have room to move towards 0 by one unit?
                keyword.objects.move(keyword.object_index, keyword.object_index-1)
                keyword.object_index = max(0, keyword.object_index-1)

        return {"FINISHED"}


class MoveObjectDown(Operator):  # "DOWN" = closer to len(list)
    """Move Keyword Down"""
    bl_idname = "ops.sw_move_file_down"
    bl_label = "Move Object Down"
    bl_options = {"UNDO", "INTERNAL"}

    def execute(self, context):
        props = context.scene.keywords_assigner

        if props.keywords:
            keyword = props.keywords[props.keyword_index]

            if keyword.object_index < len(keyword.objects):  # do we have room to move towards the end?
                keyword.objects.move(keyword.object_index, keyword.object_index+1)
                keyword.object_index = min(len(keyword.objects)-1, keyword.object_index+1)

        return {"FINISHED"}
