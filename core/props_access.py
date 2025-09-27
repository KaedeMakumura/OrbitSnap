import bpy
from typing import Optional, Tuple

# Centralized attribute names
WM_ATTR = "orbit_snap_ui"
SCENE_ATTR = "orbit_snap_props"


def _pg_type():
    # Lazy import to avoid circular deps at module import time
    from ..properties.property_group import ORBITSNAP_PR_MainSettings
    return ORBITSNAP_PR_MainSettings


def register_pointer_properties():
    """Attach PointerProperty for UI (WM) and persistence (Scene)."""
    pg = _pg_type()
    setattr(bpy.types.WindowManager, WM_ATTR, bpy.props.PointerProperty(type=pg))
    setattr(bpy.types.Scene, SCENE_ATTR, bpy.props.PointerProperty(type=pg))


def unregister_pointer_properties():
    for owner, attr in ((bpy.types.WindowManager, WM_ATTR), (bpy.types.Scene, SCENE_ATTR)):
        if hasattr(owner, attr):
            delattr(owner, attr)


def get_wm_props(context):
    return getattr(context.window_manager, WM_ATTR, None)


def get_scene_props(context):
    return getattr(context.scene, SCENE_ATTR, None)


def get_ui_props(context) -> Tuple[Optional[object], str]:
    """Return (props, source) where source in {WM, SCENE, NONE}."""
    wm_props = get_wm_props(context)
    if wm_props is not None:
        return wm_props, "WM"
    scene_props = get_scene_props(context)
    if scene_props is not None:
        return scene_props, "SCENE"
    return None, "NONE"


def _prop_names():
    return list(_pg_type().__annotations__.keys())


def copy_props(dst, src):
    for name in _prop_names():
        try:
            setattr(dst, name, getattr(src, name))
        except Exception:
            pass


def copy_ui_to_scene(context) -> bool:
    wm_props = get_wm_props(context)
    scene_props = get_scene_props(context)
    if wm_props is None or scene_props is None:
        return False
    try:
        copy_props(scene_props, wm_props)
        # mark as initialized to allow Scene -> WM restoration on load
        setattr(scene_props, 'initialized', True)
        return True
    except Exception:
        return False


def copy_scene_to_ui(context) -> bool:
    wm_props = get_wm_props(context)
    scene_props = get_scene_props(context)
    if wm_props is None or scene_props is None:
        return False
    try:
        copy_props(wm_props, scene_props)
        return True
    except Exception:
        return False

