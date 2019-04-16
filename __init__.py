bl_info = {
    "name": "SyntheticRTI",
    "author": "Andrea Dall'Alba",
    "version": (0, 5, 0),
    "blender": (2, 80, 0),
    "location": "View3D > Tools > SyntheticRTI",
    "description": "Plugin to help creating the synthetic database for RTI",
    "warning": "This addon is still in development.",
    "wiki_url": "https://github.com/giach68/SyntheticRTI",
    "category": "3D View",
}

import bpy

from . import auto_load
    

from .srtiutilities import srtiproperties
from .srtiutilities import srtigui
from .srtiutilities.srtioperators import srtiop_create
from .srtiutilities.srtioperators import srtiop_render
from .srtiutilities.srtioperators import srtiop_tools

print('| Registering properties' )
srtiproperties.register()
bpy.types.Scene.srti_props = bpy.props.PointerProperty(type = srtiproperties.srti_props)
print('| Initialize submodules' )
classes = ( srtiop_create, srtiop_render, srtiop_tools, srtigui)
# register, unregister = bpy.utils.register_submodule_factory(__name__, classes)

# auto_load.init()
def register():
    # auto_load.register()
    # srtiproperties.register()
    # srtiop_create.register()
    # srtiop_render.register()
    # srtiop_tools.register()
    # srtigui.register()
    for module in classes:
        print("| Registering %s"%module.__name__)
        module.register()

def unregister():
    # srtiop_create.unregister()
    for module in reversed(classes):
        print("| Unregistering %s"%module.__name__)
        module.unregister()
    # auto_load.unregister()


# submodules = ('srtiutilities.srtioperators.srtiop_tools')
# register, unregister = bpy.utils.register_submodule_factory(__name__, submodules)
# print('maledetto')



# load and reload submodules
##################################

# import importlib
# from . import developer_utils
# importlib.reload(developer_utils)
# modules = developer_utils.setup_addon_modules(__path__, __name__, "bpy" in locals())
# 
# srtiproperties.register()



#'srtiutilities.srtiproperties', 'srtiutilities.srtigui', 'srtiutilities.srtioperators.srtiop_create','srtiutilities.srtioperators.srtiop_render'

# register
##################################

# import traceback

# def register():

#     #try: bpy.utils.register_module(__name__)
#     #except: traceback.print_exc()

#     #print("Registered {} with {} modules".format(bl_info["name"], len(modules)))

# def unregister():
#     try: bpy.utils.unregister_module(__name__)
#     except: traceback.print_exc()

#     #print("Unregistered {}".format(bl_info["name"]))
