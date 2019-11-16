import bpy, os

from bpy.props import BoolProperty
from pathlib import Path

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

    @classmethod
    def poll(cls, context):
        space = bpy.context.space_data
        filepath = bpy.context.area.spaces.active.text.filepath
        if filepath.strip() == "": return False
        return ((space.type == 'TEXT_EDITOR')
                and Path(filepath).suffix == ".fountain")

    def execute(self, context):
        return {"FINISHED"}