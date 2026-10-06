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
        self.camera_obj.data.sensor_height = self.settings.sensor_height
        self.camera_obj.data.sensor_fit = 'AUTO'
        self.camera_obj.data.type = 'PERSP'

        bpy.context.scene.camera = self.camera_obj
        self.camera_obj[AutoCamera.CUSTOM_KEY] = True

        bpy.context.scene.render.resolution_x = self.settings.resolution_x
        bpy.context.scene.render.resolution_y = self.settings.resolution_y
        bpy.context.scene.render.resolution_percentage = 100



    def place_camera(self, x_angle: float, z_angle: float):
        loc = self.calculate_camera_location(x_angle, z_angle)
        self.camera_obj.location = loc
        self.camera_obj.rotation_euler = self.rotation_for_angles(x_angle, z_angle).to_euler()


    def calculate_camera_location(self, x_angle: float, z_angle: float):
        return self.center_point + self.orbit_offset(x_angle, z_angle) * self.distance

    @staticmethod
    def orbit_offset(x_angle: float, z_angle: float):
        """x_angleは仰角、z_angleはワールドZ軸まわりの周回角。"""
        rot_x = mathutils.Matrix.Rotation(math.radians(-x_angle), 4, 'X')
        rot_z = mathutils.Matrix.Rotation(math.radians(z_angle), 4, 'Z')
        return rot_z @ rot_x @ mathutils.Vector((0, -1, 0))

    @staticmethod
    def rotation_for_angles(x_angle, z_angle):
        return (-AutoCamera.orbit_offset(x_angle, z_angle)).to_track_quat('-Z', 'Y')

    def remove_camera_and_empty(self):
        """カメラとエンプティをシーンから削除する"""
        for obj in (self.camera_obj, self.empty_obj):
            if obj is None:
                continue
            data = obj.data if obj.type == 'CAMERA' else None
            bpy.data.objects.remove(obj, do_unlink=True)
            if data is not None and data.users == 0:
                bpy.data.cameras.remove(data)
        self.camera_obj = None
        self.empty_obj = None
