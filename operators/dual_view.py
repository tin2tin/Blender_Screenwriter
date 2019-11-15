import bpy, os

from pathlib import Path


class TEXT_OT_dual_view(bpy.types.Operator):
    '''Toggles screenplay preview'''
    bl_idname = "text.dual_view"
    bl_label = "Preview"

    @classmethod
    def poll(cls, context):
        space = bpy.context.space_data
        filepath = bpy.context.area.spaces.active.text.filepath
        if filepath.strip() == "": return False
        return ((space.type == 'TEXT_EDITOR')
                and Path(filepath).suffix == ".fountain")

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

            # The 2.81 API doesn't have an option for automatic joining.
            bpy.ops.screen.area_join(
                'INVOKE_DEFAULT',
                cursor=(otherarea.x, otherarea.y + int(otherarea.height / 2)))

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
            ctrlPanel = bpy.ops.screen.area_split(
                direction="VERTICAL")  #, factor=0.7)

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
    current_text = os.path.basename(bpy.context.space_data.text.filepath)
    if current_text.strip() == "": return
    current_character = bpy.data.texts[current_text].current_character

    if not text:
        return

    if scene.last_line is None and scene.last_line_index != text.current_line_index:
        scene.last_line = line
        scene.last_line_index = text.current_line_index

    if scene.last_character is None:  # scene.last_character != current_character:
        scene.last_character = current_character

    if line != scene.last_line or len(line) != len(scene.last_line):
        bpy.ops.scene.preview_fountain()
    elif current_character != scene.last_character:
        bpy.ops.scene.preview_fountain()

    scene.last_line = line
    scene.last_character = current_character


def redraw(context):
    for window in context.window_manager.windows:
        for area in window.screen.areas:
            if area.type == 'TEXT_EDITOR':
                area.tag_redraw()