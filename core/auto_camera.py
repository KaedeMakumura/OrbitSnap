import bpy
import mathutils
import math
from ..properties.capture_settings import CaptureSettings

class AutoCamera:
    """カメラとターゲット用エンプティを作成し、移動させるクラス"""

    CUSTOM_KEY = "orbitSnapObject" #掃除用のカスタムプロパティ

    def __init__(self, center_point: mathutils.Vector, distance: float, settings: CaptureSettings):
        self.center_point = center_point
        self.distance = distance
        self.settings = settings
        self.camera_obj = None
        self.empty_obj = None

    def create_camera_and_empty(self):
        """カメラとエンプティを作成してシーンにリンクする"""
        self.empty_obj = bpy.data.objects.new("OrbitSnapEmpty", None)
        bpy.context.collection.objects.link(self.empty_obj)
        self.empty_obj.location = self.center_point
        self.empty_obj[AutoCamera.CUSTOM_KEY] = True

        cam_data = bpy.data.cameras.new("OrbitSnapCameraData")
        self.camera_obj = bpy.data.objects.new("OrbitSnapCamera", cam_data)
        bpy.context.collection.objects.link(self.camera_obj)

        # 焦点距離とセンサー幅を設定する
        self.camera_obj.data.lens = self.settings.focal_length
        self.camera_obj.data.sensor_width = self.settings.sensor_width
        self.camera_obj.data.type = 'PERSP'

        bpy.context.scene.camera = self.camera_obj
        self.camera_obj[AutoCamera.CUSTOM_KEY] = True

        bpy.context.scene.render.resolution_x = self.settings.resolution_x
        bpy.context.scene.render.resolution_y = self.settings.resolution_y
        bpy.context.scene.render.resolution_percentage = 100



    def place_camera(self, x_angle: float, z_angle: float):
        loc = self.calculate_camera_location(x_angle, z_angle)
        self.camera_obj.location = loc
        direction = self.center_point - self.camera_obj.location
        self.camera_obj.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()


    def calculate_camera_location(self, x_angle: float, z_angle: float):
        rot_x = mathutils.Matrix.Rotation(math.radians(-x_angle), 4, 'X')
        rot_z = mathutils.Matrix.Rotation(math.radians(z_angle), 4, 'Z')
        offset = rot_z @ rot_x @ mathutils.Vector((0, -self.distance, 0))
        return self.center_point + offset

    @staticmethod
    def remove_camera_and_empty():
        """カメラとエンプティをシーンから削除する"""
        to_remove = [obj for obj in bpy.context.scene.objects if obj.get(AutoCamera.CUSTOM_KEY)]
        for obj in to_remove:
            bpy.data.objects.remove(obj, do_unlink=True)
        print(f"🧹 OrbitSnapオブジェクト削除完了: {len(to_remove)}個")
