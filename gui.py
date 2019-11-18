import bpy

class SCREENWRITER_PT_panel(bpy.types.Panel):
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
        layout.operator("text.scenes_to_strips")

def screenwriter_menu_export(self, context):
    self.layout.separator()
    self.layout.operator("export.screenplay", text="Export Screenplay")