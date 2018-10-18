##############
#####GUI######
##############

import bpy
import numpy
from ..srtifunc import *
from ..srtiproperties import file_lines as file_lines

class Values_UL_items(bpy.types.UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row()
        row.alignment = 'LEFT'
        #row.label("Id: %d" % (index))
        row.prop(item, "name", text="", emboss=False, translate=False)
        row2 = row.row(align = True)
        row2.prop(item,"min")
        row2.prop(item,"max")
        row2.prop(item,"steps")

    def invoke(self, context, event):
        pass   

###Create
class SyntheticRTIPanelCreate(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "Create"
    bl_idname = "srti.panelCreate"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "SyntheticRTI"

    def draw(self, context):
        curr_scene = context.scene

        layout = self.layout
        layout.prop(curr_scene.srti_props, "light_file_path", text = 'light file')
        row = layout.row(align = True)
        row.operator("srti.create_lamps", icon ="OUTLINER_DATA_LAMP")
        #row.operator("srti.delete_active_lamp", icon = "X")
        row.operator("srti.delete_lamps", icon = "X")
        row = layout.row(align = True)
        row.operator("srti.create_cameras",icon = "OUTLINER_DATA_CAMERA")
        #row.operator("srti.delete_active_camera", icon = "X")
        row.operator("srti.delete_cameras", icon = "X")

        layout.prop(curr_scene.srti_props, "main_object", text = "Object")
        layout.label("Parameters:", icon='ACTION')
        row = layout.row()
        row.template_list("Values_UL_items", "", curr_scene.srti_props, "list_values", curr_scene.srti_props, "selected_value_index", rows=3)

        col = row.column(align=True)
        col.operator("srti.values_uilist", icon='ZOOMIN', text="").action = 'ADD'
        col.operator("srti.values_uilist", icon='ZOOMOUT', text="").action = 'REMOVE'
        col.separator()
        col.operator("srti.values_uilist", icon='TRIA_UP', text="").action = 'UP'
        col.operator("srti.values_uilist", icon='TRIA_DOWN', text="").action = 'DOWN'

###Render
class SyntheticRTIPanelRender(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "Render"
    bl_idname = "srti.panelRender"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "SyntheticRTI"

    def draw(self, context):
        curr_scene = context.scene
        layout = self.layout
        layout.prop(curr_scene.srti_props, "output_folder", text = 'Output folder')
        layout.prop(curr_scene.srti_props, "save_name", text = 'Output name')
        col = layout.column(align = True)
        col.operator("srti.animate_all", icon ="KEYINGSET")
        col.operator("srti.render_images", icon = "RENDER_ANIMATION")
        col.operator("srti.create_file", icon = "FILE_TEXT")

###Tools
class SyntheticRTIPanelTools(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "Tools"
    bl_idname = "srti.panelTools"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "SyntheticRTI"

    def draw(self, context):
        curr_scene = context.scene
        layout = self.layout
        layout.operator("srti.export_lamp", icon = "FILE_TEXT")
        col = layout.column(align = True)
        col.operator("srti.create_export_node", icon = "NODETREE")
        row = col.row(align = True)
        row.operator("srti.render_normals", icon = 'MOD_NORMALEDIT')
        row.operator("srti.render_composite", icon = 'GROUP_VCOL')
        col.operator("srti.reset_nodes", icon = "X")


###Debug
class SyntheticRTIPanelDebug(bpy.types.Panel):
    """Creates a Panel in the Object properties window,"""
    bl_label = "Debug"
    bl_idname = "srti.panelDebug"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "SyntheticRTI"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        curr_scene = context.scene
        layout = self.layout
        num_light = max(len(curr_scene.srti_props.list_lights),1)
        num_cam = len(curr_scene.srti_props.list_cameras)
        num_values = len(curr_scene.srti_props.list_values)
        tot_comb = numpy.prod(list(row.steps for row in curr_scene.srti_props.list_values))

        if curr_scene.srti_props.main_parent:
            main = curr_scene.srti_props.main_parent.name
        else:
            main = "None"

        box = layout.box()
        box.label("Main = %s" % main)
        box.label("Lamps = %i" % num_light)
        box.label("Cameras = %i" % num_cam)
        box.label("Values = %i" % num_values)
        box.label("Combination = %i" % tot_comb)
        box.label("Total frames = %i" % (num_light * num_cam *tot_comb))
        box.label("Total file lines = %i" %len(file_lines))

        