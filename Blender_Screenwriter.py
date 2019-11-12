bl_info = {
    "name":
    "Blender Screenwriter with Fountain Live Preview",
    "author": "The Community & Fountain module by Manuel Senfft",
    "version": (0, 1),
    "blender": (2, 80, 0),
    "location": "Text Editor > Sidebar",
    "description": "Adds functions for live editing of Fountain file with live screenplay preview",
    "warning": "Dual toggle will not work in 2.81 and 2.82!",
    "wiki_url": "",
    "category": "Text Editor",
}

import bpy
import textwrap
import subprocess
import os
import sys
import fountain
from bpy.props import IntProperty, BoolProperty, PointerProperty, StringProperty
from pathlib import Path
#import fountain2pdf

class FOUNTAIN_PT_panel(bpy.types.Panel):
    """Preview fountain script as formatted screenplay"""
    bl_label = "Screenwriter"
    bl_space_type = 'TEXT_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Text"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        layout.operator("text.dual_view")
        layout.operator("scene.preview_fountain")
        repl = context.scene.text_replace
        layout.prop(repl, "enabled")
        #layout.operator("text.export_to_pdf") #not working yet


class FOUNTAIN_OT_preview_fountain(bpy.types.Operator):
    '''Updates the preview'''
    bl_idname = "scene.preview_fountain"
    bl_label = "Refresh"

    @classmethod
    def poll(cls, context):
        space = bpy.context.space_data
        filepath = bpy.context.area.spaces.active.text.filepath
        return ((space.type == 'TEXT_EDITOR') and
                Path(filepath).suffix == ".fountain")

    def execute(self, context):
        space = bpy.context.space_data
        dir = os.path.dirname(bpy.data.filepath)
        if not dir in sys.path:
            sys.path.append(dir)

        current_text = os.path.basename(bpy.context.space_data.text.filepath)
        bpy.data.texts[current_text]

        fountain_script = bpy.context.area.spaces.active.text.as_string()
        if fountain_script.strip() == "": return {"CANCELLED"}

        F = fountain.Fountain(fountain_script)

        filename = "Preview.txt"

        if filename not in bpy.data.texts:
            bpy.data.texts.new(filename)  # New document in Text Editor
        else:
            bpy.data.texts[filename].clear()  # Clear existing text

        #the scroll lock becomes very unaccurate when there is a header of the left window 
        current_line = bpy.data.texts[current_text].current_line_index-len(F.metadata) #F.metadata is not resulting in the correct number of lines. 
        current_character = bpy.data.texts[current_text].current_character
        jump_to_line = 0
        margin = " "*4
        document_width = 60+len(margin)
        action_wrapper = textwrap.TextWrapper(width=document_width)
        dialogue_wrapper = textwrap.TextWrapper(width=37+int(len(margin)/2))
        dialogue_indentation = 13+int(len(margin)/2)
        
        # title stuff
        # for meta in iter(F.metadata.items()):
            # if meta[0] == 'title':
                # bpy.data.texts[filename].write((str(meta[1])).center(document_width)+chr(10))

        for fc, f in enumerate(F.elements):
            if f.element_type == 'Scene Heading':
                bpy.data.texts[filename].write(margin+f.scene_abbreviation + " " + f.element_text + chr(10)) #.upper()
            elif f.element_type == 'Action' and f.is_centered ==False:
                action = f.element_text
                action_list = action_wrapper.wrap(text=action)
                for action in action_list:
                    bpy.data.texts[filename].write(margin+action+chr(10))
            elif f.element_type == 'Action' and f.is_centered == True:
                bpy.data.texts[filename].write(margin+f.element_text.center(document_width)+chr(10))
            elif f.element_type == 'Character':
                bpy.data.texts[filename].write(margin+f.element_text.center(document_width)+chr(10)) # .upper()
            elif f.element_type == 'Parenthetical':
                bpy.data.texts[filename].write(margin+f.element_text.center(document_width)+chr(10)) # .lower()
            elif f.element_type == 'Dialogue':
                dialogue = f.element_text
                line_list = dialogue_wrapper.wrap(text=dialogue)
                for dialogue in line_list:
                    bpy.data.texts[filename].write(margin+(" "*dialogue_indentation+dialogue)+chr(10))
            elif f.element_type == 'Synopsis':          # Ignored by Fountain formatting
                bpy.data.texts[filename].write(chr(10))
            elif f.element_type == 'Page Break':
                bpy.data.texts[filename].write(chr(10)+margin+("_"*action_wrapper)+chr(10))
            elif f.element_type == 'Boneyard':           # Ignored by Fountain formatting
                bpy.data.texts[filename].write(chr(10))
            elif f.element_type == 'Comment':            # Ignored by Fountain formatting
                bpy.data.texts[filename].write(chr(10))
            elif f.element_type == 'Section Heading':    # Ignored by Fountain formatting
                bpy.data.texts[filename].write(chr(10))
            elif f.element_type == 'Transition':
                bpy.data.texts[filename].write(margin+f.element_text.rjust(document_width)+chr(10))
            elif f.element_type == 'Empty Line':
                bpy.data.texts[filename].write(chr(10))

            #print("org "+str(f.original_line))
            #print("cur "+str(current_line))
            if current_line >= f.original_line and f.original_line != 0: #current_line
                jump_to_line = bpy.data.texts[filename].current_line_index
            
        #print("Jump: "+str(jump_to_line))    
        bpy.data.texts[filename].current_line_index = jump_to_line - 1
        # Set cursor position in 2.81
        # bpy.data.texts[filename].select_set(jump_to_line - 1, current_character, jump_to_line - 1, current_character + 1)
 
        #bpy.ops.text.dual_view()
        return {"FINISHED"}

