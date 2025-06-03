bl_info = {
    "name": "Orbit Snap",
    "author": "Kaede Makimura",
    "version": (0, 1, 0),
    "blender": (4, 2, 0),
    "location": "View3D > Sidebar > OrbitSnap Tab",
    "description": "自動撮影ツール",
    "category": "3D View",
}

import bpy
import os
# モジュールをインポート
from .properties import property_group
from .operators import run_capture
from .UI import capture_panel

#ルートパスの定義
addon_dir = os.path.dirname(__file__)

modules = [
    property_group,
    run_capture,
    capture_panel,
]

def register():
    for mod in modules:
        mod.register()
    bpy.types.Scene.orbit_snap_props = bpy.props.PointerProperty(type=property_group.ORBITSNAP_PR_MainSettings)

def unregister():
    for mod in reversed(modules):
        mod.unregister()
    del bpy.types.Scene.orbit_snap_props

if __name__ == "__main__":
    register()
