import bpy

from pathlib import Path

from ..debug_value import debug ### DEBUG
from ..functions.area_functions import findTextEditor
from ..functions.fountain_functions import returnFountainPreviewText
from ..global_variables import emptyTextBlock, previewCreated, previewExists


class SCREENWRITER_OT_dual_view(bpy.types.Operator):
    '''Toggles screenplay preview'''
    bl_idname = "screenwriter.dual_view"
    bl_label = "Preview"
    bl_options = {'INTERNAL'}

    original_area = None

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
        if debug: print('debug --- start execution') ### DEBUG
        bpy.ops.scene.preview_fountain()
        self.original_area = context.area
        original = context.copy()

        if debug: print('debug --- getting preview text block') ### DEBUG
        previewBlock = returnFountainPreviewText(context)
        if debug: print('debug --- '+str(previewBlock)) ### DEBUG
        if previewBlock == "":
            self.report({'INFO'}, emptyTextBlock)
            return {"FINISHED"}

        for area in findTextEditor(context):
            if debug: print('debug --- iterating through text areas') ### DEBUG
            if area.spaces.active.text == previewBlock:
                self.report({'INFO'}, previewExists)
    
                # flip sidebar
                context = bpy.context
                c = {}  # override dictionary
                window = context.window
                c["window"] = window
                for screen in bpy.data.screens:
                    c["screen"] = screen
                    for area in screen.areas:
                        c["area"] = area
                        if area.type == "TEXT_EDITOR":
                            for region in area.regions:
                                if region.type == 'UI':# and not (region.x - area.x):
                                    c["region"] = region
                                    bpy.ops.screen.region_flip(c) 
                return {"FINISHED"}
        
        if debug: print('debug --- splitting context area and starting dual mode') ### DEBUG

        # flip sidebar
        context = bpy.context
        c = {}  # override dictionary
        window = context.window
        c["window"] = window
        for screen in bpy.data.screens:
            c["screen"] = screen
            for area in screen.areas:
                c["area"] = area
                if area.type == "TEXT_EDITOR":
                    for region in area.regions:
                        if region.type == 'UI':# and not (region.x - area.x):
                            c["region"] = region
                            bpy.ops.screen.region_flip(c)

        #split
        bpy.ops.screen.area_split(direction="VERTICAL")
       
        #settings for preview 2.
        area = self.original_area
        override = original
        override['area'] = area
        override['space_data'] = area.spaces.active
        override['space_data'].text = previewBlock
        override['space_data'].show_region_ui = False
        override['space_data'].show_region_header = False
        override['space_data'].show_region_footer = False
        override['space_data'].show_line_numbers = False
        override['space_data'].show_syntax_highlight = False
        override['space_data'].show_word_wrap = False
        override['space_data'].show_margin = True
        override['space_data'].margin_column = 74

        self.report({'INFO'}, previewCreated)

        return {"FINISHED"}
