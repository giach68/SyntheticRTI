bl_info = {
    "name": "SyntheticRTI",
    "author": "Andrea Dall'Alba",
    "version": (0, 1),
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
from bpy_extras.io_utils import ExportHelper, ImportHelper

####Global values###
file_lines = []

###Various function###

def create_main(scene):
    """Create the main object if not already present"""
    #Aggiungo un empty a cui collegare tutte le luci per poter modificarle come gruppo
 
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

def format_index(num, tot):
    tot_dig = len(str(tot))
    return "{0:0{dig}d}".format(num, dig = tot_dig)

def calculate_tot_frame(context):
    """Return the numbers of total frames
    """
    curr_scene = context.scene
    num_light = max(len(curr_scene.srti_props.list_lights),1)
    num_cam = len(curr_scene.srti_props.list_cameras)
    num_values = len(curr_scene.srti_props.list_values)
    tot_comb = numpy.prod(list(row.steps for row in curr_scene.srti_props.list_values))
    return int(num_light * num_cam * max(tot_comb,1))

#TODO implement
def get_unice_value_name(name, list):
    return name

  
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

        #create the main parent
        create_main(curr_scene)
        main_parent = curr_scene.srti_props.main_parent

        file = open(file_path)
        righe = file.readlines() #copio tutte le linee in memoria
        file.close()
        
        n_luci = int(righe[0].split()[0])#La prima riga contiene il numero di luci totali
        #digit_luci = len(str(n_luci)) #ricavo il numero di caratteri massimo per scrivere i numeri delle lampade
        print(n_luci)
        
        ##Uso una luce standard, TODO aggiungere un oggetto
        lamp_data = bpy.data.lamps.new(name="Luce_progetto", type='SUN') # Create new lamp datablock.  It s going to be created outside
        
        for lamp in range(1, n_luci + 1): #passo tutte le luci
            valori_riga = righe[lamp].split() #divido i valori
            lmp_x = float(valori_riga[1])
            lmp_y = float(valori_riga[2])
            lmp_z = float(valori_riga[3])
            direction = Vector((lmp_x, lmp_y, lmp_z))

            print(lamp , 'x=', lmp_x, 'y=', lmp_y, 'z=', lmp_z) #stampo i valori per riga
            lamp_object = bpy.data.objects.new(name="Lampada_{0}".format(format_index(lamp, n_luci)), object_data=lamp_data) # Create new object with our lamp datablock
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
        
        #TODO loop property
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

        #set output format
        curr_scene.render.image_settings.file_format = 'OPEN_EXR_MULTILAYER'
        curr_scene.render.image_settings.color_mode = 'RGBA'
        curr_scene.render.image_settings.color_depth = '32'
        curr_scene.render.image_settings.exr_codec = 'ZIP'

        #disable compositor
        curr_scene.render.use_compositing = True
        curr_scene.use_nodes = False

        #set color management to linear
        curr_scene.display_settings.display_device = 'None'
        
        #set rendering to not overwrrite
        curr_scene.render.use_overwrite = False

        #set render passes
        curr_rend_layer = curr_scene.render.layers.active
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

        #bpy.ops.render.view_show()
        #bpy.ops.render.render(animation=True)

        return{'FINISHED'}

class create_export_file(bpy.types.Operator):
    """Create a file with all the iamges name and parameters"""
    bl_idname = "srti.create_file"
    bl_label = "Create file"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        curr_scene = context.scene
        file_name = curr_scene.srti_props.save_name
        save_dir = curr_scene.srti_props.output_folder

        #TODO not usable with relative path
        #if not os.path.isdir(save_dir): #Check if path is set
        #    self.report({'ERROR'}, "No filepath.")
        #    return{'CANCELLED'}

        file = open(bpy.path.abspath(save_dir+file_name+".csv"), "w")
        for line in file_lines:
            file.write(line)
            file.write('\n')
        file.close()

        return{'FINISHED'}

#####TOOLS#####

#export lamps
class export_as_lamp(bpy.types.Operator, ExportHelper):
    """Create a file for lamp from active object vertices"""
    bl_idname = "srti.export_lamp"
    bl_label = "Export Lamp"
    bl_options = {'REGISTER', 'UNDO'}
    # ExportHelper mixin class uses this
    filename_ext = ".ls"
    filter_glob = bpy.props.StringProperty(
            default="*.ls",
            options={'HIDDEN'},
            maxlen=255,  # Max internal buffer length, longer would be clamped.
            )

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

#TODO prepare nodes
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
        print(self.filepath)
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
        row.operator("srti.delete_lamps", icon = "X")
        row = layout.row(align = True)
        row.operator("srti.create_cameras",icon = "OUTLINER_DATA_CAMERA")
        row.operator("srti.delete_cameras", icon = "X")
        
        row = layout.row()
        row.template_list("Values_UL_items", "", curr_scene.srti_props, "list_values", curr_scene.srti_props, "selected_value_index", rows=3)

        col = row.column(align=True)
        col.operator("srti.values_uilist", icon='ZOOMIN', text="").action = 'ADD'
        col.operator("srti.values_uilist", icon='ZOOMOUT', text="").action = 'REMOVE'
        col.separator()
        col.operator("srti.values_uilist", icon='TRIA_UP', text="").action = 'UP'
        col.operator("srti.values_uilist", icon='TRIA_DOWN', text="").action = 'DOWN'

        layout.prop(curr_scene.srti_props, "main_object", text = "Object")

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
        col = layout.column(align = True)
        col.operator("srti.animate_all", icon ="KEYINGSET")
        layout.prop(curr_scene.srti_props, "output_folder", text = 'Output folder')
        layout.prop(curr_scene.srti_props, "save_name", text = 'Output name')
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
        layout.operator("srti.create_export_node", icon = "NODETREE")


###Debug
class SyntheticRTIPanelDebug(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "Debug"
    bl_idname = "srti.panelDebug"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "SyntheticRTI"

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
        box.label("main = %s" % main)
        box.label("lamps = %i" % num_light)
        box.label("cameras = %i" % num_cam)
        box.label("Values = %i" % num_values)
        box.label("Combnation = %i" % tot_comb)
        box.label("frame totali = %i" % (num_light * num_cam *tot_comb))


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
    bpy.utils.register_class(delete_cameras)
    bpy.utils.register_class(create_lamps)
    bpy.utils.register_class(create_cameras)
    bpy.utils.register_class(create_export_file)
    bpy.utils.register_class(render_images)
    bpy.utils.register_class(animate_all)
    bpy.utils.register_class(Values_UL_items)
    bpy.utils.register_class(values_UIList)
    bpy.utils.register_class(export_as_lamp)
    bpy.utils.register_class(create_export_node)
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
    bpy.utils.unregister_class(create_export_node)
    bpy.utils.unregister_class(Values_UL_items)
    bpy.utils.unregister_class(values_UIList)
    bpy.utils.unregister_class(create_cameras)
    bpy.utils.unregister_class(create_lamps)
    bpy.utils.unregister_class(delete_cameras)
    bpy.utils.unregister_class(delete_lamps)
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