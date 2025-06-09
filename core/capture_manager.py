import bpy
import mathutils
import math
import os
from ..core.auto_camera import AutoCamera
from ..object.corner_provider import get_corners
from ..utils.view_state_manager import ViewStateManager
from ..properties.capture_settings import CaptureSettings

import bpy

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
        self.saved_views = ViewStateManager.get_view_state(self.area)
        self.visible_overlay = ViewStateManager.get_overlay_visibility(self.area)

        # 撮影用にオーバーレイを非表示にする
        ViewStateManager.set_overlay_visibility(self.area, False)

        timestamp = self.settings.datetime.strftime("%Y%m%d_%H%M%S")
        self.save_dir = os.path.join(self.settings.directory, f"capture_{timestamp}")
        os.makedirs(self.save_dir, exist_ok=True)

        self.blend_name = bpy.path.basename(bpy.data.filepath).replace(".blend", "")

        center_point, distance = self.calc_capture_info(self.selected_objects)

        self.camera_controller = AutoCamera(center_point, distance, self.settings)
        self.camera_controller.create_camera_and_empty()

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

    def get_scene_corners(self, objects):
        empties = [obj for obj in objects if obj.type == 'EMPTY' and obj.empty_display_type == 'CUBE']
        normals = [obj for obj in objects if not (obj.type == 'EMPTY' and obj.empty_display_type == 'CUBE')]
        if empties:
            if len(empties) > 1:
                print("Warning: 複数のEmptyCubeがありますが、最初の1つだけを使います。")
            return get_corners(empties[0])
        else:
            all_corners = []
            for obj in normals:
                all_corners.extend(get_corners(obj))
            return all_corners


    def calc_capture_info(self, objects):
        """選択されたオブジェクトが画角に収まる距離を計算する"""

        if not objects:
            raise ValueError("オブジェクトリストが空です")

        sensor_width = self.settings.sensor_width
        sensor_height = self.settings.sensor_height
        focal_length = self.settings.focal_length
        margin_scale = self.settings.margin_scale
        corners = self.get_scene_corners(objects)


        # バウンディングボックス8点
        center = sum(corners, mathutils.Vector()) / len(corners)

        max_distance = 0
        for angle in self.settings.shot_angle_list:
            x_angle = math.radians(angle[0])  # 水平（azimuth, yaw）
            z_angle = math.radians(angle[1])  # 仰角（elevation, pitch）

            # カメラ向き
            dir_x = math.cos(z_angle) * math.cos(x_angle)
            dir_y = math.cos(z_angle) * math.sin(x_angle)
            dir_z = math.sin(z_angle)
            direction = mathutils.Vector((dir_x, dir_y, dir_z)).normalized()
            up = mathutils.Vector((0, 0, 1))
            cam_pos = center + direction * 10
            width, height = self.get_bbox_size_in_camera_view(cam_pos, direction, up, corners)
            distance = self.calculate_required_distance(width, height, sensor_width, sensor_height, focal_length, margin_scale)
            max_distance = max(max_distance, distance)

        return center, max_distance


    def get_bbox_size_in_camera_view(self, cam_pos, cam_dir, cam_up, corners):
        # カメラ平面ベクトル
        forward = cam_dir.normalized()
        right = cam_up.cross(forward).normalized()
        up = forward.cross(right).normalized()

        # 各頂点を「カメラのスクリーン平面（right, up）」で直交射影
        screen_coords = []
        for corner in corners:
            v = corner - cam_pos
            x = v.dot(right)
            y = v.dot(up)
            screen_coords.append([x, y])
        # デバッグ表示
        print("screen_coords (on camera plane):", screen_coords)
        xs = [pt[0] for pt in screen_coords]
        ys = [pt[1] for pt in screen_coords]
        width = max(xs) - min(xs)
        height = max(ys) - min(ys)
        return width, height

    def calculate_required_distance(self, width, height, sensor_width, sensor_height, focal_length, margin_scale):
        fov_x = 2 * math.atan(sensor_width / (2 * focal_length))
        fov_y = 2 * math.atan(sensor_height / (2 * focal_length))
        dist_x = (width / 2) / math.tan(fov_x / 2)
        dist_y = (height / 2) / math.tan(fov_y / 2)
        return max(dist_x, dist_y) * margin_scale

    def cleanup(self):
        # オーバーレイを元に戻す
        if self.visible_overlay:
            ViewStateManager.set_overlay_visibility(self.area, self.visible_overlay)

        # 撮影直前のビューに戻す
        if self.saved_views:
            ViewStateManager.set_view_state(self.area, self.saved_views)

        # 撮影用の要素をすべて削除する
        AutoCamera.remove_camera_and_empty()
