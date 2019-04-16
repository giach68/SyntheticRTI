##############
#####GUI######
##############

import bpy
import numpy
import os
from .srtifunc import *
from .srtiproperties import file_lines as file_lines

# class SyntheticRTIcontext(bpy.types.Panel):
#     bl_label = "SRTI_context"
#     bl_idname = "srti.SRTI_context"
#     bl_space_type = "PROPERTIES"
#     bl_region_type = "WINDOW"


##list of properties
class SRTI_UL_values_items(bpy.types.UIList):
    
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        # box = layout.box()
        # row = box.row(align = True)
        # row.alignment = 'LEFT'
        col1 = layout.column()
        col1.prop(item, "name", text="", emboss=False, translate=False, icon='PROPERTIES')
        row2 = col1.row(align = True)
        row2.prop(item,"min")
        row2.prop(item,"max")
        row2.prop(item,"steps")
        col1.separator()

    def invoke(self, context, event):
        pass   

###Create
class SRTI_PT_panel_create(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "Create"
    bl_idname = "SRTI_PT_panel_create"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "SyntheticRTI"
    def draw(self, context):
        curr_scene = context.scene
        props = curr_scene.srti_props
        layout = self.layout
        
        #light
        layout.prop(props, "C_L_light_file_path", text = 'Light file (.lp)', icon = "LIGHT_SPOT")
        row = layout.row(align = True)
        row.operator("srti.create_lamps", icon ="OUTLINER_DATA_LIGHT")
        row.operator("srti.delete_lamps", icon = "X")
        
        #camera
        row = layout.row(align = True)
        row.operator("srti.create_cameras",icon = "OUTLINER_DATA_CAMERA")
        row.operator("srti.delete_cameras", icon = "X")
        
        #object
        layout.prop(curr_scene.srti_props, "C_V_main_object", text = "Object")
        
        #Parameters
        layout.label(text = "Parameters:", icon='ACTION')
        row = layout.row()
        row.template_list("SRTI_UL_values_items", "", props, "C_V_list_values", props, "C_V_selected_value_index", rows=2)
        col = row.column(align=True)
        col.operator("srti.values_uilist", icon='ADD', text="").action = 'ADD'
        col.operator("srti.values_uilist", icon='REMOVE', text="").action = 'REMOVE'
        col.separator()
        col.operator("srti.values_uilist", icon='TRIA_UP', text="").action = 'UP'
        col.operator("srti.values_uilist", icon='TRIA_DOWN', text="").action = 'DOWN'

##Render
class SRTI_PT_panel_render(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "Render"
    bl_idname = "SRTI_PT_panel_render"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "SyntheticRTI"

    def draw(self, context):
        curr_scene = context.scene
        props = curr_scene.srti_props
        layout = self.layout
        
        #output folder
        box = layout.box()
        if props.R_FP_overwrite_folder: #if we want to overwrite
            box.label(text = "Output folder = "+props.R_FP_output_folder, icon = "FILE_FOLDER")          
            box.prop(props, "R_FP_overwrite_folder")
            box.prop(props, "R_FP_output_folder", text = 'Output folder')
        else: #standard output taken from the saved blender file
            if context.blend_data.is_saved: # if the file is saved
                box.label(text = "Output folder = "+os.path.dirname(context.blend_data.filepath), icon = "FILE_FOLDER")
            else:
                box.label(text = "Output folder = *Must save the file*", icon = "ERROR")
                
            box.prop(props, "R_FP_overwrite_folder")

            
        #output name    
        box = layout.box()
        if curr_scene.srti_props.R_FN_overwrite_name: #if we want to overwrite
            box.label(text = "Output name = "+curr_scene.srti_props.R_FN_save_name, icon = "SORTALPHA")
            box.prop(curr_scene.srti_props, "R_FN_overwrite_name")
            box.prop(curr_scene.srti_props, "R_FN_save_name", text = 'Output name')
        else: #standard name taken from the saved blender file
            if context.blend_data.is_saved: # if the file is saved
                box.label(text = "Output name = "+bpy.path.display_name(context.blend_data.filepath), icon = "SORTALPHA")
            else:
                box.label(text = "Output name = *Must save the file*", icon = "ERROR")
                
            box.prop(curr_scene.srti_props, "R_FN_overwrite_name")
        layout.prop(props, 'R_O_engine', text='Engine', expand=False)
        col = layout.column(align = True)
        col.operator("srti.animate_feature", icon ="KEYINGSET")
        col.operator("srti.create_csv_file", icon = "FILE_TEXT")
        col.operator("srti.set_render_settings", icon = "PREFERENCES")
        col.operator("render.render", text="Render Images", icon='RENDER_ANIMATION').animation = True

###Tools
class SRTI_PT_tools(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "Tools"
    bl_idname = "SRTI_PT_tools"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "SyntheticRTI"

    def draw(self, context):
        curr_scene = context.scene
        props = curr_scene.srti_props
        layout = self.layout
        
        #Export lamp
        layout.operator("srti.export_as_lamp", icon = "FILE_TEXT")
        
class SRTI_PT_tools_nodes(bpy.types.Panel):
    """Subpanel of tools: Export nodes from .exr"""
    bl_label = "Export Nodes from .exr"
    bl_idname = "SRTI_PT_tools_nodes"
    bl_parent_id = "SRTI_PT_tools"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "SyntheticRTI"

    def draw(self, context):
        curr_scene = context.scene
        props = curr_scene.srti_props
        layout = self.layout
        #Export nodes
        # box_node_exp = layout.box()
        # box_node_exp.prop(props, "T_NE_enable_node_exp", text = "Export Nodes from .exr", icon = "TRIA_DOWN" if props.T_NE_enable_node_exp else "TRIA_RIGHT", emboss = False)
        # if props.T_NE_enable_node_exp:
        col = layout.column(align = True)
        col.operator("srti.create_export_node", icon = "NODETREE")
        row = col.row(align = True)
        row.operator("srti.export_normals", icon = 'MOD_NORMALEDIT')
        row.operator("srti.export_composite", icon = 'GROUP_VCOL')
        col.operator("srti.delete_nodes", icon = "X")

class SRTI_PT_tools_subdivide(bpy.types.Panel):
    """Subpanel of tools: Export nodes from .exr"""
    bl_label = "Subdivide rendered sets"
    bl_idname = "SRTI_PT_tools_subdivide"
    bl_parent_id = "SRTI_PT_tools"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "SyntheticRTI"

    def draw(self, context):
        curr_scene = context.scene
        props = curr_scene.srti_props
        layout = self.layout
        #subdivide files
        # box_sub_file = layout.box()
        # box_sub_file.prop(props, 'T_SF_enable_sub_file', text='Subdivide rendered sets', icon='TRIA_DOWN' if props.T_SF_enable_sub_file else 'TRIA_RIGHT', emboss=False)
        # if props.T_SF_enable_sub_file:
        col = layout.column()
        col.prop(props, 'T_SF_input_file', text='CSV File', icon='FILE_TEXT')
        col.prop(props, 'T_SF_origin_folder', text='Origin folder', icon='COPYDOWN')
        col.prop(props, 'T_SF_output_folder', text='Output folder', icon='PASTEDOWN')
        col2 = col.column()
        col2.prop(props, 'T_SF_recursive')
        col2.prop(props, 'T_SF_create_csv')
        if props.T_SF_create_csv: 
            col2.prop(props, 'T_SF_additional_filename')
        row = col.row()
        row.label(text = 'Mode:')
        row.prop(props, 'T_SF_mode', text='Mode:', expand=True)

        layout.operator('srti.subdivide_sets', icon='IMGDISPLAY')

###Debug
class SRTI_PT_panel_debug(bpy.types.Panel):
    """Creates a Panel in the Object properties window,"""
    bl_label = "Debug"
    bl_idname = "SRTI_PT_panel_debug"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "SyntheticRTI"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        curr_scene = context.scene
        layout = self.layout
        num_light = max(len(curr_scene.srti_props.C_L_list_lights),1)
        num_cam = len(curr_scene.srti_props.C_C_list_cameras)
        num_values = len(curr_scene.srti_props.C_V_list_values)
        tot_comb = numpy.prod(list(row.steps for row in curr_scene.srti_props.C_V_list_values))

        if curr_scene.srti_props.C_C_main_parent:
            main = curr_scene.srti_props.C_C_main_parent.name
        else:
            main = "None"

        box = layout.box()
        box.label(text = "Main = %s" % main)
        box.label(text = "Lamps = %i" % num_light)
        box.label(text = "Cameras = %i" % num_cam)
        box.label(text = "Values = %i" % num_values)
        box.label(text = "Combination = %i" % tot_comb)
        box.label(text = "Total frames = %i" % (num_light * num_cam *tot_comb))
        box.label(text = "Total file lines = %i" %len(file_lines))


classes = (SRTI_UL_values_items, SRTI_PT_panel_create, SRTI_PT_panel_render, SRTI_PT_tools, SRTI_PT_tools_nodes, SRTI_PT_tools_subdivide, SRTI_PT_panel_debug)
register, unregister = bpy.utils.register_classes_factory(classes)        