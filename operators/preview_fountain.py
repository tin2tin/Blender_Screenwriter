import bpy, textwrap, os, sys

from .. import fountain
from pathlib import Path

class SCREENWRITER_OT_preview_fountain(bpy.types.Operator):
    '''Updates the preview'''
    bl_idname = "scene.preview_fountain"
    bl_label = "Refresh"

    @classmethod
    def poll(cls, context):
        space = bpy.context.space_data
        filepath = bpy.context.area.spaces.active.text.filepath
        if filepath.strip() == "": return False
        return ((space.type == 'TEXT_EDITOR')
                and Path(filepath).suffix == ".fountain")

    def execute(self, context):
        space = bpy.context.space_data
        dir = os.path.dirname(bpy.data.filepath)
        if not dir in sys.path:
            sys.path.append(dir)

        current_text = os.path.basename(bpy.context.space_data.text.filepath)
        if current_text.strip() == "": return

        fountain_script = bpy.context.area.spaces.active.text.as_string()
        if fountain_script.strip() == "": return {"CANCELLED"}

        F = fountain.Fountain(fountain_script)

        filename = "Preview.txt"

        if filename not in bpy.data.texts:
            bpy.data.texts.new(filename)  # New document in Text Editor
        else:
            bpy.data.texts[filename].clear()  # Clear existing text

        # Get number of header lines
        contents = fountain_script.strip().replace('\r', '')

        contents_has_metadata = ':' in contents.splitlines()[0]
        contents_has_body = '\n\n' in contents

        if contents_has_metadata and contents_has_body:
            lines = fountain_script.split('\n\n')
            lines = lines[0].splitlines()
            current_line = bpy.data.texts[current_text].current_line_index - len(
                lines) - 1
        # elif contents_has_metadata and not contents_has_body:
        # self._parse_head(contents.splitlines())
        else:
            current_line = bpy.data.texts[current_text].current_line_index

        current_character = bpy.data.texts[current_text].current_character
        jump_to_line = 0
        margin = " " * 4
        document_width = 60 + len(margin)
        action_wrapper = textwrap.TextWrapper(width=document_width)
        dialogue_wrapper = textwrap.TextWrapper(
            width=37 + int(len(margin) / 2))
        dialogue_indentation = 13 + int(len(margin) / 2)
        cursor_indentation = margin
        add_lines = 0
        add_characters = current_character
        cursor_indentation_actual = ""
        text = bpy.context.area.spaces.active.text
        current_line_length = len(text.current_line.body)
        add_lines_actual = 0
        add_characters_actual = 0

        # This is the way to use title stuff
        # for meta in iter(F.metadata.items()):
        # if meta[0] == 'title':
        # bpy.data.texts[filename].write((str(meta[1])).center(document_width)+chr(10))

        add_lines = 0 

        for fc, f in enumerate(F.elements):
            add_lines = -1 
            #add_lines = 0  #int(document_width/current_character)
            add_characters = current_character
            if f.element_type == 'Scene Heading':
                if str(f.scene_number) != "": f.scene_number = f.scene_number+ " "
                bpy.data.texts[filename].write(
                    margin + f.scene_number+ f.scene_abbreviation.upper() + " " + f.element_text.upper() +
                    chr(10))
                   
                cursor_indentation = margin
            elif f.element_type == 'Action' and f.is_centered == False:
                action = f.element_text
                action_list = action_wrapper.wrap(text=action)
                add_action_lines = 0
                
                for action in action_list:
                    bpy.data.texts[filename].write(margin + action + chr(10))
                cursor_indentation = margin
            elif f.element_type == 'Action' and f.is_centered == True:
                bpy.data.texts[filename].write(
                    margin + f.element_text.center(document_width) + chr(10))
                cursor_indentation = margin + ("_" * (int(
                    (document_width / 2 - len(f.element_text) / 2)) - 2))
            elif f.element_type == 'Character':
                bpy.data.texts[filename].write(
                    margin + f.element_text.center(document_width).upper() +
                    chr(10))  # .upper()
                cursor_indentation = margin + ("_" * ((f.element_text.center(
                    document_width)).find(f.element_text)))
            elif f.element_type == 'Parenthetical':
                bpy.data.texts[filename].write(
                    margin + f.element_text.center(document_width).lower() +
                    chr(10))  # .lower()
                cursor_indentation = margin + ("_" * int(
                    (document_width / 2 - len(f.element_text) / 2)))
            elif f.element_type == 'Dialogue':
                dialogue = f.element_text
                current_character
                line_list = dialogue_wrapper.wrap(text=dialogue)
                for dialogue in line_list:
                    bpy.data.texts[filename].write(margin + (
                        " " * dialogue_indentation + dialogue) + chr(10))
                    # if add_characters >= len(dialogue):
                    # add_characters = add_characters-len(dialogue)
                    # add_lines += 1
                cursor_indentation = margin + (" " * dialogue_indentation
                                               )  # + (" "*add_characters)
            elif f.element_type == 'Synopsis':  # Ignored by Fountain formatting
                bpy.data.texts[filename].write(chr(10))
            elif f.element_type == 'Page Break':
                bpy.data.texts[filename].write(
                    chr(10) + margin + ("_" * document_width) + chr(10))
            elif f.element_type == 'Boneyard':  # Ignored by Fountain formatting
                bpy.data.texts[filename].write(chr(10))
            elif f.element_type == 'Comment':  # Ignored by Fountain formatting
                bpy.data.texts[filename].write(chr(10))
            elif f.element_type == 'Section Heading':  # Ignored by Fountain formatting
                bpy.data.texts[filename].write(chr(10))
            elif f.element_type == 'Transition':
                bpy.data.texts[filename].write(
                    margin + f.element_text.rjust(document_width).upper() + chr(10))
                cursor_indentation = margin + ("_" * (
                    document_width - len(f.element_text)))
            elif f.element_type == 'Empty Line':
                bpy.data.texts[filename].write(chr(10))
            #print("org "+str(f.original_line))
            #print("cur "+str(current_line))
            if current_line >= f.original_line and f.original_line != 0:  #current_line
                jump_to_line = bpy.data.texts[filename].current_line_index
                cursor_indentation_actual = cursor_indentation
                add_lines_actual = add_lines
                #print("add line: "+str(add_lines_actual))
                #add_characters_actual = add_characters
        #print("Jump: "+str(jump_to_line))

        line = jump_to_line - 1 #- add_lines_actual
        if line < 0: line = 0
        bpy.data.texts[filename].current_line_index = line
        cur = current_character + len(cursor_indentation_actual)  #+ add_characters_actual
        #print("Character:" + str(cur)+" Line: "+str((line)))
        bpy.data.texts[filename].select_set(line, cur, line, cur)

        return {"FINISHED"}