def get_mergables(areas):
    xs,ys = dict(),dict()
    for a in areas:
        xs[a.x] = a
        ys[a.y] = a
    for area in reversed(areas):
        tx = area.x + area.width + 1
        ty = area.y + area.height + 1
        if tx in xs and xs[tx].y == area.y and xs[tx].height == area.height:
            return area,xs[tx]
        elif ty in ys and ys[ty].x == area.x and ys[ty].width == area.width:
            return area,ys[ty]
    return None,None

def teardown(context):
    while len(context.screen.areas) > 1:
        a,b = get_mergables(context.screen.areas)
        if a and b:
            bpy.ops.screen.area_join(cursor=(a.x,a.y))#,max_x=b.x,max_y=b.y)
            area = context.screen.areas[0]
            region = area.regions[0]
            blend_data = context.blend_data
            bpy.ops.screen.screen_full_area(dict(screen=context.screen,window=context.window,region=region,area=area,blend_data=blend_data))
            bpy.ops.screen.back_to_previous(dict(screen=context.screen,window=context.window,region=region,area=area,blend_data=blend_data))


def split_area(window,screen,region,area,xtype,direction="VERTICAL",factor=0.5,mouse_x=-100,mouse_y=-100):
    beforeptrs = set(list((a.as_pointer() for a in screen.areas)))
    bpy.ops.screen.area_split(dict(region=region,area=area,screen=screen,window=window),direction=direction,factor=factor)
    afterptrs = set(list((a.as_pointer() for a in screen.areas)))
    newareaptr = list(afterptrs-beforeptrs)
    newarea = area_from_ptr(newareaptr[0])
    newarea.type = xtype
    return newarea


def area_from_ptr(ptr):
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.as_pointer() == ptr:
                return area

class TEXT_OT_dual_view(bpy.types.Operator):
    '''Toggles screenplay preview'''
    bl_idname = "text.dual_view"
    bl_label = "Preview"

    @classmethod
    def poll(cls, context):
        space = bpy.context.space_data
        filepath = bpy.context.area.spaces.active.text.filepath
        return ((space.type == 'TEXT_EDITOR') and
                Path(filepath).suffix == ".fountain")

    original_area = None

    def execute(self, context):
        main_scene = bpy.context.scene
        count = 0
        original_type = bpy.context.area.type

        # # setting font (on Windows) not working
        # try:
            # for a in bpy.context.screen.areas:
                # if a.type == 'PREFERENCES': 
                    # bpy.context.area.type ="PREFERENCES"
                    # bpy.context.preferences.view.font_path_ui_mono("C:\\Windows\\Fonts\\Courier.ttf")
                    # break
        # except RuntimeError as ex:
            # error_report = "\n".join(ex.args)
            # print("Caught error:", error_report)
            # #pass
        bpy.context.area.type = original_type
        self.original_area = context.area
        original = context.copy()
        thisarea = context.area
        otherarea = None
        tgxvalue = thisarea.x + thisarea.width + 1
        thistype = context.area.type

        arealist = list(context.screen.areas)

        filename = "Preview.txt"
        if filename not in bpy.data.texts:
            bpy.ops.scene.preview_fountain()
            
            fountain_script = bpy.context.area.spaces.active.text.as_string()            
            if fountain_script.strip() == "":
                msg = "Text-block can't be empty!"
                self.report({'INFO'}, msg)
                return {"CANCELLED"}            

        for area in context.screen.areas:
            if area == thisarea:
                continue
            elif area.x == tgxvalue and area.y == thisarea.y:
                otherarea = area
                break

        if otherarea:  #leave trim-mode

            bpy.ops.screen.area_join(min_x=thisarea.x, min_y=thisarea.y, max_x=otherarea.x, max_y=otherarea.y)

            # normal settings
            bpy.ops.screen.screen_full_area()
            bpy.ops.screen.screen_full_area()
            override = context.copy()
            area = self.original_area
            override['area'] = area
            override['space_data'] = area.spaces.active

            return {"FINISHED"}

        else:  # enter dual-mode

            areax = None

            #split
            window = context.window
            region = context.region
            screen = context.screen
            main = context.area

            main.type = "TEXT_EDITOR"
            ctrlPanel = bpy.ops.screen.area_split(direction="VERTICAL")#, factor=0.7)

            #settings for preview 2.
            bpy.ops.screen.screen_full_area()
            bpy.ops.screen.screen_full_area()
            override = original
            area = self.original_area
            override['area'] = area
            override['space_data'] = area.spaces.active
            override['space_data'].text = bpy.data.texts['Preview.txt']
            override['space_data'].show_region_ui = False
            override['space_data'].show_region_header = False
            override['space_data'].show_region_footer = False
            override['space_data'].show_line_numbers = False
            override['space_data'].show_syntax_highlight = False
            override['space_data'].show_word_wrap = False

            for area in context.screen.areas:
                if area not in arealist:
                    areax = area
                    break

            if areax:
                areax.type = thistype
                return {"FINISHED"}

        return {"CANCELLED"}

