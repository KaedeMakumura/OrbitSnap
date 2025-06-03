import bpy
from bpy.props import IntProperty, FloatProperty, BoolProperty, EnumProperty, StringProperty

class ORBITSNAP_PR_MainSettings(bpy.types.PropertyGroup):
    focal_length: IntProperty(name="Focal Length (mm)", default=50, min=28, max=150)
    margin_scale: FloatProperty(name="Margin Scale", default=1.3, min=0.5, max=2.0)

    orbit_step: EnumProperty(
        name="Orbit Step",
        description="水平回転の分割角度",
        items=[
            ('30', "30°", "30度刻みで撮影"),
            ('45', "45°", "45度刻みで撮影"),
            ('90', "90°", "90度刻みで撮影"),
        ],
        default='90'
    )

    use_angle_0: BoolProperty(name="horizontal", default=True)
    use_angle_30: BoolProperty(name="  30°", default=False)
    use_angle_45: BoolProperty(name="  45°", default=False)
    use_angle_60: BoolProperty(name="  60°", default=False)
    use_angle_m30: BoolProperty(name="-30°", default=False)
    use_angle_m45: BoolProperty(name="-45°", default=False)
    use_angle_m60: BoolProperty(name="-60°", default=False)

    show_watermark: bpy.props.BoolProperty(
        name="Watermark Info",
        description="Watermark の表示項目設定を展開します",
        default=False
    )

    w_datetime: BoolProperty(name="datetime", default=False)
    w_filename: BoolProperty(name="file_name", default=False)
    w_focal_length: BoolProperty(name="focal_length", default=False)
    w_orbit_angle: BoolProperty(name="orbit_angle", default=False)
    w_elevation_angle: BoolProperty(name="elevation_angle", default=False)
    w_note: BoolProperty(name="note", default=False)
    note: StringProperty(name="Note Text", default="")


def register():
    bpy.utils.register_class(ORBITSNAP_PR_MainSettings)

def unregister():
    bpy.utils.unregister_class(ORBITSNAP_PR_MainSettings)
