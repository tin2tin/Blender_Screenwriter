import bpy, textwrap, os, sys, re, math

from .. import fountain
from pathlib import Path


def operator_exists(idname):
    from bpy.ops import op_as_string
    try:
        op_as_string(idname)
        return True
    except:
        return False


class SCREENWRITER_OT_mindmap_fountain(bpy.types.Operator):
    '''Generates the mindmap'''
    bl_idname = "screenwriter.mindmap_fountain"
    bl_label = "Generate Mindmap"

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

        #current_text = os.path.basename(bpy.context.space_data.text.filepath)
        current_text = bpy.context.space_data.text.name
        if current_text.strip() == "": return

        fountain_script = bpy.context.area.spaces.active.text.as_string()
        if fountain_script.strip() == "": return {"CANCELLED"}

        # Clean out notes and comments.
        reg_exp = "\\[\\[(.*?)\\]\\]"
        fountain_script = re.sub(reg_exp, "", fountain_script)

        # Clean out multiple empty lines.
        reg_exp = "'[\n]+', '\n'"
        fountain_script = re.sub(r'[\r\n][\r\n]{2,}', '\n\n', fountain_script)

        for window in bpy.context.window_manager.windows:
            screen = window.screen
            for area in screen.areas:
                if area.type == 'NODE_EDITOR':
                    from bpy import context
                    with context.temp_override(window=window, area=area):
                        if not hasattr(bpy.types, bpy.ops.node.add_node.idname()):
                            print("The Mindmap add-on is not installed!")
                            return {"CANCELLED"}
                        else:
                            bpy.context.scene.use_nodes = True
                            tree = bpy.context.scene.node_tree

                            F = fountain.Fountain(fountain_script)

                            # Get number of header lines
                            contents = fountain_script.strip().replace('\r', '')

                            contents_has_metadata = ':' in contents.splitlines()[0]
                            contents_has_body = '\n\n' in contents

                            if contents_has_metadata and contents_has_body:
                                lines = fountain_script.split('\n\n')
                                lines = lines[0].splitlines()
                                current_line = bpy.data.texts[current_text].current_line_index - len(lines) - 1
                            else:
                                current_line = bpy.data.texts[current_text].current_line_index

                            bpy.context.scene.title_page_index = current_line
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
                            #text = bpy.context.area.spaces.active.text
                            #current_line_length = len(text.current_line.body)
                            add_characters_actual = 0
                            end_line_title = ""
                            end_line_nr = 0
                            contact_indent = ""#" "*35
                            
                            new_node = ""
                            nodes = []
                            nodes_cnt = 0
                            x=0

                            for fc, f in enumerate(F.elements):
                                add_characters = current_character
                                if f.element_type == 'Scene Heading':
                                    if f.scene_abbreviation[0:1] in ['.']: 
                                        f.scene_abbreviation = f.scene_abbreviation[2:]
                                        if str(f.scene_number) != "":
                                            f.scene_number = f.scene_number
                                    elif str(f.scene_number) != "": 
                                        f.scene_number = f.scene_number + " "
                                    if len(f.scene_number + f.scene_abbreviation) > 0:
                                        f.scene_abbreviation += " "