handler = None


def get_space(context):
    for area in context.screen.areas:
        if area.type == "TEXT_EDITOR":
            return area.spaces.active


def text_handler(spc, context):

    scene = bpy.context.scene
    text = bpy.context.area.spaces.active.text
    line = text.current_line.body

    if not text:
        return

    if scene.last_line is None and scene.last_line_index != text.current_line_index:
        scene.last_line = line
        scene.last_line_index = text.current_line_index

    if line != bpy.context.scene.last_line and len(line) > len(bpy.context.scene.last_line):
        bpy.ops.scene.preview_fountain()
    scene.last_line = line


def redraw(context):
    for window in context.window_manager.windows:
        for area in window.screen.areas:
            if area.type == 'TEXT_EDITOR':
                area.tag_redraw()


def activate_handler(self, context):
    global handler

    spc = get_space(context)
    if not spc:
        return

    enabled = context.scene.text_replace.enabled

    if enabled:
        handler = spc.draw_handler_add(text_handler, (
            spc,
            context,
        ), "WINDOW", "POST_PIXEL")
        print("handler activated", handler)
    else:
        if handler is not None:
            spc.draw_handler_remove(handler, "WINDOW")
        handler = None
        print("handler deactivated")


class TextReplaceProperties(bpy.types.PropertyGroup):
    enabled: BoolProperty(
        name="Live Preview",
        description="Enables live screenplay preview",
        update=activate_handler,
        default=False)


# NOT WORKING - THE FONT IS TOO LARGE AND IN THE WRONG STYLE # NB. needs Reportlab and a custom fountain2pdf file. 
class TEXT_OT_export_to_pdf(bpy.types.Operator):
    """Add video sequencer scene strips from all screenplay scenes"""
    bl_idname = "text.export_to_pdf"
    bl_label = "Export to PDF"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        space = bpy.context.space_data
        filepath = bpy.context.area.spaces.active.text.filepath
        return ((space.type == 'TEXT_EDITOR') and
                Path(filepath).suffix == ".fountain")

    def execute(self, context):
       
        dir = os.path.dirname(bpy.data.filepath)
        if not dir in sys.path:
            sys.path.append(dir)

        fountain_script = bpy.context.area.spaces.active.text.as_string()
        if fountain_script.strip() == "": return {"CANCELLED"}

        old_filename = bpy.context.space_data.text.filepath
        bpy.types.Scene.codestyle_name = old_filename
        filename = bpy.utils.script_path_user() + "\\addons\\screenplay.txt"
        bpy.ops.text.save_as(filepath=filename, check_existing=False)

        cmd = chr(34)+bpy.utils.script_path_user()+"\\addons\\fountain2pdf.pdf"+chr(34)+' "%s"' % (filename)
        print(cmd)
        process = subprocess.Popen(cmd,
                                   shell=True,
                                   stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        o, e = process.communicate()
        print(o, e)

        bpy.context.space_data.text.filepath = old_filename
        return {'FINISHED'}


def register():
    bpy.utils.register_class(FOUNTAIN_PT_panel)
    bpy.utils.register_class(FOUNTAIN_OT_preview_fountain)
    bpy.utils.register_class(TEXT_OT_dual_view)
    bpy.utils.register_class(TEXT_OT_export_to_pdf)

    bpy.types.Scene.last_line = StringProperty(default="")
    bpy.types.Scene.last_line_index = IntProperty(default=0)

    bpy.utils.register_class(TextReplaceProperties)
    bpy.types.Scene.text_replace = PointerProperty(type=TextReplaceProperties)


def unregister():
    bpy.utils.unregister_class(FOUNTAIN_PT_panel)
    bpy.utils.unregister_class(FOUNTAIN_OT_preview_fountain)
    bpy.utils.unregister_class(TEXT_OT_dual_view)
    bpy.utils.unregister_class(TEXT_OT_export_to_pdf)

    del bpy.types.Scene.last_line
    del bpy.types.Scene.last_line_index

    bpy.utils.unregister_class(TextReplaceProperties)
    del bpy.types.Scene.text_replace


if __name__ == "__main__":
    register()
