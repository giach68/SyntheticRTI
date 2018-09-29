bl_info = {
    "name": "SyntheticRTI",
    "author": "Andrea Dall'Alba",
    "version": (0, 2, 2),
    "blender": (2, 79, 0),
    "location": "View3D > Tools > SyntheticRTI",
    "description": "Plugin to help creating the synthetic database for RTI",
    "category": "3D View",
}

import bpy
from mathutils import Vector
import numpy
import itertools
import os
import re
from bpy_extras.io_utils import ExportHelper, ImportHelper

####Global values###
file_lines = []

###Various function###
def create_main(scene):
    """Create the main object if not already present"""
    #Add Empty to parent all lights 
 
    if not scene.srti_props.main_parent:
        main_parent = bpy.data.objects.new(name = "main_parent", object_data = None)
        scene.objects.link(main_parent)
        main_parent.empty_draw_type = 'SPHERE'
        scene.srti_props.main_parent = main_parent

def delete_main(scene):
    """Delete main parent""" 
    if scene.srti_props.main_parent:
        bpy.ops.object.select_all(action='DESELECT')
        scene.srti_props.main_parent.select = True #delete the main parent (need revision)
        scene.srti_props.main_parent = None
        bpy.ops.object.delete()
        file_lines = []
        print(file_lines)


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
  
###OPERATORS###
#########LAMP#########
class create_lamps(bpy.types.Operator):
    """Create lamps from file"""
    bl_idname = "srti.create_lamps"
    bl_label = "Create Lamps"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        bpy.ops.srti.delete_lamps() #delete exsisting lamps

        curr_scene = context.scene
        file_path = curr_scene.srti_props.light_file_path

        if not os.path.isfile(file_path) or os.path.splitext(file_path)[1] != ".lp":
            self.report({'ERROR'}, 'No valid file selected on '+file_path)
            return {'CANCELLED'}

        #create the main parent
        create_main(curr_scene)
        main_parent = curr_scene.srti_props.main_parent

        file = open(file_path)
        rows = file.readlines() #copy all lines in memory
        file.close()
        
        n_lights = int(rows[0].split()[0])#in the first row there is the total count of lights
        print(n_lights)
        
        ##Use standars light, TODO add a differente object
        lamp_data = bpy.data.lamps.new(name="Project_light", type='SUN') # Create new lamp datablock.  It s going to be created outside
        
        for lamp in range(1, n_lights + 1): #step trought all lamps
            valori_riga = rows[lamp].split() #split values
            lmp_x = float(valori_riga[1])
            lmp_y = float(valori_riga[2])
            lmp_z = float(valori_riga[3])
            direction = Vector((lmp_x, lmp_y, lmp_z))

            print(lamp , 'x=', lmp_x, 'y=', lmp_y, 'z=', lmp_z) #print all values
            lamp_object = bpy.data.objects.new(name="Lamp_{0}".format(format_index(lamp, n_lights)), object_data=lamp_data) # Create new object with our lamp datablock
            curr_scene.objects.link(lamp_object) # Link lamp object to the scene so it'll appear in this scene
            lamp_object.parent = main_parent
            lamp_object.location = (lmp_x, lmp_y, lmp_z) # Place lamp to a specified location
            
            lamp_object.rotation_mode = 'QUATERNION'
            lamp_object.rotation_quaternion = direction.to_track_quat('Z','Y')
            
            ##change the name
            lamp = curr_scene.srti_props.list_lights.add()
            lamp.light = lamp_object

        return{'FINISHED'}

class delete_lamps(bpy.types.Operator):
    """Delete all lamps"""
    bl_idname = "srti.delete_lamps"
    bl_label = "Delete Lamps"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        lamp_list = context.scene.srti_props.list_lights

        bpy.ops.object.select_all(action='DESELECT')

        if lamp_list:
            for obj in lamp_list:
                obj.light.hide = False
                obj.light.select = True
    
        bpy.ops.object.delete()

        if not context.scene.srti_props.list_cameras: #delete the main object if no cameras
            delete_main(context.scene)
        
        context.scene.srti_props.list_lights.clear() #delete the idlist
        return{'FINISHED'}

class delete_active_lamp(bpy.types.Operator):
    """Delete selected lamp"""
    bl_idname = "srti.delete_active_lamp"
    bl_label = "Delete Active Lamp"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        lamp_list = context.scene.srti_props.list_lights
        active_lamp = context.active_object 
        i = 0 #need index to delete lamp

        bpy.ops.object.select_all(action='DESELECT')

        if lamp_list:
            for obj in lamp_list:
                if obj.light == active_lamp: 
                    print (obj)
                    lamp_list.remove(i)
                    active_lamp.select = True
                    bpy.ops.object.delete()
                    break
                i += 1

        if (not context.scene.srti_props.list_cameras) and len(lamp_list) < 1 : #delete the main object if no cameras and lights
            delete_main(context.scene)  
    
        return{'FINISHED'}

