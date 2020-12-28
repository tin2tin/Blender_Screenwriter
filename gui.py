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
        row = layout.row(align=True)
        row.operator("screenwriter.dual_view")
        row.operator("scene.preview_fountain", text="", icon="FILE_REFRESH")
        
        repl = context.scene.text_replace
        layout.prop(repl, "enabled")

        layout.operator("screenwriter.insert_title_page")
        # layout.operator("screenwriter.insert_scene_numbers") #unfinished implementation


class SCREENWRITER_PT_sequencer_panel(bpy.types.Panel):
    """Screenwriter Sequencer Options"""
    bl_label = "Sequencer"
    bl_parent_id = "SCREENWRITER_PT_panel"
    bl_options = {'DEFAULT_CLOSED'}
    bl_space_type = 'TEXT_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Screenwriter"

    def draw(self, context):
        layout = self.layout
        scn = context.scene
        props = scn.keywords_assigner
        layout = layout.column(align=False)

        row = layout.row(align=False)
        row.prop(props, "new_keyword", text="Word")
        row.operator("ops.rename_keyword", icon="COPY_ID", text="")
        row.operator("ops.add_keyword", icon="ADD", text="")

        row = layout.row()
        row.template_list("OBJECT_UL_screenwriter_keywords", "", props, "keywords", props, "keyword_index", rows=5)

        col = row.column()
        col.operator("ops.sw_remove_keyword", text="", icon="REMOVE")
        col.operator("ops.sw_move_keyword_up", text="", icon="TRIA_UP")
        col.operator("ops.sw_move_keyword_down", text="", icon="TRIA_DOWN")

        if 0 <= props.keyword_index < len(props.keywords):
            #layout.label(text="Objects")
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

        layout.operator("screenwriter.fountain_to_strips")
        #layout.operator("screenwriter.strips_to_markers")
        #layout.operator("screenwriter.clear_markers")
        #layout.prop(context.scene, 'screenwriter_channel')
        layout.separator()
        layout.operator("text.switch_to_scene")

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
