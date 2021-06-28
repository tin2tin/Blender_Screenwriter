import bpy

from bpy.types import Panel, PropertyGroup, UIList, Operator, OperatorFileListElement
#from bpy.props import StringProperty, CollectionProperty, IntProperty, PointerProperty, BoolProperty
#from pathlib import Path
#import bpy
#from bpy_extras.io_utils import ImportHelper
#from os import path

class SCREENWRITER_PT_panel(bpy.types.Panel):
    """Preview fountain script as formatted screenplay"""
    bl_label = "Screenwriter"
    bl_space_type = 'TEXT_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Screenwriter"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False


class SCREENWRITER_PT_preview_panel(bpy.types.Panel):
    """Screenwriter Setup Options"""
    bl_label = "Preview"
    bl_parent_id = "SCREENWRITER_PT_panel"
    #bl_options = {'DEFAULT_CLOSED'}
    bl_space_type = 'TEXT_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Screenwriter"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        column = layout.column(heading="Split", align=True)
        split = column.split(factor=0.4, align=True) 
        split.alignment = 'RIGHT'
        split.label(text="Add")
        split.operator("screenwriter.dual_view", text="Dual View")

        column = layout.column(heading="Refresh", align=True) 
        repl = context.scene.text_replace
        column.prop(repl, "enabled", text="Auto", toggle=True)
        split = column.split(factor=0.4, align=False) 
        split.alignment = 'RIGHT'
        split.label(text="")
        split.operator("scene.preview_fountain", text="Manual")
        split.active = not repl.enabled

        prefs = context.preferences
        view = prefs.view
        layout.prop(view, "font_path_ui_mono", text="Font")


class SCREENWRITER_PT_layout_panel(bpy.types.Panel):
    """Screenwriter Layout Options"""
    bl_label = "Layout"
    bl_parent_id = "SCREENWRITER_PT_panel"
    #bl_options = {'DEFAULT_CLOSED'}
    bl_space_type = 'TEXT_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Screenwriter"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        column = layout.column(align=True) 
        split = column.split(factor=0.4, align=False) 
        split.alignment = 'RIGHT'
        split.label(text="Insert")
        split.operator("screenwriter.insert_title_page", text="Title Page")

        split = column.split(factor=0.4, align=False) 
        split.alignment = 'RIGHT'
        split.label(text="")
        split.operator("screenwriter.insert_scene_numbers", text="Scene Numbers")

        split = column.split(factor=0.4, align=False) 
        split.alignment = 'RIGHT'
        split.label(text="")
        split.operator("screenwriter.insert_shot", text="Shot")

        column = layout.column(align=True)
        split = column.split(factor=0.4, align=False) 
        split.alignment = 'RIGHT'
        split.label(text="Correct")
        split.operator("screenwriter.correct_caps", text="Caps")


class SCREENWRITER_PT_screenplayer_panel(bpy.types.Panel):
    """Screenwriter Screenplayer Options"""
    bl_label = "Screenplayer"
    bl_parent_id = "SCREENWRITER_PT_panel"
    #bl_options = {'DEFAULT_CLOSED'}
    bl_space_type = 'TEXT_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Screenwriter"

    def draw(self, context):
        layout = self.layout
        scn = context.scene
        props = scn.keywords_assigner
        layout = layout.column(align=False)
        layout.label(text="Keywords from Screenplay:")
        row = layout.row(align=False)
        row.prop(props, "new_keyword", text="")
        row.operator("ops.get_keyword", text="", icon="EYEDROPPER")

        row = layout.row()
        row.template_list("OBJECT_UL_screenwriter_keywords", "", props, "keywords", props, "keyword_index", rows=5)

        col = row.column()
        col.operator("ops.add_keyword", text="", icon="ADD")
        col.operator("ops.sw_remove_keyword", text="", icon="REMOVE")
        col.operator("ops.sw_move_keyword_up", text="", icon="TRIA_UP")
        col.operator("ops.sw_move_keyword_down", text="", icon="TRIA_DOWN")

        col.operator("ops.rename_keyword", text="", icon="COPY_ID")

        if 0 <= props.keyword_index < len(props.keywords):
            layout.label(text="Assigned 3D Objects:")
            keyword = props.keywords[props.keyword_index]

            row = layout.row()
            row.template_list("OBJECT_UL_screenwriter_objects", "", keyword, "objects", keyword, "object_index",
                              rows=7)

            col = row.column()
            col.operator("ops.sw_add_objects", text="", icon="ADD")
            col.operator("ops.sw_remove_file", text="", icon="REMOVE")
            col.operator("ops.sw_move_file_up", text="", icon="TRIA_UP")
            col.operator("ops.sw_move_file_down", text="", icon="TRIA_DOWN")

#            layout.separator()

#            col = layout.row(align=True)
#            col.operator("ops.sw_load_reload_objects", icon="FILE_REFRESH")
#            col.operator("ops.sw_remove_keyword_objects", icon="REMOVE")
#            col = layout.row(align=True)
#            col.operator("ops.sw_save_keyword_objects", icon="WINDOW")
#            col.operator("ops.sw_run_objects", icon="PLAY")
            
        #layout.operator("text.scenes_to_strips")
        layout_big = layout.column(align=False)
        layout_big.separator()
        layout_big.scale_y = 1.3
        layout_big.operator("screenwriter.fountain_to_strips", text="Generate Movie")
        #layout.operator("screenwriter.strips_to_markers")
        #layout.operator("screenwriter.clear_markers")
        #layout.prop(context.scene, 'screenwriter_channel')


class SCREENWRITER_PT_navigation_panel(bpy.types.Panel):
    """Screenwriter Navigation Options"""
    bl_label = "Navigation"
    bl_parent_id = "SCREENWRITER_PT_screenplayer_panel"
    #bl_options = {'DEFAULT_CLOSED'}
    bl_space_type = 'TEXT_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Screenwriter"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        column = layout.column(heading="Switch to", align=True) 
        split = column.split(factor=0.4, align=False) 
        split.alignment = 'RIGHT'
        split.label(text="Switch to")
        split.operator("text.switch_to_scene", text="Screenplay Scene")
        split = column.split(factor=0.4, align=False) 
        split.alignment = 'RIGHT'
        split.label(text="")
        split.operator("text.switch_to_master", text="Master Scene")


# ---------------------------------------------------------------------------------------------
# UI LISTS
# ---------------------------------------------------------------------------------------------
class OBJECT_UL_screenwriter_keywords(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row(align=True)

        row.label(text=item.name)
        row.label(text="{} Object(s)".format(len(item.objects)))


class OBJECT_UL_screenwriter_objects(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row(align=True)

        row.label(text=item.objectname)
        row.label(text=item.objecttype.title())
        # row.prop(item, "runnable", text="Visible")


def screenwriter_menu_export(self, context):
    self.layout.separator()
    self.layout.operator("export.screenplay", text="Export Screenplay")
