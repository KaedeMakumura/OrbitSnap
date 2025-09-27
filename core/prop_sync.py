import bpy
from bpy.app.handlers import persistent
from .props_access import copy_props, get_wm_props, get_scene_props


@persistent
def on_load_post(_dummy):
    """When a .blend is opened, reflect Scene -> WM if Scene was saved."""
    wm_props = get_wm_props(bpy.context)
    scene_props = get_scene_props(bpy.context)
    if wm_props is None or scene_props is None:
        return

    # Only overwrite WM if Scene has been initialized/persisted
    initialized = getattr(scene_props, 'initialized', False)
    if initialized:
        copy_props(wm_props, scene_props)
    else:
        # Keep WM defaults
        pass


@persistent
def on_save_pre(_dummy):
    """Before saving the .blend, sync WM -> Scene so values persist."""
    wm_props = get_wm_props(bpy.context)
    scene_props = get_scene_props(bpy.context)
    if wm_props is None or scene_props is None:
        return
    try:
        copy_props(scene_props, wm_props)
        setattr(scene_props, 'initialized', True)
    except Exception:
        pass
