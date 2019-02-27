
import bpy
from .srtifunc import *

####Global values###
file_lines = []

 ######RNA PROPERTIES######

 #
class light(bpy.types.PropertyGroup):
    light = bpy.props.PointerProperty(name="Light object",
        type = bpy.types.Object,
        description = "A lamp")

class camera(bpy.types.PropertyGroup):
    camera = bpy.props.PointerProperty(name = "Camera object",
        type = bpy.types.Object,
        description = "A camera")

class value(bpy.types.PropertyGroup):
    name = bpy.props.StringProperty(update = update_value_name)
    min = bpy.props.FloatProperty(default = 0)
    max = bpy.props.FloatProperty(default = 1)
    steps = bpy.props.IntProperty(default = 2, min = 2)

class srti_props(bpy.types.PropertyGroup):
    #---Create properties(C):
        
    #main parente empty pointer
    C_C_main_parent = bpy.props.PointerProperty(name="Main Parent",
        type=bpy.types.Object,
        description = "Main parent of the group")
    
    #--Lamps(C_L)
    #path to the .lp file
    C_L_light_file_path = bpy.props.StringProperty(name="Lights file Path",
        subtype='FILE_PATH',
        default="*.lp",
        description = 'Path to the lights file.')
        
    #list of lamps
    C_L_list_lights = bpy.props.CollectionProperty(type = light)
    
    #--Cameras(C_C):
    #list of cameras
    C_C_list_cameras = bpy.props.CollectionProperty(type = camera)
    
    #--Values(C_V):
    #pointer to object affected by value changes
    C_V_main_object = bpy.props.PointerProperty(name="Main object",
        type=bpy.types.Object,
        description = "Main object to apply material")
    
    #list of values
    C_V_list_values = bpy.props.CollectionProperty(type = value)
    
    #index of active value   
    C_V_selected_value_index = bpy.props.IntProperty()

    #---Render properties(R):
    
    #--output folder path(R_FP)
    #boolean to overwrite the output folder path   
    R_FP_overwrite_folder = bpy.props.BoolProperty(name = "Overwrite export folder",
        default = False,
        description = "Overwrite export folder path")

    #output folder path in use if overwrite_folder = true
    R_FP_output_folder = bpy.props.StringProperty(name="Save file directory",
        subtype='DIR_PATH',
        description = 'Path to the lights file.')

    #--output folder name(R_FN)
    #boolean to overwrite the output folder name
    R_FN_overwrite_name = bpy.props.BoolProperty(name = "Overwrite output name",
        default = False,
        description = "Overwrite output name")

    #output name in use if overwrite_name = true
    R_FN_save_name = bpy.props.StringProperty(name="Save file name",
        default = "Image",
        description = "Export file name")
    
    #---tools properties:
    
    #--Node export(T_NE)
    #boolean to enable Tools: node export
    T_NE_enable_node_exp = bpy.props.BoolProperty(name = "Enable node export",
        default = False,
        description = "Enable node export")

    #--Subdivide Files
    #boolean to enable Tools: Subdivide files
    T_SF_enable_sub_file = bpy.props.BoolProperty(name='Enable subdivide file',
        default=False,
        description='Subdivide files from an origin folder to an output folder by materials taken from a .CSV file generated from the plugin')

    #Input CSV file
    T_SF_input_file = bpy.props.StringProperty(name='CSV input file',
        subtype='FILE_PATH',
        default='*.csv',
        description='Path to the CSV input file.')

    #origin folder
    T_SF_origin_folder = bpy.props.StringProperty(name='Origin folder',
        subtype='DIR_PATH',
        description='Path to the origin folder')

    #output folder
    T_SF_output_folder = bpy.props.StringProperty(name='output folder',
        subtype='DIR_PATH',
        description='Path to the output folder')

    #boolean to subdivide files recursevlyin folders
    T_SF_recursive = bpy.props.BoolProperty(name='Subdivide recursevly',
        default=False,
        description='Subdivide files in subdirectories of the origin path')

    #Mode to use to copy or move files
    T_SF_mode = bpy.props.EnumProperty(items=[
        ('copy', 'Copy', 'Copy', '', 0),
        ('move', 'Move', 'Move', '', 1)],
        default='copy',
        name='Subdivide method')

    #Boolean to create additional csv file for folder
    T_SF_create_csv = bpy.props.BoolProperty(name='Create additional files',
        default=False,
        description='Create additional .CSV file in folder with light directions')
    
    #additional file name 
    T_SF_additional_filename = bpy.props.StringProperty(name='Output file name.',
        default='light-directions.csv',
        description='Output file name.')

    #modified = bpy.props.BoolProperty(name = "Boolean if not animated", default = True)



def register():
    print("-"*40)
    print("registering properties")
    print(__name__)
    
    ##register properties
    bpy.utils.register_class(light)
    bpy.utils.register_class(camera)
    bpy.utils.register_class(value)
    bpy.utils.register_class(srti_props)
    bpy.types.Scene.srti_props = bpy.props.PointerProperty(type = srti_props)
