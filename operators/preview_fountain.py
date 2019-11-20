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
        try:
            filepath = space.text.name
            #filepath = bpy.context.area.spaces.active.text.filepath
            if filepath.strip() == "": return False
            return ((space.type == 'TEXT_EDITOR')
                    and Path(filepath).suffix == ".fountain")
        except AttributeError: return False

    def execute(self, context):
        space = bpy.context.space_data
        dir = os.path.dirname(bpy.data.filepath)
        if not dir in sys.path:
            sys.path.append(dir)

        #current_text = os.path.basename(bpy.context.space_data.text.filepath)
        current_text = bpy.context.space_data.text.name
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
        else:
            current_line = bpy.data.texts[current_text].current_line_index

        # Layout
        current_character = bpy.data.texts[current_text].current_character
        jump_to_line = 0
        margin = " " * 4
        document_width = 60 + len(margin)
        document_height = 56
        action_wrapper = textwrap.TextWrapper(width=document_width)
        dialogue_wrapper = textwrap.TextWrapper(width=37 + int(len(margin) / 2))
        dialogue_indentation = 13 + int(len(margin) / 2)
        cursor_indentation = margin
        add_characters = current_character
        cursor_indentation_actual = ""
        text = bpy.context.area.spaces.active.text
        current_line_length = len(text.current_line.body)
        add_characters_actual = 0
        end_line_title = ""
        end_line_nr = 0
        block_indent = " "*40

        # Add a Title Page
        if contents_has_metadata:

            # add title
            for meta in iter(F.metadata.items()):
                if meta[0] == 'title':
                    # blank lines
                    for l in range(int(document_height/2)-len(meta[1])):
                        bpy.data.texts[filename].write(chr(10))
                    # title
                    for i in meta[1]:
                        bpy.data.texts[filename].write(margin+((str(i)).center(document_width)+chr(10)))
                        end_line_title = str(i)
                        end_line_nr = bpy.data.texts[filename].current_line_index

                # add credit
                elif meta[0] == 'credit' or meta[0] == 'credits':
                    for i in meta[1]:
                        bpy.data.texts[filename].write(chr(10)+margin+(str(i).center(document_width)+chr(10)+chr(10)))
                        end_line_title = str(i)
                        end_line_nr = bpy.data.texts[filename].current_line_index

                # get author
                elif meta[0] == 'author' or meta[0] == 'authors':
                    for i in meta[1]:
                        bpy.data.texts[filename].write(margin+(str(i).center(document_width)+chr(10)+chr(10)))
                        end_line_title = str(i)
                        end_line_nr = bpy.data.texts[filename].current_line_index

                # get source
                elif meta[0] == 'source':
                    for i in meta[1]:
                        bpy.data.texts[filename].write(chr(10)+margin+(str(i).center(document_width)+chr(10)))
                        end_line_title = str(i)
                        end_line_nr = bpy.data.texts[filename].current_line_index

                # get date
                elif meta[0] == 'draft date' or meta[0] == 'date':
                    for i in meta[1]:
                        bpy.data.texts[filename].write(block_indent+margin+(str(i)+chr(10)))

                # get contact
                elif meta[0] == 'contact':
                    for i in meta[1]:
                        bpy.data.texts[filename].write(block_indent+margin+(str(i)+chr(10)))

            # insert blank lines after title
            if end_line_title != 0:
                cli = bpy.data.texts[filename].current_line_index
                blank_lines = ""
                for l in range(document_height - cli-2):
                    blank_lines = blank_lines + chr(10)

                txt = bpy.data.texts[filename].as_string()
                text = txt.replace(end_line_title, end_line_title+blank_lines)
                bpy.data.texts[filename].clear()
                bpy.data.texts[filename].write(text)

            # add pagebreak
            bpy.data.texts[filename].write(chr(10) + margin + ("_" * document_width) + chr(10))

        for fc, f in enumerate(F.elements):
            add_characters = current_character
            if f.element_type == 'Scene Heading':
                if str(f.scene_number) != "": f.scene_number = f.scene_number+ " "
                bpy.data.texts[filename].write(
                    margin + f.scene_number+ f.scene_abbreviation.upper() + " " + f.element_text.upper() + chr(10))
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
                    chr(10))
                cursor_indentation = margin + ("_" * ((f.element_text.center(
                    document_width)).find(f.element_text)))
            elif f.element_type == 'Parenthetical':
                bpy.data.texts[filename].write(
                    margin + f.element_text.center(document_width).lower() +
                    chr(10))
                cursor_indentation = margin + ("_" * int(
                    (document_width / 2 - len(f.element_text) / 2)))
            elif f.element_type == 'Dialogue':
                dialogue = f.element_text
                current_character
                line_list = dialogue_wrapper.wrap(text=dialogue)
                for dialogue in line_list:
                    bpy.data.texts[filename].write(margin + (
                        " " * dialogue_indentation + dialogue) + chr(10))
                cursor_indentation = margin + (" " * dialogue_indentation)
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
            if current_line >= f.original_line and f.original_line != 0:
                jump_to_line = bpy.data.texts[filename].current_line_index
                cursor_indentation_actual = cursor_indentation

        line = jump_to_line - 1
        if line < 0: line = 0
        bpy.data.texts[filename].current_line_index = line
        cur = current_character + len(cursor_indentation_actual)
        bpy.data.texts[filename].select_set(line, cur, line, cur)

        return {"FINISHED"}