########CAMERA########
class create_cameras(bpy.types.Operator):
    """Create cameras"""
    bl_idname = "srti.create_cameras"
    bl_label = "Create cameras"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        curr_scene = context.scene

        #create the main parent
        create_main(curr_scene)
        main_parent = curr_scene.srti_props.main_parent

        camera_data = bpy.data.cameras.new("Camera")
        camera_object = bpy.data.objects.new("Camera", camera_data)
        curr_scene.objects.link(camera_object)

        camera_object.parent = main_parent
        camera_object.location = (0, 0, 2)

        camera = curr_scene.srti_props.list_cameras.add()
        camera.camera = camera_object

        return{'FINISHED'}

class delete_cameras(bpy.types.Operator):
    """Delete all cameras"""
    bl_idname = "srti.delete_cameras"
    bl_label = "Delete cameras"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        curr_scene = context.scene
        camera_list = curr_scene.srti_props.list_cameras

        bpy.ops.object.select_all(action='DESELECT')
        
        if camera_list:
            for obj in camera_list:
                obj.camera.select = True
    
        bpy.ops.object.delete()

        if not context.scene.srti_props.list_lights: #delete the main object if no lamps
             delete_main(context.scene)
        
        context.scene.srti_props.list_cameras.clear() #delete the idlist
              
        return{'FINISHED'}

class delete_active_camera(bpy.types.Operator):
    """Delete selected camera"""
    bl_idname = "srti.delete_active_camera"
    bl_label = "Delete Active Camera"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        camera_list = context.scene.srti_props.list_cameras
        active_cam = context.active_object 
        i = 0 #need index to delete lamp

        bpy.ops.object.select_all(action='DESELECT')

        if camera_list:
            for obj in camera_list:
                if obj.camera == active_cam: 
                    print (obj)
                    camera_list.remove(i)
                    active_cam.select = True
                    bpy.ops.object.delete()
                    break
                i += 1

        if (not context.scene.srti_props.list_lights) and len(camera_list) < 1 : #delete the main object if no cameras and lights
            delete_main(context.scene)  
    
        return{'FINISHED'}

