
import bpy
from .srtifunc import *

####Global values###
file_lines = []

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
    name = bpy.props.StringProperty(update = update_value_name)
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
    print("-"*40)
    print("registering properties")
    print(__name__)
    
    ##register properties
    bpy.utils.register_class(light)
    bpy.utils.register_class(camera)
    bpy.utils.register_class(value)
    #bpy.utils.register_class(value_node)
    bpy.utils.register_class(srti_props)
    bpy.types.Scene.srti_props = bpy.props.PointerProperty(type = srti_props)


#def unregister():
#    bpy.utils.unregister_class(SyntheticRTIPanelTools)
#    bpy.utils.unregister_class(SyntheticRTIPanelDebug)
#    bpy.utils.unregister_class(SyntheticRTIPanelRender)
#    bpy.utils.unregister_class(SyntheticRTIPanelCreate)
#    bpy.utils.unregister_class(export_as_lamp)
#    bpy.utils.unregister_class(render_normals)
#    bpy.utils.unregister_class(render_composite)
#    bpy.utils.unregister_class(reset_nodes)
#    bpy.utils.unregister_class(create_export_node)
#    bpy.utils.unregister_class(Values_UL_items)
#    bpy.utils.unregister_class(values_UIList)
#    bpy.utils.unregister_class(create_cameras)
#    bpy.utils.unregister_class(create_lamps)
#    bpy.utils.unregister_class(delete_cameras)
#    bpy.utils.unregister_class(delete_lamps)
#    bpy.utils.unregister_class(delete_active_lamp)
#    bpy.utils.unregister_class(delete_active_camera)
#    bpy.utils.unregister_class(create_export_file)
#    bpy.utils.unregister_class(render_images)
#    bpy.utils.unregister_class(animate_all)
#    bpy.utils.unregister_class(srti_props)
#    bpy.utils.unregister_class(light)
#    bpy.utils.unregister_class(camera)
#    bpy.utils.unregister_class(value)
#    #bpy.utils.register_class(value_node)
#    #bpy.types.Scene.srti_props = bpy.props.PointerProperty(type = srti_props)

#    ##Delete of custom rna data
#    #del bpy.types.Scene.srti_light_file_path
#    #del bpy.types.Scene.srti_main_parent_prop

#if __name__ == "__main__":
#    print("registering main")
#    print(__main__)
#    register()
