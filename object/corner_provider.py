from abc import ABC, abstractmethod
import mathutils

# 共通インターフェース
class CornerProvider(ABC):
    @abstractmethod
    def get_corners(self, obj):
        pass

# 通常オブジェクト用
class ObjectCornerProvider(CornerProvider):
    def get_corners(self, obj):
        corners = []
        for v in obj.bound_box:
            world_v = obj.matrix_world @ mathutils.Vector(v)
            corners.append(world_v)
        return corners

# エンプティCube用
class EmptyCubeCornerProvider(CornerProvider):
    def get_corners(self, obj):
        # 回転と親オブジェクトの変換を含め、ワールド座標へ変換する。
        size = obj.empty_display_size
        corners = [obj.matrix_world @ mathutils.Vector((x * size, y * size, z * size))
                   for x in (-1, 1) for y in (-1, 1) for z in (-1, 1)]

        return corners

# 判別＆委譲関数
def get_corners(obj):
    if obj.type == 'EMPTY' and obj.empty_display_type == 'CUBE':
        provider = EmptyCubeCornerProvider()
    else:
        provider = ObjectCornerProvider()
    return provider.get_corners(obj)


def get_framing_points(objects, depsgraph):
    """変形後の形状を一度取得する。Empty Cubeを選択していれば、その範囲を優先する。"""
    for obj in objects:
        if obj.type == 'EMPTY' and obj.empty_display_type == 'CUBE':
            return get_corners(obj)
    points = []
    for obj in objects:
        evaluated = obj.evaluated_get(depsgraph)
        if obj.type in {'MESH', 'CURVE', 'SURFACE', 'FONT', 'META'}:
            try:
                mesh = evaluated.to_mesh()
                if mesh is not None:
                    points.extend(evaluated.matrix_world @ vertex.co for vertex in mesh.vertices)
            finally:
                evaluated.to_mesh_clear()
        else:
            # ライト・カメラ・通常のエンプティは撮影範囲を決める境界ボックスを持たない。
            if obj.type not in {'EMPTY', 'LIGHT', 'CAMERA'}:
                points.extend(get_corners(evaluated))
    return points
