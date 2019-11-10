bl_info = {
    "name":
    "Fountain Live Preview",
    "author": "tintwotin",
    "version": (0, 1),
    "blender": (2, 80, 0),
    "location": "Text Editor > Sidebar",
    "description": "Adds functions for live editing of fountain file with live screenplay preview",
    "warning": "",
    "wiki_url": "",
    "category": "Text Editor",
}

import bpy
import textwrap
import os
import sys
import fountain
from bpy.props import IntProperty, BoolProperty, PointerProperty, StringProperty
from pathlib import Path


class FOUNTAIN_PT_panel(bpy.types.Panel):
    """Preview fountain script as formatted screenplay"""
    bl_label = "Fountain"
    bl_space_type = 'TEXT_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Text"

    def draw(self, context):
        layout = self.layout

        layout.operator("scene.preview_fountain")
        layout.operator("areatype.trimview")
        repl = context.scene.text_replace
        layout.prop(repl, "enabled")


class FOUNTAIN_OT_preview_fountain(bpy.types.Operator):
    bl_idname = "scene.preview_fountain"
    bl_label = "Preview Screenplay"

    # @classmethod
    # def poll(cls, context):
        # space = bpy.context.space_data # Is not getting the right context if clicked in 2. te
        # return ((space.type == 'TEXT_EDITOR') and
                # Path(space.text.filepath).suffix == ".fountain")

    def execute(self, context):

        dir = os.path.dirname(bpy.data.filepath)
        if not dir in sys.path:
            sys.path.append(dir)

        fountain_script = bpy.context.area.spaces.active.text.as_string()

        F = fountain.Fountain(fountain_script)

        #        if 'title' in F.metadata:
        #            file_name = F.metadata['title'][0]
        #        else:
        file_name = "Fountain"
        #filename = "Preview_"+file_name[:-4]+".txt"
        filename = "Preview" + ".txt"

        if filename not in bpy.data.texts:
            bpy.data.texts.new(filename)  # New document in Text Editor
        else:
            bpy.data.texts[filename].clear()  # Clear existing text

        action_wrapper = textwrap.TextWrapper(width=60)
        dialogue_wrapper = textwrap.TextWrapper(width=37)

        for fc, f in enumerate(F.elements):
            if f.element_type == 'Scene Heading':
                bpy.data.texts[filename].write(f.element_text+chr(10))
            if f.element_type == 'Action':
                action = f.element_text
                action_list = action_wrapper.wrap(text=action)
                for element in action_list:
                    bpy.data.texts[filename].write(element+chr(10))
            if f.element_type == 'Character':
                bpy.data.texts[filename].write((f.element_text).center(60)+chr(10))
            if f.element_type == 'Parenthetical':
                bpy.data.texts[filename].write((f.element_text).center(60)+chr(10))
            if f.element_type == 'Dialogue':
                dialogue = f.element_text
                line_list = dialogue_wrapper.wrap(text=dialogue)
                for element in line_list:
                    bpy.data.texts[filename].write((" "*13+element)+chr(10))
            elif f.element_type == 'Synopsis':          # Ignored by Fountain formatting
                bpy.data.texts[filename].write(chr(10))
            elif f.element_type == 'Page Break':
                bpy.data.texts[filename].write(chr(10)+("_"*60)+chr(10)+chr(10))
            elif f.element_type == 'Boneyard':           # Ignored by Fountain formatting
                bpy.data.texts[filename].write(chr(10))
            elif f.element_type == 'Comment':            # Ignored by Fountain formatting
                bpy.data.texts[filename].write(chr(10))
            elif f.element_type == 'Section Heading':    # Ignored by Fountain formatting
                bpy.data.texts[filename].write(chr(10))
            elif f.element_type == 'Transition':
                bpy.data.texts[filename].write(f.element_text.rjust(60)+chr(10))
            elif f.element_type == 'Empty Line':
                bpy.data.texts[filename].write(chr(10))

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