####ANIMATION########
class animate_all(bpy.types.Operator):
    """Animate all lights, cameras and parameter"""
    bl_idname = "srti.animate_all"
    bl_label = "Animate all"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        #index
        index_light = 0
        index_cam = 0
        index_prop = 0

        #global var
        curr_scene = context.scene
        lamp_list = curr_scene.srti_props.list_lights
        camera_list = curr_scene.srti_props.list_cameras
        value_list = curr_scene.srti_props.list_values
        object = curr_scene.srti_props.main_object
        file_name = curr_scene.srti_props.save_name
        global file_lines

        #generated lists
        all_values = []
        material_list = []
        val_names = {}

        #generated value
        tot_light = max(len(lamp_list),1) #at least we want to iterate one frame over the camera when there are no lights
        tot_cam = len(camera_list)

        #set renderer to cycle (could be written in a setting file)
        curr_scene.render.engine = 'CYCLES'
        
        #Abort if no camera in scene
        if tot_cam < 1:
            self.report({'ERROR'}, "There are no cameras in the scene.")
            return{'CANCELLED'}

        file_lines.clear()

        #If there is no object selected we only iterate over cameras and lamps
        if not object:
            self.report({'WARNING'}, "No object selected for values.")
            tot_comb = 1
            file_lines.append("image,x_lamp,y_lamp,z_lamp")
        else:
            #add or update value node to all materials enabling nodes fore each
            #global material_list and delete all animation data
            file_lines.append("image,x_lamp,y_lamp,z_lamp,"+",".join(value.name for value in value_list))
            for material_slot in object.material_slots:
                if material_slot.material:
                    
                    material_slot.material.use_nodes = True
                    material_slot.material.node_tree.animation_data_clear() #delete animation
                    node_list=[]
                    index = 0

                    for value in value_list:
                        #for every value chek if node exist otherwise create a new one
                        node_name = "srti_" + value.name
                        if node_name in material_slot.material.node_tree.nodes:
                            node = material_slot.material.node_tree.nodes[node_name]
                        else:
                            node = material_slot.material.node_tree.nodes.new("ShaderNodeValue")
                            node.name = node_name
                            node.label = value.name
                            node.location = (0, -100*index)
                        node_list.append(node)
                        index += 1
                    material_list.append(node_list)

            #Creation of values array
            values = curr_scene.srti_props.list_values
            #global all_values
            index_name = 0
            for val in values:
                all_values.append(numpy.linspace(val.min,val.max,val.steps))
                val_names.update({val.name:index_name})
                index_name += 1
            print (all_values)
            tot_comb = numpy.prod(list(row.steps for row in values))

        print("---out---")
        print(material_list)
        print (all_values)
        print(file_lines)

        #Set animation boundaries
        tot_frames = tot_cam * tot_light * tot_comb
        curr_scene.frame_start = 1
        curr_scene.frame_end = tot_frames
        #val_combination = list(itertools.product(*all_values))

        #Delete animations for cameras and lamps
        for cam in camera_list:
            cam.camera.animation_data_clear()

        for lamp in lamp_list:
            lamp.light.animation_data_clear()

        #delete markers
        curr_scene.timeline_markers.clear()
        
        for curr_val in itertools.product(*all_values) if object else [0]: #Loop for every value combination (if no object we only do once)
            for material in material_list if object else []: #loop over every object's materials if there is an object              
                for val_node in material: #loop for every value node
                    #TODO add a marker name for parameters
                    curr_frame = (index_prop * tot_cam * tot_light)
                    val_node.outputs[0].keyframe_insert(data_path = "default_value", frame = curr_frame )
                    val_node.outputs[0].default_value = curr_val[val_names[val_node.name[5:]]]
                    val_node.outputs[0].keyframe_insert(data_path = "default_value", frame = curr_frame + 1)
            for cam in camera_list: #loop every camera
                curr_frame = index_prop*tot_cam*tot_light + index_cam * tot_light + 1
                mark = curr_scene.timeline_markers.new(cam.camera.name, curr_frame) # create a marker
                mark.camera = cam.camera

                if not lamp_list: #create the list when there aren't lights
                    string = "{0}_{1},,,".format(file_name, format_index(curr_frame,tot_frames))
                    if curr_val:
                        string +=","+",".join(str(x) for x in curr_val)
                    file_lines.append(string)
                    print(string)
                    
                for lamp in lamp_list: #loop every lamp
                    lamp = lamp.light
                    #animate lamps
                    curr_frame = (index_prop * tot_cam * tot_light) + (index_cam * tot_light) + index_light + 1
                    #hide lamp on theprevious and next frame
                    lamp.hide_render = True
                    lamp.hide = True
                    lamp.keyframe_insert(data_path = 'hide_render', frame = curr_frame - 1)
                    lamp.keyframe_insert(data_path = 'hide', frame = curr_frame - 1)
                    lamp.keyframe_insert(data_path = 'hide_render', frame = curr_frame + 1)
                    lamp.keyframe_insert(data_path = 'hide', frame = curr_frame + 1)
                    #rendo visibile la lampada solo nel suo frame
                    lamp.hide_render = False
                    lamp.hide = False
                    lamp.keyframe_insert(data_path = 'hide_render', frame = curr_frame)
                    lamp.keyframe_insert(data_path = 'hide', frame = curr_frame)

                    #add a line for the files with all the details
                    string = "%s-%s,%f,%f,%f" % (file_name, format_index(curr_frame, tot_frames), lamp.location[0], lamp.location[1], lamp.location[2])
                    if curr_val:
                        string += ","+ ",".join(str(x) for x in curr_val)
                    file_lines.append(string)
                    print(string)
                    index_light += 1

                index_cam += 1
                index_light = 0
            
            index_cam = 0
            index_prop += 1

        #self.report({'INFO'}, "Animation complete, total frames = %i" % tot_frames)
            
        return{'FINISHED'}

#####RENDERING######
class render_images(bpy.types.Operator):
    """Render all images"""
    bl_idname = "srti.render_images"
    bl_label = "Set Render"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        curr_scene = context.scene
        file_name = curr_scene.srti_props.save_name
        save_dir = curr_scene.srti_props.output_folder


        #TODO not usable with relative path
        #if not os.path.isdir(save_dir): #Check if path is set
        #    self.report({'ERROR'}, "No filepath.")
        #    return{'CANCELLED'}

        #TODO parametrize all export setting in a file for presets
        max_digit = len(str(calculate_tot_frame(context)))
        curr_scene.render.filepath = "{0}/EXR/{1}-{2}".format(save_dir[:-1],file_name,"#"*max_digit)

        #set render settings
        set_render_exr(curr_scene)

        #bpy.ops.render.view_show()
        #bpy.ops.render.render(animation=True)

        return{'FINISHED'}

class create_export_file(bpy.types.Operator):
    """Create a file with all the images name and parameters"""
    bl_idname = "srti.create_file"
    bl_label = "Create file"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return len(file_lines) != 0
    
    def execute(self, context):
        curr_scene = context.scene
        file_name = curr_scene.srti_props.save_name
        save_dir = curr_scene.srti_props.output_folder

        file = open(bpy.path.abspath(save_dir+file_name+".csv"), "w")
        for line in file_lines:
            file.write(line)
            file.write('\n')
        file.close()

        return{'FINISHED'}

