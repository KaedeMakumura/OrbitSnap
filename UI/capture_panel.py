import bpy

class ORBITSNAP_PT_Panel(bpy.types.Panel):
    bl_label = "Orbit Snap"
    bl_idname = "ORBITSNAP_PT_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "OrbitSnap"

    def draw(self, context):
        layout = self.layout
        props = context.scene.orbit_snap_props

        #保存フォルダ
        layout.prop(props, "directory")
        layout.separator()

        # 焦点距離とマージン
        layout.prop(props, "focal_length")
        layout.prop(props, "margin_scale")
        layout.separator()

        # 周囲をどの角度で撮影するか
        row = layout.row(align=True)
        row.label(text="Orbit Step")
        row.prop(props, "orbit_step", text="")

        # 仰角の設定
        row_t = layout.row(align=True)
        row_t.label(text="Elevation Angle")

        # 仰角0
        row1 = layout.row(align=True)
        row1.prop(props, "use_angle_0")

        # 仰角プラス
        row2 = layout.row(align=True)
        row2.prop(props, "use_angle_30")
        row2.prop(props, "use_angle_45")
        row2.prop(props, "use_angle_60")

        # 仰角マイナス
        row3 = layout.row(align=True)
        row3.prop(props, "use_angle_m30")
        row3.prop(props, "use_angle_m45")
        row3.prop(props, "use_angle_m60")

        # 写真への書き込み設定
        layout.separator()
        layout.label(text="Watermark Info")
        layout.prop(props, "w_datetime")
        layout.prop(props, "w_filename")
        layout.prop(props, "w_focal_length")
        layout.prop(props, "w_orbit_angle")
        layout.prop(props, "w_elevation_angle")
        layout.prop(props, "w_note")

        row4 = layout.row()
        row4.enabled = props.w_note
        row4.prop(props, "note")

        layout.separator()
        layout.operator("orbitsnap.run_capture", text="Shot Orbit Snap", icon="RENDER_STILL")

def register():
    bpy.utils.register_class(ORBITSNAP_PT_Panel)

def unregister():
    bpy.utils.unregister_class(ORBITSNAP_PT_Panel)
