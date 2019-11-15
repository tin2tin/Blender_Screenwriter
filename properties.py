import bpy

from bpy.props import BoolProperty
from pathlib import Path


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