#####TOOLS#####
#export lamps
class export_as_lamp(bpy.types.Operator, ExportHelper):
    """Create a file for lamp from active object vertices (Must be a MESH!)"""
    bl_idname = "srti.export_lamp"
    bl_label = "Export Lamp"
    bl_options = {'REGISTER', 'UNDO'}
    # ExportHelper mixin class uses this
    filename_ext = ".lp"
    filter_glob = bpy.props.StringProperty(
            default="*.lp",
            options={'HIDDEN'},
            maxlen=255,  # Max internal buffer length, longer would be clamped.
            )

    @classmethod
    def poll(cls, context):
        if context.active_object != None:
            if context.active_object.type == 'MESH': 
                return True
        return False

    def execute(self, context):
        obj = context.active_object
        i = 0
        list = []
        for vert in obj.data.vertices:
            coord = vert.co
            i += 1
            string = "{0:08d} {1} {2} {3}".format(i, coord[0], coord[1], coord[2])
            list.append(string)

        print(i)
        for string in list:
            print (string)

        file = open(self.filepath, "w")
        file.write(str(i))
        file.write('\n')
        for line in list:
            file.write(line)
            file.write('\n')

        file.close()
        return{'FINISHED'}

class create_export_node(bpy.types.Operator, ImportHelper):
    """Prepares the file to output png passes"""
    bl_idname = "srti.create_export_node"
    bl_label = "Create Nodes"
    bl_options = {'REGISTER', 'UNDO'}

    filename_ext = ".exr"
    filter_glob = bpy.props.StringProperty(
        default="*.exr",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
        )

    def execute(self, context):
        curr_scene = context.scene
        file_path = self.filepath
        folder_path = os.path.split(file_path)[0]
        file_name = os.path.splitext(bpy.path.basename(file_path))[0]
        project_name = re.split('\d+$', file_name)[0]
        image = bpy.data.images.load(file_path)
        #check if there is a project number suffix
        if file_name[0].isdigit(): 
            project_number = re.split('(^\d+)', file_name)[1]+"-"
        else:
            project_number = ''

        self.report({'OPERATOR'}, "file path: " + file_path)
        self.report({'OPERATOR'}, "file name: "+ file_name)
        self.report({'OPERATOR'}, "folder: "+ folder_path)
        self.report({'OPERATOR'}, "project name: "+ project_name)
        self.report({'OPERATOR'}, "project number: "+ project_number)

        #search for minimum and maximum frames
        list_of_files = os.listdir(folder_path)
        frame_max = frame_min = int(re.split('(\d+$)', file_name)[1])

        for file in list_of_files:
            #print(file)
            if os.path.splitext(file)[1].lower() == ".exr":
                num = int(re.split('(\d+)(?=\.exr$)', file, flags = re.I)[1])  # assuming filename is "filexxx.exr"
                #compare num to previous max, e.g.
                frame_max = num if num > frame_max else frame_max  
                frame_min = num if num < frame_min else frame_min
    
        self.report({'OPERATOR'},"max= "+ str(frame_max))
        self.report({'OPERATOR'},"min= "+ str(frame_min))

        #create nodes 
        curr_scene.use_nodes = True
        curr_scene.node_tree.use_opencl = True
        tree_nodes = curr_scene.node_tree.nodes
        tree_links = curr_scene.node_tree.links
        tree_nodes.clear() #delete all nodes

        ##image node
        node_image = tree_nodes.new(type = 'CompositorNodeImage')
        node_image.name = 'SRTI_IMAGE'
        node_image.location = (0,0)
        node_image.image = image
        if not node_image.has_layers:
            self.report({'ERROR'}, "Image is not valid.")
            curr_scene.use_nodes = False
            return{'CANCELLED'}
        node_image.layer = 'RenderLayer'
        image.source = 'SEQUENCE'
        node_image.use_auto_refresh = True
        node_image.frame_duration = frame_max

        ##Normal nodes
        #Normal multiply 0.5
        node_normal_mult = tree_nodes.new(type = 'CompositorNodeMixRGB')
        node_normal_mult.name = 'SRTI_NORMAL_MULT'
        node_normal_mult.label = 'NORMAL_MULT'
        node_normal_mult.location = (300,300)
        node_normal_mult.blend_type = 'MULTIPLY'
        node_normal_mult.inputs[0].default_value = 1
        tree_links.new(node_image.outputs['Normal'],node_normal_mult.inputs[1])
        node_normal_mult.inputs[2].default_value = (0.5, 0.5, 0.5, 1)
                
        #Normal add 0.5
        node_normal_add = tree_nodes.new(type = 'CompositorNodeMixRGB')
        node_normal_add.name = 'SRTI_NORMAL_ADD'
        node_normal_add.label = 'NORMAL_ADD'
        node_normal_add.location = (480,300)
        node_normal_add.blend_type = 'ADD'
        node_normal_add.inputs[0].default_value = 1
        tree_links.new(node_normal_mult.outputs[0],node_normal_add.inputs[1])
        node_normal_add.inputs[2].default_value = (0.5, 0.5, 0.5, 1)

        ##intermediate nodes
        #DIFF
        node_diff = tree_nodes.new(type = 'CompositorNodeMixRGB')
        node_diff.name = 'SRTI_DIFF'
        node_diff.label = 'DIFF'
        node_diff.location = (300,20)
        node_diff.blend_type = 'MULTIPLY'
        node_diff.inputs[0].default_value = 1
        tree_links.new(node_image.outputs['DiffDir'],node_diff.inputs[1])
        tree_links.new(node_image.outputs['DiffCol'],node_diff.inputs[2])

        #INDIFF
        node_indiff = tree_nodes.new(type = 'CompositorNodeMixRGB')
        node_indiff.name = 'SRTI_INDIFF'
        node_indiff.label = 'INDIFF'
        node_indiff.location = (460, -60)
        node_indiff.blend_type = 'MULTIPLY'
        node_indiff.inputs[0].default_value = 1
        tree_links.new(node_image.outputs['DiffInd'],node_indiff.inputs[1])
        tree_links.new(node_image.outputs['DiffCol'],node_indiff.inputs[2])

        #SPEC
        node_spec = tree_nodes.new(type = 'CompositorNodeMixRGB')
        node_spec.name = 'SRTI_SPEC'
        node_spec.label = 'SPEC'
        node_spec.location = (620,-140)
        node_spec.blend_type = 'MULTIPLY'
        node_spec.inputs[0].default_value = 1
        tree_links.new(node_image.outputs['GlossDir'],node_spec.inputs[1])
        tree_links.new(node_image.outputs['GlossCol'],node_spec.inputs[2])

        #INSPEC
        node_inspec = tree_nodes.new(type = 'CompositorNodeMixRGB')
        node_inspec.name = 'SRTI_INSPEC'
        node_inspec.label = 'INSPEC'
        node_inspec.location = (780,-220)
        node_inspec.blend_type = 'MULTIPLY'
        node_inspec.inputs[0].default_value = 1
        tree_links.new(node_image.outputs['GlossInd'],node_inspec.inputs[1])
        tree_links.new(node_image.outputs['GlossCol'],node_inspec.inputs[2])

        #DIFF-INDIFF
        node_diff_indiff = tree_nodes.new(type = 'CompositorNodeMixRGB')
        node_diff_indiff.name = 'SRTI_DIFF-INDIFF'
        node_diff_indiff.label = 'DIFF-INDIFF'
        node_diff_indiff.location = (940,20)
        node_diff_indiff.blend_type = 'ADD'
        node_diff_indiff.inputs[0].default_value = 1
        tree_links.new(node_diff.outputs[0],node_diff_indiff.inputs[1])
        tree_links.new(node_indiff.outputs[0],node_diff_indiff.inputs[2])
                
        #DIFF-SPEC
        node_diff_spec = tree_nodes.new(type = 'CompositorNodeMixRGB')
        node_diff_spec.name = 'SRTI_DIFF-SPEC'
        node_diff_spec.label = 'DIFF-SPEC'
        node_diff_spec.location = (1100,-60)
        node_diff_spec.blend_type = 'ADD'
        node_diff_spec.inputs[0].default_value = 1
        tree_links.new(node_diff.outputs[0],node_diff_spec.inputs[1])
        tree_links.new(node_spec.outputs[0],node_diff_spec.inputs[2])
                
        #DIFF-SPEC-INDIFF
        node_diff_spec_indiff = tree_nodes.new(type = 'CompositorNodeMixRGB')
        node_diff_spec_indiff.name = 'SRTI_DIFF-SPEC-INDIFF'
        node_diff_spec_indiff.label = 'DIFF-SPEC-INDIFF'
        node_diff_spec_indiff.location = (1260,-140)
        node_diff_spec_indiff.blend_type = 'ADD'
        node_diff_spec_indiff.inputs[0].default_value = 1
        tree_links.new(node_diff_spec.outputs[0],node_diff_spec_indiff.inputs[1])
        tree_links.new(node_indiff.outputs[0],node_diff_spec_indiff.inputs[2])
                
        #DIFF-SPEC-INDIFF-INSPEC
        node_diff_spec_indiff_inspec = tree_nodes.new(type = 'CompositorNodeMixRGB')
        node_diff_spec_indiff_inspec.name = 'SRTI_DIFF-SPEC-INDIFF-INSPEC'
        node_diff_spec_indiff_inspec.label = 'DIFF-SPEC-INDIFF-INSPEC'
        node_diff_spec_indiff_inspec.location = (1420,-220)
        node_diff_spec_indiff_inspec.blend_type = 'ADD'
        node_diff_spec_indiff_inspec.inputs[0].default_value = 1
        tree_links.new(node_diff_spec_indiff.outputs[0],node_diff_spec_indiff_inspec.inputs[1])
        tree_links.new(node_inspec.outputs[0],node_diff_spec_indiff_inspec.inputs[2])

        ##Outputs node
        #OUT_NORMAL
        node_out_normal = tree_nodes.new(type = 'CompositorNodeOutputFile')
        node_out_normal.name = 'SRTI_OUT_NORMAL'
        node_out_normal.label = 'OUT_NORMAL'
        node_out_normal.location = (660, 300)
        node_out_normal.file_slots.clear()
        node_out_normal.file_slots.new(project_name + "NORMAL-")
        tree_links.new(node_normal_add.outputs[0],node_out_normal.inputs[0])
        node_out_normal.base_path = os.path.abspath(folder_path + "\..\PNG")
        node_out_normal.format.file_format = 'PNG'
        node_out_normal.format.color_mode = 'RGB'
        node_out_normal.format.color_depth = '16'
        node_out_normal.format.compression = 0

        #OUT_COMPOSITE
        node_out_composite = tree_nodes.new(type = 'CompositorNodeOutputFile')
        node_out_composite.name = 'SRTI_OUT_COMPOSITE'
        node_out_composite.label = 'OUT_COMPOSITE'
        node_out_composite.location = (1640, 0)
        node_out_composite.file_slots.clear()
        node_out_composite.file_slots.new(project_number + "DIFF\\"+project_name+"DIFF-")
        tree_links.new(node_diff.outputs[0],node_out_composite.inputs[0])
        node_out_composite.file_slots.new(project_number + "DIFF-INDIFF\\"+project_name+"DIFF-INDIFF-")
        tree_links.new(node_diff_indiff.outputs[0],node_out_composite.inputs[1])
        node_out_composite.file_slots.new(project_number + "DIFF-SPEC\\"+project_name+"DIFF-SPEC-")
        tree_links.new(node_diff_spec.outputs[0],node_out_composite.inputs[2])
        node_out_composite.file_slots.new(project_number + "DIFF-SPEC-INDIFF\\"+project_name+"DIFF-SPEC-INDIFF-")
        tree_links.new(node_diff_spec_indiff.outputs[0],node_out_composite.inputs[3])
        node_out_composite.file_slots.new(project_number + "DIFF-SPEC-INDIFF-INSPEC\\"+project_name+"DIFF-SPEC-INDIFF-INSPEC-")
        tree_links.new(node_diff_spec_indiff_inspec.outputs[0],node_out_composite.inputs[4])
        node_out_composite.file_slots.new(project_number + "SHADOWS\\"+project_name+"SHADOWS-")
        tree_links.new(node_image.outputs["Shadow"],node_out_composite.inputs[5])
        node_out_composite.base_path = os.path.abspath(folder_path + "\..\PNG")
        node_out_composite.format.file_format = 'PNG'
        node_out_composite.format.color_mode = 'RGB'
        node_out_composite.format.color_depth = '16'
        node_out_composite.format.compression = 0

        #need a folder to save images
        curr_scene.render.filepath = os.path.abspath(folder_path + "\..\PNG\\tmp")+"\\tmp"
        curr_scene.render.resolution_percentage = 1

        #enable compositor
        curr_scene.render.use_compositing = True
        curr_scene.use_nodes = True
        curr_scene.frame_end = frame_max
        curr_scene.frame_start = 1

        return{'FINISHED'}

