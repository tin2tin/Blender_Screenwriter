import bpy

from ..global_variables import previewFileName

def returnFountainPreviewText(context):
    previewBlock = bpy.data.texts[previewFileName]
    if previewFileName not in bpy.data.texts:
        bpy.ops.scene.preview_fountain()
        fountain_script = bpy.context.area.spaces.active.text.as_string()
        if fountain_script.strip() == "":
            previewBlock = ""
    return previewBlock