class AREATYPE_OT_trim(bpy.types.Operator):
    bl_idname = "areatype.trimview"
    bl_label = "Dual View"

    # @classmethod
    # def poll(cls, context): # Is not getting the right context if clicked in 2. te
        # space = bpy.context.space_data
        # return ((space.type == 'TEXT_EDITOR') and
                # Path(space.text.filepath).suffix == ".fountain")

    original_area = None

    def execute(self, context):

        self.original_area = context.area
        original = context.copy()
        thisarea = context.area
        otherarea = None
        tgxvalue = thisarea.x + thisarea.width + 1
        thistype = context.area.type

        arealist = list(context.screen.areas)

        for area in context.screen.areas:
            if area == thisarea:
                continue
            elif area.x == tgxvalue and area.y == thisarea.y:
                otherarea = area
                break

        if otherarea:  #leave trim-mode
            #            print("this x: "+str(thisarea.x))   #min_x = left x of left window
            #            print("this y: "+str(thisarea.y))   #min_y = mouse position, starting from window bottom y
            #            print("other x: "+str(otherarea.x)) #max_x = x between left and right window
            #            print("other y: "+str(otherarea.y)) #max_y = mouse position, starting from window bottom y

            #join BROKEN!!
            #teardown(context)
            bpy.ops.screen.area_join(cursor=(otherarea.x + thisarea.width + 1, otherarea.y))#, max_x=otherarea.x, max_y=otherarea.y) #broken
            #bpy.ops.screen.area_join(min_x=thisarea.x, min_y=thisarea.y, max_x=otherarea.x, max_y=otherarea.y) #broken

            # normal settings

            #bpy.ops.screen.screen_full_area()
            #bpy.ops.screen.screen_full_area()
            # override = context.copy()
            # area = self.original_area
            # override['area'] = area
            # override['space_data'] = area.spaces.active
            #            for region in area.regions:
            #                if region.type == 'PREVIEW':
            #                    break
            #            override['region'] = region
            return {"FINISHED"}

        else:  # enter dual-mode

            areax = None

            #split
                    
            window = context.window
            region = context.region
            screen = context.screen
            main = context.area
            
            main.type = "TEXT_EDITOR"
            
            #ctrlPanel = split_area(window,screen,region,main,"TEXT_EDITOR",direction="VERTICAL",factor=0.5)            

            ctrlPanel = bpy.ops.screen.area_split(direction="VERTICAL")
#            ctrlPanel.spaces[0].text = bpy.data.texts['Preview.txt']
            #settings for preview 2.

            # fit 1. preview to window
            bpy.ops.screen.screen_full_area()
            bpy.ops.screen.screen_full_area()
            override = original
            area = self.original_area
            override['area'] = area
            override['space_data'] = area.spaces.active

            for area in context.screen.areas:
                if area not in arealist:
                    areax = area
                    break


#            for area in reversed(context.screen.areas):
#                if area.type == "TEXT_EDITOR":
#                    suffix = Path(area.space_data.text.filepath).suffix
#                    if suffix == ".fountain":
#                        area.space_data.text = bpy.data.texts['Preview.txt']
#                        break
#                else:
#                    raise RuntimeError("Nothing found")

#            bpy.context.space_data.text = bpy.data.texts['Preview.txt']

            msg = "Change text-block to Preview.txt in the new Text Editor area."
            self.report({'INFO'}, msg)

            if areax:
                areax.type = thistype
                return {"FINISHED"}

            #bpy.context.space_data.text = bpy.data.texts['Preview.txt']

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

    if scene.last_line is None or scene.last_line_index != text.current_line_index:
        scene.last_line = line
        scene.last_line_index = text.current_line_index

    if line != bpy.context.scene.last_line and len(line) > len(
            bpy.context.scene.last_line):
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


def register():
    bpy.utils.register_class(FOUNTAIN_PT_panel)
    bpy.utils.register_class(FOUNTAIN_OT_preview_fountain)
    bpy.utils.register_class(AREATYPE_OT_trim)

    bpy.types.Scene.last_line = StringProperty(default="")
    bpy.types.Scene.last_line_index = IntProperty(default=0)

    bpy.utils.register_class(TextReplaceProperties)
    bpy.types.Scene.text_replace = PointerProperty(type=TextReplaceProperties)


def unregister():
    bpy.utils.unregister_class(FOUNTAIN_PT_panel)
    bpy.utils.unregister_class(FOUNTAIN_OT_preview_fountain)
    bpy.utils.unregister_class(AREATYPE_OT_trim)

    del bpy.types.Scene.last_line
    del bpy.types.Scene.last_line_index

    bpy.utils.unregister_class(TextReplaceProperties)
    del bpy.types.Scene.text_replace


if __name__ == "__main__":
    register()
