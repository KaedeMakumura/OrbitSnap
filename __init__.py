import bpy
import os
# モジュールをインポート
from .properties import property_group
from .operators import run_capture
from .UI import capture_panel
from .core import prop_sync
from .core import props_access

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
    # Dual storage: WM for UI edits (non-persistent), Scene for persistence
    props_access.register_pointer_properties()

    # Initialize WM from Scene when a .blend is opened
    if prop_sync.on_load_post not in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.append(prop_sync.on_load_post)
    # Before saving, sync WM -> Scene so values persist even without running
    if prop_sync.on_save_pre not in bpy.app.handlers.save_pre:
        bpy.app.handlers.save_pre.append(prop_sync.on_save_pre)
    # Also run once for current session
    try:
        prop_sync.on_load_post(None)
    except Exception:
        pass

def unregister():
    for mod in reversed(modules):
        mod.unregister()
    if prop_sync.on_load_post in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(prop_sync.on_load_post)
    if prop_sync.on_save_pre in bpy.app.handlers.save_pre:
        bpy.app.handlers.save_pre.remove(prop_sync.on_save_pre)
    props_access.unregister_pointer_properties()

if __name__ == "__main__":
    register()
