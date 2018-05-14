import bpy
from mathutils import Vector
import numpy
import itertools


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
        file_path = curr_scene.srti_props.lightsFilePath

        #create the main parent
        create_main(curr_scene)
        main_parent = curr_scene.srti_props.main_parent

        file = open(file_path)
        righe = file.readlines() #copio tutte le linee in memoria
        file.close()
        
        n_luci = int(righe[0].split()[0])#La prima riga contiene il numero di luci totali
        digit_luci = len(str(n_luci)) #ricavo il numero di caratteri massimo per scrivere i numeri delle lampade
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
            lamp_object = bpy.data.objects.new(name="Lampada_{0:0>{dig}}".format(lamp, dig = digit_luci), object_data=lamp_data) # Create new object with our lamp datablock
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

        index_light = 0
        index_cam = 0
        index_prop = 0

        curr_scene = context.scene
        lamp_list = curr_scene.srti_props.list_lights
        camera_list = curr_scene.srti_props.list_cameras
        value_list = curr_scene.srti_props.list_values
        object = curr_scene.srti_props.main_object
        all_values = []
        material_list = []

        tot_light = len(lamp_list)
        tot_cam = len(camera_list)
        
        if tot_cam < 1:
            self.report({'ERROR'}, "There are any cameras in the scene.")
            return{'FINISHED'}

        if not object:
            self.report({'WARNING'}, "No object selected for values")
            tot_comb = 1
        else:
            #add value node to all materials enabling nodes fore each
            global material_list
            for material_slot in object.material_slots:
                if material_slot.material:
                    
                    material_slot.material.use_nodes = True
                    node_list=[]
                    for value in value_list:
                        node = material_slot.material.node_tree.nodes.new("ShaderNodeValue")

                        node.name = value.name
                        node.label = value.name
                        node_list.append(node)
                    material_list.append(node_list)

            print(material_list)

            #Creation of values array
            values = curr_scene.srti_props.list_values
            global all_values
            for val in values:
                all_values.append(numpy.linspace(val.min,val.max,val.steps))
            print (all_values)
            tot_comb = numpy.prod(list(row.steps for row in values))
        print("out")
        print(material_list)
        print (all_values)
        curr_scene.frame_start = 1
        curr_scene.frame_end = tot_cam * tot_light * tot_comb
        #val_combination = list(itertools.product(*all_values))

        #Delete animations
        for cam in camera_list:
            cam.camera.animation_data_clear()

        for lamp in lamp_list:
            lamp.light.animation_data_clear()

        #delete markers
        curr_scene.timeline_markers.clear()
        
        #TODO loop property
        for curr_val in itertools.product(*all_values) if object else [0]:

            for cam in camera_list: #loop every camera
                mark = curr_scene.timeline_markers.new(cam.camera.name, index_prop*tot_cam*tot_light + index_cam * tot_light + 1) # create a marker
                mark.camera = cam.camera
                for lamp in lamp_list: #loop every lamp
                    lamp = lamp.light
                    #animate lamps
                    curr_frame = (index_prop * tot_cam * tot_light) + (index_cam * tot_light) + index_light + 1
                    #hide lamp on theprevious and next frame
                    lamp.hide_render = True
                    lamp.keyframe_insert(data_path = 'hide_render', frame = curr_frame - 1)
                    lamp.keyframe_insert(data_path = 'hide_render', frame = curr_frame + 1)
                    #rendo visibile la lampada solo nel suo frame
                    lamp.hide_render = False
                    lamp.keyframe_insert(data_path = 'hide_render', frame = curr_frame)

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
    bl_label = "Render"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        #TODO è poi così necessario?
        return{'FINISHED'}

class create_export_file(bpy.types.Operator):
    """Create a file with all the iamges name and parameters"""
    bl_idname = "srti.create_file"
    bl_label = "Create file"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        #TODO
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
            item.name = "Value" # assign name of selected object
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
        row.label("Id: %d" % (index))
        row.prop(item, "name", text="", emboss=False, translate=False)
        row2 = row.row(align = True)
        row2.prop(item,"min")
        row2.prop(item,"max")
        row2.prop(item,"steps")

    def invoke(self, context, event):
        pass   