class render_normals(bpy.types.Operator):
    """Render a normal map"""
    bl_idname = "srti.render_normals"
    bl_label = "Render Normals"
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        if context.scene.node_tree == None or context.scene.node_tree.nodes.find("SRTI_OUT_COMPOSITE") == -1 or context.scene.node_tree.nodes.find("SRTI_OUT_NORMAL") == -1:
            return False
        else: 
            return True

    def execute(self, context):
        curr_scene = context.scene
        node_out_composite = curr_scene.node_tree.nodes["SRTI_OUT_COMPOSITE"]
        node_out_normal = curr_scene.node_tree.nodes["SRTI_OUT_NORMAL"]
        
        #mute composite output
        node_out_composite.mute = True
        node_out_normal.mute = False
        curr_scene.frame_current = 1

        #set output format
        curr_scene.render.image_settings.file_format = 'PNG'
        curr_scene.render.image_settings.color_mode = 'RGB'
        curr_scene.render.image_settings.color_depth = '16'
        curr_scene.render.image_settings.compression = 0

        #enable compositor
        curr_scene.render.use_compositing = True
        curr_scene.use_nodes = True

        #set color management to linear
        curr_scene.display_settings.display_device = 'None'
        
        #set rendering to overwrrite
        curr_scene.render.use_overwrite = True
 
        #render normal
        bpy.ops.render.render("INVOKE_DEFAULT")
        #bpy.ops.render.view_cancel()

        return{'FINISHED'}

