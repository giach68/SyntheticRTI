bl_info = {
    "name": "SyntheticRTI",
    "author": "Andrea Dall'Alba",
    "version": (0, 6, 0),
    "blender": (2, 80, 0),
    "location": "View3D > Tools > SyntheticRTI",
    "description": "Plugin to help creating the synthetic database for RTI",
    "warning": "This addon is still in development.",
    "wiki_url": "https://github.com/giach68/SyntheticRTI",
    "category": "3D View",
}

import bpy

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

def register():
    for module in classes:
        print("| Registering %s"%module.__name__)
        module.register()

def unregister():
    for module in reversed(classes):
        print("| Unregistering %s"%module.__name__)
        module.unregister()
    