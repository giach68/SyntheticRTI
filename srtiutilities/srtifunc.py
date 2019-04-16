
import bpy
import numpy
import os

###Various function###
def get_srti_collection(scene):
    """Get SRTI main collection, it create a new one if it does not exist yet."""
    if 'SRTI' in bpy.data.collections: # check if exist
        return bpy.data.collections['SRTI']
    else:
        new_collection = bpy.data.collections.new('SRTI') #create new collection
        scene.collection.children.link(new_collection) # Add the new collection to scene
        return new_collection

def get_camera_collection(scene):
    """Get camera collection, it create a new one if it does not exist yet."""
    if 'SRTI_cameras' in bpy.data.collections: # check if exist
        return bpy.data.collections['SRTI_cameras']
    else:
        new_collection = bpy.data.collections.new('SRTI_cameras') #create new collection
        srti_collection = get_srti_collection(scene) #get SRTI collection
        srti_collection.children.link(new_collection) # Add the new collection to SRTI collection
        return new_collection

def get_lights_collection(scene):
    """Get lights collection, it create a new one if it does not exist yet."""
    if 'SRTI_lights' in bpy.data.collections: # check if exist
        return bpy.data.collections['SRTI_lights']
    else:
        new_collection = bpy.data.collections.new('SRTI_lights') #create new collection
        srti_collection = get_srti_collection(scene) #get SRTI collection
        srti_collection.children.link(new_collection) # Add the new collection to SRTI collection
        return new_collection

def get_main(scene):
    """Get main object, it create a new one if it does not exist yet."""
    #Add Empty to parent all lights
    if not scene.srti_props.C_C_main_parent: #check if exist
        main_parent = bpy.data.objects.new(name = "main_parent", object_data = None) #create datablock
        srti_collection = get_srti_collection(scene) #get SRTI collection
        srti_collection.objects.link(main_parent) #link main to collection
        main_parent.empty_display_type = 'SPHERE' #set empty appearance
        scene.srti_props.C_C_main_parent = main_parent #link object to properties
        print("--- Create Main: %s."%main_parent.name)    
    return scene.srti_props.C_C_main_parent

def delete_main(scene):
    """Delete main parent""" 
    if scene.srti_props.C_C_main_parent: #check if exist
        print("Main found")
        bpy.ops.object.select_all(action='DESELECT') #deselect all
        scene.srti_props.C_C_main_parent.select_set(True) #select the main parent
        scene.srti_props.C_C_main_parent = None #unlink object from properties
        bpy.ops.object.delete() #delete
        file_lines = [] #clear file lines
        bpy.data.collections.remove(bpy.data.collections['SRTI']) #remove SRTI collection
        print("--- Delete Main.")

def check_lamp_cam(scene):
    """Return true if there are lamps or cameras in the scene and, if there is none, it delete the main parent"""
    if (not scene.srti_props.C_C_list_cameras) and (not scene.srti_props.C_L_list_lights): #delete the main object if no cameras and lights
        print("--There are no camera and no lights.")
        delete_main(scene)
        return False
    return True

def format_index(num, tot):
    tot_dig = len(str(tot))
    return num_to_fixed_len_str(num, tot_dig)

def num_to_fixed_len_str(num, len):
    return "{0:0{dig}d}".format(num, dig = len)

def calculate_tot_frame(context):
    """Return the numbers of total frames"""
    curr_scene = context.scene
    num_light = max(len(curr_scene.srti_props.C_L_list_lights),1)
    num_cam = len(curr_scene.srti_props.C_C_list_cameras)
    num_values = len(curr_scene.srti_props.C_V_list_values)
    tot_comb = numpy.prod(list(row.steps for row in curr_scene.srti_props.C_V_list_values))
    return int(num_light * num_cam * max(tot_comb,1))

def update_value_name(self, context):
    """Check all value names and add numbers if there are equal names"""
    #could be better but work for small numbers of values
    value_list = context.scene.srti_props.C_V_list_values
    
    #External loop is implicit because when the name change a new check is triggered so we have a "free" recursive system 
    for i,elem in enumerate(value_list[1:]): #index from enumeration of values starting from the second element
        for old_elem in value_list[0:i+1]: #add 1 to index becouse i start from 0 not 1 after taking away the first element
            if old_elem.name == elem.name:
                if old_elem.name[-3:].isdigit(): #if there is already a number we increase it
                    index = int(elem.name[-3:]) + 1
                    elem.name = elem.name[0:-4]+".{0:03}".format(index) #trigger the new update_value_name function
                else: #we add .001 at the end of the name
                    elem.name +=".001" #trigger the new update_value_name function
        
def set_render_exr(context):
    """Prepare the render setting""" 
    scene = context.scene

    #set cycles as renderer  
    scene.render.engine = scene.srti_props.R_O_engine

    #set output format
    scene.render.image_settings.file_format = 'OPEN_EXR_MULTILAYER'
    scene.render.image_settings.color_mode = 'RGBA'
    scene.render.image_settings.color_depth = '32'
    scene.render.image_settings.exr_codec = 'ZIP'

    #disable compositor
    scene.render.use_compositing = True
    scene.use_nodes = False

    #set color management to linear
    scene.display_settings.display_device = 'None'
        
    #set rendering to not overwrrite
    scene.render.use_overwrite = False

    #set render passes
    curr_rend_layer = context.view_layer
    curr_rend_layer.use_pass_combined = True
    curr_rend_layer.use_pass_z = True
    curr_rend_layer.use_pass_normal = True
    curr_rend_layer.use_pass_shadow = True
    curr_rend_layer.use_pass_diffuse_direct = True
    curr_rend_layer.use_pass_diffuse_indirect = True
    curr_rend_layer.use_pass_diffuse_color = True
    curr_rend_layer.use_pass_glossy_direct = True
    curr_rend_layer.use_pass_glossy_indirect = True
    curr_rend_layer.use_pass_glossy_color = True


    #view_layers["View Layer"].use_pass_combined
  
def get_export_folder_path(context):
    """Get export folder path. Return empty string if the file is not saved and/or there is no overwrite name"""
    save_dir = os.path.dirname(context.blend_data.filepath)
    if context.scene.srti_props.R_FP_overwrite_folder:
        save_dir = context.scene.srti_props.R_FP_output_folder
    return save_dir

def get_export_name(context):
    """Get export name. Return empty string if the file is not saved and/or there is no overwrite name"""
    file_name = bpy.path.display_name(context.blend_data.filepath)
    if context.scene.srti_props.R_FN_overwrite_name:
        file_name = context.scene.srti_props.R_FN_save_name
    return file_name