#                                    bpy.data.texts[filename].write(
#                                        margin + f.scene_number+ f.scene_abbreviation.upper() + f.element_text.upper() + chr(10))
                                    bpy.ops.node.add_node(type='MindmapNodeType', use_transform=True)
                                    #new_node = tree.nodes.new(type='MindmapNodeType')
                                    new_node = bpy.context.active_node
                                    if new_node:
                                        nodes.append(new_node)
                                        new_node.label = f.scene_number+ f.scene_abbreviation.upper() + f.element_text.upper()
                                        new_node.my_string_prop = ""
                                        new_node.show_in_single_node = False
                                        new_node.node_image = ""
                                        if (nodes_cnt/10 == int(nodes_cnt/10)):
                                            x = 0
                                        else:
                                            x = nodes_cnt - (10 * math.floor(nodes_cnt/10))
                                        new_node.location = (x*300, math.floor(nodes_cnt/10) * -500)
                                        nodes_cnt += 1

                                elif f.element_type == 'Action' and f.is_centered == False and new_node:
                                    action = f.element_text
                                    action_list = action_wrapper.wrap(text=action)
                                    add_action_lines = 0
                                    for action in action_list:
                                        #bpy.data.texts[filename].write(margin + action + chr(10))
                                        new_node.my_string_prop = new_node.my_string_prop + action
                    #                cursor_indentation = margin
                                    
                                elif f.element_type == 'Action' and f.is_centered == True and new_node:
                    #                bpy.data.texts[filename].write(
                    #                    margin + f.element_text.center(document_width) + chr(10))
                                        new_node.my_string_prop = new_node.my_string_prop + f.element_text
                    #                cursor_indentation = margin + ("_" * (int(
                    #                    (document_width / 2 - len(f.element_text) / 2)) - 2))
                                elif f.element_type == 'Character' and new_node:
                    #                bpy.data.texts[filename].write(
                    #                    margin + f.element_text.center(document_width).upper() +
                    #                    chr(10))
                    #                cursor_indentation = margin + ("_" * ((f.element_text.center(
                    #                    document_width)).find(f.element_text)))
                                    new_node.my_string_prop = new_node.my_string_prop + f.element_text
                                elif f.element_type == 'Parenthetical' and new_node:
                    #                bpy.data.texts[filename].write(
                    #                    margin + f.element_text.center(document_width).lower() +
                    #                    chr(10))
                    #                cursor_indentation = margin + ("_" * int(
                    #                    (document_width / 2 - len(f.element_text) / 2)))
                                    new_node.my_string_prop = new_node.my_string_prop + f.element_text
                                elif f.element_type == 'Dialogue' and new_node:
                    #                dialogue = f.element_text
                                    new_node.my_string_prop = new_node.my_string_prop + f.element_text
                    #                current_character
                    #                line_list = dialogue_wrapper.wrap(text=dialogue)
                    #                for dialogue in line_list:
                    #                    bpy.data.texts[filename].write(margin + (
                    #                        " " * dialogue_indentation + dialogue) + chr(10))
                    #                cursor_indentation = margin + (" " * dialogue_indentation)
                                    
                    #            elif f.element_type == 'Page Break':
                    #                bpy.data.texts[filename].write(
                    #                    chr(10) + margin + ("_" * document_width) + chr(10))
                                # # not for mindmap
                                # elif f.element_type == 'Boneyard':  # Ignored by Fountain formatting
                                #     bpy.data.texts[filename].write(chr(10))
                                # elif f.element_type == 'Comment':  # Ignored by Fountain formatting
                                #     bpy.data.texts[filename].write(chr(10))
                                # elif f.element_type == 'Section Heading':  # Ignored by Fountain formatting
                                #     bpy.data.texts[filename].write(chr(10))
                                # elif f.element_type == 'Synopsis':  # Ignored by Fountain formatting
                                #     bpy.data.texts[filename].write(chr(10))
                                elif f.element_type == 'Transition' and new_node:
                    #                bpy.data.texts[filename].write(
                    #                    margin + f.element_text.rjust(document_width).upper() + chr(10))
                    #                cursor_indentation = margin + ("_" * (
                    #                    document_width - len(f.element_text)))
                                    new_node.my_string_prop = new_node.my_string_prop + f.element_text
#                            bpy.ops.node.select_all(action='SELECT') #crash !?
#                            bpy.ops.node.view_all()
                            
                            print(tree)
                            # create links between nodes
                            for i in range(nodes_cnt-1):
                                tree.links.new(nodes[i].outputs[0], nodes[i+1].inputs[0])
                            return {"FINISHED"}
