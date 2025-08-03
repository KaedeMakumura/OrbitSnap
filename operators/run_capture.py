import bpy
import os
from ..core.capture_manager import OrbitSnapManager
from ..core.watermark import Watermark
from ..properties.capture_settings import CaptureSettings

class ORBITSNAP_OT_RunCapture(bpy.types.Operator):
    bl_idname = "orbitsnap.run_capture"
    bl_label = "Shot Orbit Snap"
    bl_description = "選択オブジェクトを自動撮影します"

    # --- モーダル制御用変数 ---
    settings: CaptureSettings = None # executeで設定
    _manager: OrbitSnapManager = None
    writer: Watermark = None

    def execute(self, context):
        props = context.scene.orbit_snap_props

        # Eeveeだけ(Cyclesでの描画が遅いのでスクショしても何も映らない)
        engine = context.scene.render.engine
        if engine == 'CYCLES':
            self.report({'ERROR'}, "現在のレンダエンジンはCyclesです。Eeveeに変更してください。")
            return {'CANCELLED'}

        # 3DVIEWがアクティブでない場合
        area = bpy.context.area
        if area.type != 'VIEW_3D':
            self.report({'WARNING'}, "3Dビューが選択されていません！")
            return {'CANCELLED'}

        # オブジェクトが選択されていない場合
        selected_objects = context.selected_objects
        if not selected_objects:
            self.report({'WARNING'}, "オブジェクトが選択されていません！")
            return {'CANCELLED'}

        # 保存チェック
        if not bpy.data.filepath:
            self.report({'ERROR'}, "保存されていないファイルでは撮影できません！")
            return {'CANCELLED'}

        # --- 設定とマネージャーの準備 ---
        try:
            self.settings = CaptureSettings.from_props(props=props)
            # 保存先存在チェック
            if not os.path.isdir(self.settings.directory):
                self.report({'WARNING'}, "指定されたフォルダが存在しません: ")
                return {'CANCELLED'}

            self.writer = Watermark(settings=self.settings)
            self._manager = OrbitSnapManager(area, selected_objects, self.settings)
            self._manager.prepare() # ここでカメラ作成、視点変更などを行う


        except Exception as e:
            self.report({'ERROR'}, f"準備中にエラーが発生しました: {e}")
            self._cleanup() # エラー時もクリーンアップ
            return {'CANCELLED'}

        # --- 撮影開始
        try:

            for x_angle, z_angle in self.settings.shot_angle_list:

                # capture の引数を修正
                filepath = self._manager.capture(x_angle, z_angle)
                self.writer.draw(filepath=filepath, orbit_angle=z_angle, elevation_angle=x_angle)

            # フォルダを開く
            if self.settings.open_folder_after_capture:
                os.startfile(self._manager.save_dir)

            # 後片付け
            self.report({'INFO'}, "全キャプチャ完了！")
            self._cleanup()
            return {'FINISHED'}

        except Exception as e:
            self.report({'ERROR'}, f"撮影中にエラーが発生しました: {e}")
            self._cleanup() # エラー時もクリーンアップして終了
            return {'CANCELLED'}

    def _cleanup(self):

        # マネージャーの後処理
        if self._manager:
            try:
                self._manager.cleanup()
            except Exception as e:
                print(f"クリーンアップ中にエラー発生: {e}")

        # 変数リセット (念のため)
        self.settings = None
        self._manager = None


def register():
    bpy.utils.register_class(ORBITSNAP_OT_RunCapture)

def unregister():
    bpy.utils.unregister_class(ORBITSNAP_OT_RunCapture)
