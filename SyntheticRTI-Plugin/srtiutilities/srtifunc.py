
import bpy
import numpy

###Various function###
def create_main(scene):
    """Create the main object if not already present"""
    #Add Empty to parent all lights 
    if not scene.srti_props.main_parent:
        main_parent = bpy.data.objects.new(name = "main_parent", object_data = None)
        scene.objects.link(main_parent)
        main_parent.empty_draw_type = 'SPHERE'
        scene.srti_props.main_parent = main_parent
        print("--- Create Main: %s."%main_parent.name)

def delete_main(scene):
    """Delete main parent""" 
    if scene.srti_props.main_parent:
        bpy.ops.object.select_all(action='DESELECT')
        scene.srti_props.main_parent.select = True #delete the main parent (need revision)
        scene.srti_props.main_parent = None
        bpy.ops.object.delete()
        file_lines = []
        print("--- Delete Main.")

def check_lamp_cam(scene):
    """Return true if there are lamps or cameras in the scene and, if there is none, it delete the main parent"""
    if (not scene.srti_props.list_cameras) and (not scene.srti_props.list_lights): #delete the main object if no cameras and lights
        print("--There are no camera and no lights.")
        delete_main(scene)
        return False
    return True

def format_index(num, tot):
    tot_dig = len(str(tot))
    return "{0:0{dig}d}".format(num, dig = tot_dig)

def calculate_tot_frame(context):
    """Return the numbers of total frames"""
    curr_scene = context.scene
    num_light = max(len(curr_scene.srti_props.list_lights),1)
    num_cam = len(curr_scene.srti_props.list_cameras)
    num_values = len(curr_scene.srti_props.list_values)
    tot_comb = numpy.prod(list(row.steps for row in curr_scene.srti_props.list_values))
    return int(num_light * num_cam * max(tot_comb,1))

#TODO implement
def get_unice_value_name(name, list):
    """Give a unique name in a list""" 
    return name

def set_render_exr(scene):
    """Prepare the render setting""" 
    #set cycles as renderer  
    scene.render.engine = 'CYCLES'

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
    curr_rend_layer = scene.render.layers.active
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
  