class SyntheticRTIPanel(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "Lamps"
    bl_idname = "srti.panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "SyntheticRTI"

    def draw(self, context):
        curr_scene = context.scene

        num_light = len(curr_scene.srti_props.list_lights)
        num_cam = len(curr_scene.srti_props.list_cameras)
        num_values = len(curr_scene.srti_props.list_values)
        tot_comb = numpy.prod(list(row.steps for row in curr_scene.srti_props.list_values))

        if curr_scene.srti_props.main_parent:
            main = curr_scene.srti_props.main_parent.name
        else:
            main = "None"

        layout = self.layout
        layout.prop(curr_scene.srti_props, "lightsFilePath", text = 'File')
        row = layout.row(align = True)
        row.operator("srti.create_lamps", icon ="OUTLINER_DATA_LAMP")
        row.operator("srti.delete_lamps", icon = "X")
        row = layout.row(align = True)
        row.operator("srti.create_cameras",icon = "OUTLINER_DATA_CAMERA")
        row.operator("srti.delete_cameras", icon = "X")
        box = layout.box()
        box.label("RNA PROP")
        box.label("main = %s" % main)
        box.label("lamps = %i" % num_light)
        box.label("cameras = %i" % num_cam)
        box.label ("Values = %i" % num_values)
        box.label("Combnation = %i" % tot_comb)
        box.label("frame totali = %i" % (num_light * num_cam *tot_comb))

        row = layout.row()
        row.template_list("Values_UL_items", "", curr_scene.srti_props, "list_values", curr_scene.srti_props, "selected_value_index", rows=3)

        col = row.column(align=True)
        col.operator("srti.values_uilist", icon='ZOOMIN', text="").action = 'ADD'
        col.operator("srti.values_uilist", icon='ZOOMOUT', text="").action = 'REMOVE'
        col.separator()
        col.operator("srti.values_uilist", icon='TRIA_UP', text="").action = 'UP'
        col.operator("srti.values_uilist", icon='TRIA_DOWN', text="").action = 'DOWN'

        layout.prop(curr_scene.srti_props, "main_object", text = "Object")
        
        col = layout.column(align = True)
        col.operator("srti.animate_all", icon ="KEYINGSET")
        col.operator("srti.render_images", icon = "RENDER_ANIMATION")
        col.operator("srti.create_file", icon = "FILE_TEXT")

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
    #name = bpy.props.StringProperty()
    min = bpy.props.FloatProperty(default = 0)
    max = bpy.props.FloatProperty(default = 1)
    steps = bpy.props.IntProperty(default = 2, min = 2)

class value_node(bpy.types.PropertyGroup):
    node = bpy.props.PointerProperty(name = "Value Node",
        type = bpy.types.Node,
        description = "value nodes")

class srti_props(bpy.types.PropertyGroup):
    lightsFilePath = bpy.props.StringProperty(name="Lights file Path",
        subtype='FILE_PATH',
        default="*.lp",
        description = 'Path to the lights file.')

    main_parent = bpy.props.PointerProperty(name="Main Parent",
        type=bpy.types.Object,
        description = "Main parent of the group")

    main_object = bpy.props.PointerProperty(name="Main object",
        type=bpy.types.Object,
        description = "Main object to apply material")

    selected_value_index = bpy.props.IntProperty()

    list_lights = bpy.props.CollectionProperty(type = light)
    list_cameras = bpy.props.CollectionProperty(type = camera)
    list_values = bpy.props.CollectionProperty(type = value)
    list_nodes = bpy.props.CollectionProperty(type = value_node)

def register():

    ##register properties
    bpy.utils.register_class(light)
    bpy.utils.register_class(camera)
    bpy.utils.register_class(value)
    bpy.utils.register_class(value_node)
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
    bpy.utils.register_class(SyntheticRTIPanel)

def unregister():
    bpy.utils.unregister_class(SyntheticRTIPanel)
    bpy.utils.unregister_class(create_cameras)
    bpy.utils.unregister_class(create_lamps)
    bpy.utils.unregister_class(delete_cameras)
    bpy.utils.unregister_class(delete_lamps)
    bpy.utils.unregister_class(create_export_file)
    bpy.utils.unregister_class(render_images)
    bpy.utils.unregister_class(animate_all)

    ##Delete of custom rna data
    del bpy.types.Scene.srti_lightsFilePath
    del bpy.types.Scene.srti_main_parent_prop

if __name__ == "__main__":
    register()