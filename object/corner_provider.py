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
        # === エンプティの情報を取得 ===
        scale = obj.scale
        empty_display_size = obj.empty_display_size

        # 表示サイズとスケールを考慮して実際の直方体サイズを求める（直径扱いに補正）
        size_x = scale.x * empty_display_size
        size_y = scale.y * empty_display_size
        size_z = scale.z * empty_display_size

        half = mathutils.Vector((size_x, size_y, size_z))  # 半サイズ＝±で定義する

        offsets = [
            (-half.x, -half.y, -half.z),
            (-half.x, -half.y,  half.z),
            (-half.x,  half.y, -half.z),
            (-half.x,  half.y,  half.z),
            ( half.x, -half.y, -half.z),
            ( half.x, -half.y,  half.z),
            ( half.x,  half.y, -half.z),
            ( half.x,  half.y,  half.z),
        ]

        corners = [obj.location + mathutils.Vector(offset) for offset in offsets]

        return corners

# 判別＆委譲関数
def get_corners(obj):
    if obj.type == 'EMPTY' and obj.empty_display_type == 'CUBE':
        provider = EmptyCubeCornerProvider()
    else:
        provider = ObjectCornerProvider()
    return provider.get_corners(obj)
