import bpy
from mathutils import Vector

###Global var###

srti_lamp_list = []
srti_camera_list = []
srti_main_parent = []

###Various function###

####TMP
def printdebug():
    print("Lamp:")
    print(srti_lamp_list)
    print("camera:")
    print(srti_camera_list)
    print("main:")
    print(srti_main_parent)

def populate(context):
    """populate global variables from the main parent name when loading a file"""
    global srti_main_parent 
    global srti_lamp_list
    global srti_camera_list

    parent_name = context.scene.srti_main_parent_prop
    if parent_name:
        print(parent_name)
        main_parent = context.scene.objects[parent_name]
        srti_main_parent.append(main_parent)
        
        for obj in context.scene.objects:
            if obj.parent == main_parent:
                if obj.type == 'LAMP': #take all lights
                    srti_lamp_list.append(obj)
                elif obj.type == 'CAMERA': #take all cameras
                    srti_camera_list.append(obj)

        printdebug()
    else:
        print("Nothing to load")

def create_main(scene):
    """Create the main object if not already present"""
    #Aggiungo un empty a cui collegare tutte le luci per poter modificarle come gruppo
    global srti_main_parent 

    if not srti_main_parent:
        main_parent = bpy.data.objects.new(name = "main_parent", object_data = None)
        scene.objects.link(main_parent)
        main_parent.empty_draw_type = 'SPHERE'
   
        srti_main_parent.append(main_parent) 
        scene.srti_main_parent_prop = main_parent.name

def delete_main(scene):
    """Delete main parent"""
    global srti_main_parent 

    bpy.ops.object.select_all(action='DESELECT')
    if srti_main_parent:
        srti_main_parent[0].select = True #delete the main parent (need revision)
    bpy.ops.object.delete()
    srti_main_parent = []
    scene.srti_main_parent_prop = "" #delete the property of the main parent

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
        file_path = curr_scene.srti_lightsFilePath

        #create the main parent
        create_main(curr_scene)
        main_parent = srti_main_parent[0]

        file = open(file_path)
        righe = file.readlines() #copio tutte le linee in memoria
        file.close()
        
        n_luci = int(righe[0].split()[0])#La prima riga contiene il numero di luci totali
        digit_luci = len(str(n_luci)) #ricavo il numero di caratteri massimo per scrivere i numeri delle lampade
        print(n_luci)
        
        ##Uso una luce standard, TODO aggiungere un oggetto
        lamp_data = bpy.data.lamps.new(name="Luce_progetto", type='SUN') # Create new lamp datablock. It s going to be created outside

        
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
            
            lamp_object.keyframe_insert(data_path = 'hide_render', frame = i-1)
            srti_lamp_list.append(lamp_object)

        return{'FINISHED'}

class delete_lamps(bpy.types.Operator):
    """Delete all lamps"""
    bl_idname = "srti.delete_lamps"
    bl_label = "Delete Lamps"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        global srti_lamp_list

        bpy.ops.object.select_all(action='DESELECT')

        if srti_lamp_list:
            for obj in srti_lamp_list:
                obj.select = True
    
        bpy.ops.object.delete()

        if not srti_camera_list: #delete the main object if no cameras
            delete_main(context.scene)

        srti_lamp_list = [] #delete information in global variable

        return{'FINISHED'}

########CAMERA########
class create_cameras(bpy.types.Operator):
    """Create cameras"""
    bl_idname = "srti.create_cameras"
    bl_label = "Create cameras"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        #bpy.ops.srti.delete_cameras() #delete exsisting cameras

        curr_scene = context.scene

        #create the main parent
        create_main(curr_scene)
        main_parent = srti_main_parent[0]

        camera_data = bpy.data.cameras.new("Camera")
        camera_object = bpy.data.objects.new("Camera", camera_data)
        curr_scene.objects.link(camera_object)

        camera_object.parent = main_parent
        camera_object.location = (0, 0, 2)

        srti_camera_list.append(camera_object)

        return{'FINISHED'}

