###OPERATORS###
import bpy
import os
from ..srtifunc import *
from mathutils import Vector
from ..srtiproperties import file_lines as file_lines

#########LAMP#########
class SRTI_OT_create_lamps(bpy.types.Operator):
    """Create lamps from .lp file."""
    bl_idname = "srti.create_lamps"
    bl_label = "Create Lamps"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        curr_scene = context.scene
        props = curr_scene.srti_props
        file_path = props.C_L_light_file_path

        #check if valid .lp file
        if not os.path.isfile(file_path) or os.path.splitext(file_path)[1] != ".lp":
            self.report({'ERROR'}, 'No valid file selected on '+file_path)
            return {'CANCELLED'}

        bpy.ops.srti.delete_lamps() #delete exsisting lamps

        light_collection = get_lights_collection(curr_scene) #get light collection
        main_parent = get_main(curr_scene) #get main

        #open file
        file = open(file_path)
        rows = file.readlines() #copy all lines in memory
        file.close()
        
        #read file's rows
        n_lights = int(rows[0].split()[0])#in the first row there is the total count of lights
        print("- Creating %i lamps ---"%n_lights)
        
        ##Use standard light, TODO add a differente object
        lamp_data = bpy.data.lights.new(name="Project_light", type='SUN') # Create new lamp datablock.  It s going to be created outside
        
        #create all light
        for lamp in range(1, n_lights + 1): #step trought all lamps
            valori_riga = rows[lamp].split() #split values
            lmp_x = float(valori_riga[1])
            lmp_y = float(valori_riga[2])
            lmp_z = float(valori_riga[3])
            direction = Vector((lmp_x, lmp_y, lmp_z))

            print("-- ", lamp , 'x=', lmp_x, 'y=', lmp_y, 'z=', lmp_z) #print all values
            lamp_object = bpy.data.objects.new(name="Lamp_{0}".format(format_index(lamp, n_lights)), object_data=lamp_data) # Create new object with our lamp datablock
            light_collection.objects.link(lamp_object) # Link lamp object to the scene so it'll appear in this scene
            lamp_object.parent = main_parent
            lamp_object.location = (lmp_x, lmp_y, lmp_z) # Place lamp to a specified location
            
            lamp_object.rotation_mode = 'QUATERNION'
            lamp_object.rotation_quaternion = direction.to_track_quat('Z','Y')
            
            ##change the name
            lamp = props.C_L_list_lights.add()
            lamp.light = lamp_object

        self.report({'INFO'},"Created %i lamps."%n_lights)
        return{'FINISHED'}

class SRTI_OT_delete_lamps(bpy.types.Operator):
    """Delete all lamps"""
    bl_idname = "srti.delete_lamps"
    bl_label = "Delete Lamps"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        curr_scene = context.scene
        props = curr_scene.srti_props
        lamp_list = props.C_L_list_lights

        if lamp_list:
            print("- Deleting all lamps ---")
            light_collection = get_lights_collection(curr_scene) #get light collection
            bpy.ops.object.select_all(action='DESELECT') #deselect all lamps

            #select all lights
            for obj in lamp_list:
                obj.light.hide_viewport = False
                obj.light.select_set(True)
    
            bpy.ops.object.delete()

            props.C_L_list_lights.clear() #delete the idlist
            bpy.data.collections.remove(light_collection) #remove light collection
            check_lamp_cam(curr_scene) # check presence of cameras

            self.report({'INFO'},"Deleted all lamps.")

        return{'FINISHED'}

########CAMERA########
class SRTI_OT_create_cameras(bpy.types.Operator):
    """Create cameras"""
    bl_idname = "srti.create_cameras"
    bl_label = "Create Camera"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        curr_scene = context.scene
        props = curr_scene.srti_props

        camera_collection = get_camera_collection(curr_scene) #get camera collection
        main_parent = get_main(curr_scene) #get main

        print("- Creating new camera ---")
        camera_data = bpy.data.cameras.new("Camera")
        camera_object = bpy.data.objects.new("Camera", camera_data)
        camera_collection.objects.link(camera_object)

        camera_object.parent = main_parent
        camera_object.location = (0, 0, 2)

        camera = props.C_C_list_cameras.add()
        camera.camera = camera_object

        self.report({'INFO'},"Created camera: %s."%camera.camera.name)
        return{'FINISHED'}

class SRTI_OT_delete_cameras(bpy.types.Operator):
    """Delete all cameras"""
    bl_idname = "srti.delete_cameras"
    bl_label = "Delete Cameras"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        curr_scene = context.scene
        props = curr_scene.srti_props
        camera_list = props.C_C_list_cameras
        
        if camera_list:
            print("- Deleting all cameras ---")
            camera_collection = get_camera_collection(curr_scene) #get camera collection
            bpy.ops.object.select_all(action='DESELECT') #deselect all objects

            #select all cameras
            for obj in camera_list:
                obj.camera.select_set(True)

            bpy.ops.object.delete() #delete slected objects

            bpy.data.collections.remove(camera_collection) #remove camera collection    
            props.C_C_list_cameras.clear() #delete the idlist
            check_lamp_cam(curr_scene) # check presence of lights

            self.report({'INFO'},"Deleted all cameras")
        return{'FINISHED'}

# ui list item actions
class SRTI_OT_values_uilist(bpy.types.Operator):

    bl_idname = "srti.values_uilist"
    bl_label = "Values List"

    action : bpy.props.EnumProperty(
        items=(
            ('UP', "Up", ""),
            ('DOWN', "Down", ""),
            ('REMOVE', "Remove", ""),
            ('ADD', "Add", ""),
        )
    )

    def invoke(self, context, event):

        curr_scene = context.scene
        props = curr_scene.srti_props
        idx = props.C_V_selected_value_index

        try:
            item = props.C_V_list_values[idx]
        except IndexError:
            pass

        else:
            if self.action == 'DOWN' and idx < len(props.C_V_list_values) - 1:
                item_next = props.C_V_list_values[idx+1].name
                props.C_V_list_values.move(idx, idx + 1)
                props.C_V_selected_value_index += 1
                info = 'Item %d selected' % (props.C_V_selected_value_index + 1)
                self.report({'INFO'}, info)

            elif self.action == 'UP' and idx >= 1:
                item_prev = props.C_V_list_values[idx-1].name
                props.C_V_list_values.move(idx, idx-1)
                props.C_V_selected_value_index -= 1
                info = 'Item %d selected' % (props.C_V_selected_value_index + 1)
                self.report({'INFO'}, info)

            elif self.action == 'REMOVE':
                info = 'Item %s removed from list' % (props.C_V_list_values[props.C_V_selected_value_index].name)
                props.C_V_selected_value_index -= 1
                self.report({'INFO'}, info)
                props.C_V_list_values.remove(idx)

        if self.action == 'ADD':
            item = props.C_V_list_values.add()
            #item.id = len(props.C_V_list_values)
            item.name = "Value" # assign name of selected object props.C_V_list_values
            props.C_V_selected_value_index = (len(props.C_V_list_values)-1)
            info = '%s added to list' % (item.name)
            self.report({'INFO'}, info)

        return {"FINISHED"}



classes = (SRTI_OT_create_lamps, SRTI_OT_delete_lamps, SRTI_OT_create_cameras, SRTI_OT_delete_cameras, SRTI_OT_values_uilist)
register, unregister = bpy.utils.register_classes_factory(classes)