class render_composite(bpy.types.Operator):
    """Render all composite images (! It may take time !)"""
    bl_idname = "srti.render_composite"
    bl_label = "Render Composite"
    bl_options = {'REGISTER'}
        
    @classmethod
    def poll(cls, context):
        if context.scene.node_tree == None or context.scene.node_tree.nodes.find("SRTI_OUT_COMPOSITE") == -1 or context.scene.node_tree.nodes.find("SRTI_OUT_NORMAL") == -1:
            return False
        else: 
            return True

    def execute(self, context):
        curr_scene = context.scene
        node_out_composite = curr_scene.node_tree.nodes["SRTI_OUT_COMPOSITE"]
        node_out_normal = curr_scene.node_tree.nodes["SRTI_OUT_NORMAL"]
        
        #mute normal output
        node_out_normal.mute = True
        node_out_composite.mute = False
        curr_scene.frame_current = 1
        #set output format
        curr_scene.render.image_settings.file_format = 'PNG'
        curr_scene.render.image_settings.color_mode = 'RGB'
        curr_scene.render.image_settings.color_depth = '16'
        curr_scene.render.image_settings.compression = 0

        #enable compositor
        curr_scene.render.use_compositing = True
        curr_scene.use_nodes = True

        #set color management to linear
        curr_scene.display_settings.display_device = 'None'
        
        #set rendering to not overwrrite
        curr_scene.render.use_overwrite = True
 
        #render composite animation
        bpy.ops.render.render("INVOKE_DEFAULT", animation = True, write_still=False)
        return{'FINISHED'}

