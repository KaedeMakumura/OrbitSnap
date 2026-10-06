import bpy
import mathutils
import os
from ..core.auto_camera import AutoCamera
from ..object.corner_provider import get_framing_points
from ..utils.view_state_manager import ViewStateManager
from ..properties.capture_settings import CaptureSettings
from .framing import required_distance


class OrbitSnapManager:
    def __init__(self, area, selected_objects, settings: CaptureSettings):
        self.area = area
        self.selected_objects   = selected_objects
        self.settings           = settings
        self.camera_controller  = None
        self.save_dir           = None
        self.blend_name         = None
        self.saved_views        = None # 撮影直前のビュー情報を保持
        self.visible_overlay    = None # 撮影直前のオーバーレイの表示状態を保持
        self.shot_count = 0
        self.saved_render = None
        self.saved_camera = None
        self.saved_space_camera = None

    def prepare(self):
        """
        撮影準備
        ・撮影後､現在のビューに戻すために現在のビューを記録しておく
        ・スクリーンショット等に使用する日時､ファイル名の準備
        ・カメラ位置の計算と設置
        ・オーバーレイを非表示にする
        ・カメラ視点にする

        Returns:None

        """
        # 現在のビューの状態を記録｡処理終了後にこの視点に戻すため｡
        scene = bpy.context.scene
        self.saved_camera = scene.camera
        self.saved_space_camera = self.area.spaces.active.camera
        render = scene.render
        self.saved_render = (render.resolution_x, render.resolution_y,
                             render.resolution_percentage, render.filepath)
        self.saved_views = ViewStateManager.get_view_state(self.area)
        self.visible_overlay = ViewStateManager.get_overlay_visibility(self.area)

        # 撮影用にオーバーレイを非表示にする
        ViewStateManager.set_overlay_visibility(self.area, False)

        timestamp = self.settings.datetime.strftime("%Y%m%d_%H%M%S")
        self.save_dir = os.path.join(self.settings.directory, f"capture_{timestamp}")
        os.makedirs(self.save_dir, exist_ok=True)

        self.blend_name = bpy.path.basename(bpy.data.filepath).replace(".blend", "")

        self.camera_controller = AutoCamera(mathutils.Vector((0, 0, 0)), 1, self.settings)
        self.camera_controller.create_camera_and_empty()
        center_point, distance = self.calc_capture_info(self.selected_objects)
        self.camera_controller.center_point = center_point
        self.camera_controller.distance = distance
        self.camera_controller.empty_obj.location = center_point

        # スクリーンショット用に視点を変更
        ViewStateManager.switch_to_camera_view(self.area)

    def capture(self, x_angle: float, z_angle: float):
        """指定された角度で1枚の画像を撮影"""
        self.camera_controller.place_camera(x_angle, z_angle)

        filename = f"{self.blend_name}_shot_{self.shot_count:03d}_x{x_angle:+03d}_z{z_angle:03d}.png"
        filepath = os.path.join(self.save_dir, filename)

        bpy.context.scene.render.filepath = filepath

        bpy.ops.render.opengl(write_still=True) # 注:撮影はパネルを操作した画面で実行される
        self.shot_count += 1 # ショット数をインクリメント
        return filepath # 撮影したファイルパスを返す

    def calc_capture_info(self, objects):
        """選択されたオブジェクトが画角に収まる距離を計算する"""

        if not objects:
            raise ValueError("オブジェクトリストが空です")
        points = get_framing_points(objects, bpy.context.evaluated_depsgraph_get())
        if not points:
            raise ValueError("撮影対象の形状を取得できません")
        if not self.settings.shot_angle_list:
            raise ValueError("撮影角度が設定されていません")
        center = mathutils.Vector(tuple(
            (min(p[axis] for p in points) + max(p[axis] for p in points)) / 2
            for axis in range(3)))
        relative_points = [point - center for point in points]

        # Blenderの画角にはセンサーフィット・解像度・ピクセル比が反映される。
        camera = self.camera_controller.camera_obj.data
        frame = camera.view_frame(scene=bpy.context.scene)
        horizontal_slope = max(abs(v.x / v.z) for v in frame)
        vertical_slope = max(abs(v.y / v.z) for v in frame)
        distance = 0.0
        maximum_depth = 0.0
        for elevation, orbit in self.settings.shot_angle_list:
            rotation = AutoCamera.rotation_for_angles(elevation, orbit)
            right = rotation @ mathutils.Vector((1, 0, 0))
            up = rotation @ mathutils.Vector((0, 1, 0))
            forward = rotation @ mathutils.Vector((0, 0, -1))
            local_points = [(p.dot(right), p.dot(up), p.dot(forward))
                            for p in relative_points]
            distance = max(distance, required_distance(
                local_points, horizontal_slope, vertical_slope,
                self.settings.margin_scale, camera.clip_start))
            maximum_depth = max(maximum_depth, max(p[2] for p in local_points))
        camera.clip_end = max(camera.clip_end, (distance + maximum_depth) * 1.01)
        return center, distance

    def cleanup(self):
        # オーバーレイを元に戻す
        if self.visible_overlay is not None:
            ViewStateManager.set_overlay_visibility(self.area, self.visible_overlay)

        # 撮影直前のビューに戻す
        if self.saved_views:
            ViewStateManager.set_view_state(self.area, self.saved_views)

        # 撮影用の要素をすべて削除する
        if self.camera_controller is not None:
            self.camera_controller.remove_camera_and_empty()
        if self.saved_render is not None:
            scene = bpy.context.scene
            scene.camera = self.saved_camera
            self.area.spaces.active.camera = self.saved_space_camera
            (scene.render.resolution_x, scene.render.resolution_y,
             scene.render.resolution_percentage, scene.render.filepath) = self.saved_render
