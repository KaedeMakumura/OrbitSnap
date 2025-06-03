import os
from ..__init__ import addon_dir

def get_root_path() -> str:
    return addon_dir

def get_font_path(font_name: str = "NotoSansJP-Regular.ttf") -> str:
    addon_root = get_root_path()
    return os.path.join(addon_root, "fonts", font_name)