class reset_nodes(bpy.types.Operator):
    """Reset workspace deleting nodes"""
    bl_idname = "srti.reset_nodes"
    bl_label = "Delete Nodes"
    bl_options = {'REGISTER', 'UNDO' }

    @classmethod
    def poll(cls, context):
        return context.scene.node_tree != None

    def execute(self, context):
        #reset all to normal
        curr_scene = context.scene
        set_render_exr(curr_scene)
        curr_scene.node_tree.nodes.clear()
        curr_scene.render.resolution_percentage = 100
        return{'FINISHED'}


# ui list item actions
class values_UIList(bpy.types.Operator):
    bl_idname = "srti.values_uilist"
    bl_label = "Values List"

    action = bpy.props.EnumProperty(
        items=(
            ('UP', "Up", ""),
            ('DOWN', "Down", ""),
            ('REMOVE', "Remove", ""),
            ('ADD', "Add", ""),
        )
    )

    def invoke(self, context, event):

        scn = context.scene
        idx = scn.srti_props.selected_value_index

        try:
            item = scn.srti_props.list_values[idx]
        except IndexError:
            pass

        else:
            if self.action == 'DOWN' and idx < len(scn.srti_props.list_values) - 1:
                item_next = scn.srti_props.list_values[idx+1].name
                scn.srti_props.list_values.move(idx, idx + 1)
                scn.srti_props.selected_value_index += 1
                info = 'Item %d selected' % (scn.srti_props.selected_value_index + 1)
                self.report({'INFO'}, info)

            elif self.action == 'UP' and idx >= 1:
                item_prev = scn.srti_props.list_values[idx-1].name
                scn.srti_props.list_values.move(idx, idx-1)
                scn.srti_props.selected_value_index -= 1
                info = 'Item %d selected' % (scn.srti_props.selected_value_index + 1)
                self.report({'INFO'}, info)

            elif self.action == 'REMOVE':
                info = 'Item %s removed from list' % (scn.srti_props.list_values[scn.srti_props.selected_value_index].name)
                scn.srti_props.selected_value_index -= 1
                self.report({'INFO'}, info)
                scn.srti_props.list_values.remove(idx)

        if self.action == 'ADD':
            item = scn.srti_props.list_values.add()
            #item.id = len(scn.srti_props.list_values)
            item.name = "Value" # assign name of selected object scn.srti_props.list_values
            scn.srti_props.selected_value_index = (len(scn.srti_props.list_values)-1)
            info = '%s added to list' % (item.name)
            self.report({'INFO'}, info)

        return {"FINISHED"}
    
##############
#####GUI######
##############
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
        row.operator("srti.delete_active_lamp", icon = "X")
        row.operator("srti.delete_lamps", icon = "X")
        row = layout.row(align = True)
        row.operator("srti.create_cameras",icon = "OUTLINER_DATA_CAMERA")
        row.operator("srti.delete_active_camera", icon = "X")
        row.operator("srti.delete_cameras", icon = "X")

        layout.prop(curr_scene.srti_props, "main_object", text = "Object")
        
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

        


 ######RNA PROPERTIES######