class delete_cameras(bpy.types.Operator):
    """Delete all cameras"""
    bl_idname = "srti.delete_cameras"
    bl_label = "Delete cameras"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        global srti_camera_list
        bpy.ops.object.select_all(action='DESELECT')
        
        if srti_camera_list:
            for obj in srti_camera_list:
                obj.select = True
    
        bpy.ops.object.delete()

        if not srti_lamp_list: #delete the main object if no lamps
             delete_main(context.scene)
        
        srti_camera_list = []
              
        return{'FINISHED'}

####ANIMATION########
class animate_all(bpy.types.Operator):
    """Animate all lights, cameras and parameter"""
    bl_idname = "srti.animate_all"
    bl_label = "Animate all"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):

        #TODO gestire le proprietà
        global srti_camera_list
        global srti_lamp_list
        global srti_main_parent

        index_light = 0
        index_cam = 0
        index_prop = 0

        tot_light = len(srti_lamp_list)
        tot_cam = len(srti_camera_list)
        
        curr_scene = context.scene
        
        curr_scene.frame_start = 1
        curr_scene.frame_end = tot_cam * tot_light

        #Delete animations
        for cam in srti_camera_list:
            cam.animation_data_clear()

        for lamp in srti_lamp_list:
            lamp.animation_data_clear()

        #delete markers
        curr_scene.timeline_markers.clear()
        
        #TODO loop property

        for cam in srti_camera_list: #loop every camera
            mark = curr_scene.timeline_markers.new(cam.name, index_prop + index_cam * tot_light + 1) # create a marker
            mark.camera = cam
            for lamp in srti_lamp_list: #loop every lamp
                #animate lamps
                curr_frame = (index_prop * tot_cam * tot_light) + (index_cam * tot_light) + index_light + 1
                #hide lamp on theprevious and next frame
                lamp.hide_render = True
                lamp.keyframe_insert(data_path = 'hide_render', frame = curr_frame-1)
                lamp.keyframe_insert(data_path = 'hide_render', frame = curr_frame+1)
                #rendo visibile la lampada solo nel suo frame
                lamp.hide_render = False
                lamp.keyframe_insert(data_path = 'hide_render', frame = curr_frame)

                index_light += 1

            index_cam += 1
            index_light = 0
            
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
    
##############
#####GUI######
##############

class SyntheticRTIPanel(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "Lamps"
    bl_idname = "srti.panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "SyntheticRTI"

    def draw(self, context):
        layout = self.layout
        ##layout.operator("")
        layout.prop(context.scene, "srti_lightsFilePath", text = 'File')
        layout.operator("srti.create_lamps")
        layout.operator("srti.delete_lamps")
        layout.operator("srti.create_cameras")
        layout.operator("srti.delete_cameras")
        layout.label("main = %s" % (str(len(srti_main_parent))))
        layout.label("lamps = %s" % (str(len(srti_lamp_list))))
        layout.label("cameras = %s" % (str(len(srti_camera_list))))
        layout.label("frame totali = %s" % (str(len(srti_camera_list) * len(srti_lamp_list))))
        layout.operator("srti.animate_all")
        layout.operator("srti.render_images")
        layout.operator("srti.create_file")

def register():
    ##Scene data definition
    ##File path of selected lights file
    bpy.types.Scene.srti_lightsFilePath = bpy.props.StringProperty(
            name="Lights file Path",
            subtype='FILE_PATH',
            default="*.lp",
            description = 'Path to the lights file.'      
            )
    bpy.types.Scene.srti_main_parent_prop = bpy.props.StringProperty()
    bpy.utils.register_class(delete_lamps)
    bpy.utils.register_class(delete_cameras)
    bpy.utils.register_class(create_lamps)
    bpy.utils.register_class(create_cameras)
    bpy.utils.register_class(create_export_file)
    bpy.utils.register_class(render_images)
    bpy.utils.register_class(animate_all)
    bpy.utils.register_class(SyntheticRTIPanel)
    populate(bpy.context)

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