import bpy


class ViewStateManager:
    """3D View の状態を取得・操作するクラス"""

    @staticmethod
    def get_view_state(area):
        """指定area(VIEW_3D)の状態を取得"""
        if area.type != 'VIEW_3D':
            raise ValueError("area.type != 'VIEW_3D'")
        space = area.spaces.active
        region_3d = space.region_3d
        return (
            space,
            region_3d.view_location.copy(),
            region_3d.view_rotation.copy(),
            region_3d.view_distance,
            region_3d.view_perspective,
        )

    @staticmethod
    def set_view_state(area, state):
        """指定area(VIEW_3D)の状態を復元"""
        if area.type != 'VIEW_3D':
            raise ValueError("area.type != 'VIEW_3D'")
        space = area.spaces.active
        region_3d = space.region_3d
        space, loc, rot, dist, persp = state
        region_3d.view_location = loc
        region_3d.view_rotation = rot
        region_3d.view_distance = dist
        region_3d.view_perspective = persp

    @staticmethod
    def get_overlay_visibility(area):
        """指定area(VIEW_3D)のオーバーレイ表示状態を取得"""
        if area.type != 'VIEW_3D':
            raise ValueError("area.type != 'VIEW_3D'")
        # spaces.active だけでもOK
        return area.spaces.active.overlay.show_overlays

    @staticmethod
    def set_overlay_visibility(area, visible: bool):
        """指定area(VIEW_3D)のオーバーレイ表示状態を設定"""
        if area.type != 'VIEW_3D':
            raise ValueError("area.type != 'VIEW_3D'")
        area.spaces.active.overlay.show_overlays = visible

    @staticmethod
    def switch_to_camera_view(area):
        """指定area(VIEW_3D)の視点をカメラに変更"""
        if area.type != 'VIEW_3D':
            raise ValueError("area.type != 'VIEW_3D'")
        space = area.spaces.active
        space.region_3d.view_perspective = 'CAMERA'
        space.camera = bpy.context.scene.camera