class light(bpy.types.PropertyGroup):
    light = bpy.props.PointerProperty(name="Light object",
        type = bpy.types.Object,
        description = "A lamp")

class camera(bpy.types.PropertyGroup):
    camera = bpy.props.PointerProperty(name = "Camera object",
        type = bpy.types.Object,
        description = "A camera")

class value(bpy.types.PropertyGroup):
    min = bpy.props.FloatProperty(default = 0)
    max = bpy.props.FloatProperty(default = 1)
    steps = bpy.props.IntProperty(default = 2, min = 2)

class srti_props(bpy.types.PropertyGroup):
    light_file_path = bpy.props.StringProperty(name="Lights file Path",
        subtype='FILE_PATH',
        default="*.lp",
        description = 'Path to the lights file.')

    output_folder = bpy.props.StringProperty(name="Save file directory",
        subtype='DIR_PATH',
        description = 'Path to the lights file.')

    save_name = bpy.props.StringProperty(name="Save file name",
        default = "Image",
        description = "file name")

    main_parent = bpy.props.PointerProperty(name="Main Parent",
        type=bpy.types.Object,
        description = "Main parent of the group")

    main_object = bpy.props.PointerProperty(name="Main object",
        type=bpy.types.Object,
        description = "Main object to apply material")

    modified = bpy.props.BoolProperty(name = "Boolean if not animated", default = True)

    selected_value_index = bpy.props.IntProperty()

    list_lights = bpy.props.CollectionProperty(type = light)
    list_cameras = bpy.props.CollectionProperty(type = camera)
    list_values = bpy.props.CollectionProperty(type = value)
    #list_file = bpy.props.CollectionProperty(type = bpy.props.StringProperty)

def register():
    ##register properties
    bpy.utils.register_class(light)
    bpy.utils.register_class(camera)
    bpy.utils.register_class(value)
    #bpy.utils.register_class(value_node)
    bpy.utils.register_class(srti_props)
    bpy.types.Scene.srti_props = bpy.props.PointerProperty(type = srti_props)

    #register operators
    bpy.utils.register_class(delete_lamps)
    bpy.utils.register_class(delete_active_lamp)
    bpy.utils.register_class(delete_cameras)
    bpy.utils.register_class(delete_active_camera)
    bpy.utils.register_class(create_lamps)
    bpy.utils.register_class(create_cameras)
    bpy.utils.register_class(create_export_file)
    bpy.utils.register_class(render_images)
    bpy.utils.register_class(animate_all)
    bpy.utils.register_class(Values_UL_items)
    bpy.utils.register_class(values_UIList)
    bpy.utils.register_class(export_as_lamp)
    bpy.utils.register_class(create_export_node)
    bpy.utils.register_class(render_normals)
    bpy.utils.register_class(render_composite)
    bpy.utils.register_class(reset_nodes)
    bpy.utils.register_class(SyntheticRTIPanelCreate)
    bpy.utils.register_class(SyntheticRTIPanelRender)
    bpy.utils.register_class(SyntheticRTIPanelTools)
    bpy.utils.register_class(SyntheticRTIPanelDebug)

def unregister():
    bpy.utils.unregister_class(SyntheticRTIPanelTools)
    bpy.utils.unregister_class(SyntheticRTIPanelDebug)
    bpy.utils.unregister_class(SyntheticRTIPanelRender)
    bpy.utils.unregister_class(SyntheticRTIPanelCreate)
    bpy.utils.unregister_class(export_as_lamp)
    bpy.utils.unregister_class(render_normals)
    bpy.utils.unregister_class(render_composite)
    bpy.utils.unregister_class(reset_nodes)
    bpy.utils.unregister_class(create_export_node)
    bpy.utils.unregister_class(Values_UL_items)
    bpy.utils.unregister_class(values_UIList)
    bpy.utils.unregister_class(create_cameras)
    bpy.utils.unregister_class(create_lamps)
    bpy.utils.unregister_class(delete_cameras)
    bpy.utils.unregister_class(delete_lamps)
    bpy.utils.unregister_class(delete_active_lamp)
    bpy.utils.unregister_class(delete_active_camera)
    bpy.utils.unregister_class(create_export_file)
    bpy.utils.unregister_class(render_images)
    bpy.utils.unregister_class(animate_all)
    bpy.utils.unregister_class(srti_props)
    bpy.utils.unregister_class(light)
    bpy.utils.unregister_class(camera)
    bpy.utils.unregister_class(value)
    #bpy.utils.register_class(value_node)
    #bpy.types.Scene.srti_props = bpy.props.PointerProperty(type = srti_props)

    ##Delete of custom rna data
    #del bpy.types.Scene.srti_light_file_path
    #del bpy.types.Scene.srti_main_parent_prop

if __name__ == "__main__":
    register()
