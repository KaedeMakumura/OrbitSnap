"""実行方法: blender --background --factory-startup --python-exit-code 1 --python tests/blender_framing.py"""

import datetime
import importlib
import math
from pathlib import Path
import sys
import tempfile
import types

import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector

# 拡張機能のUI・Pillowの初期化処理を実行せずに、対象モジュールを読み込む。
root = Path(__file__).resolve().parents[1]
package = types.ModuleType('orbitsnap')
package.__path__ = [str(root)]
sys.modules['orbitsnap'] = package
AutoCamera = importlib.import_module('orbitsnap.core.auto_camera').AutoCamera
Manager = importlib.import_module('orbitsnap.core.capture_manager').OrbitSnapManager
Settings = importlib.import_module('orbitsnap.properties.capture_settings').CaptureSettings
provider = importlib.import_module('orbitsnap.object.corner_provider')
solve = importlib.import_module('orbitsnap.core.framing').required_distance


def area_for_tests():
    region = types.SimpleNamespace(view_location=Vector((0, 0, 0)),
                                   view_rotation=AutoCamera.rotation_for_angles(0, 0),
                                   view_distance=10, view_perspective='PERSP')
    space = types.SimpleNamespace(region_3d=region, camera=bpy.context.scene.camera,
                                  overlay=types.SimpleNamespace(show_overlays=False))
    return types.SimpleNamespace(type='VIEW_3D', spaces=types.SimpleNamespace(active=space))


angles = [(e, o) for e in (-60, -30, 0, 30, 60) for o in range(0, 360, 30)]
scene = bpy.context.scene
bpy.ops.mesh.primitive_cube_add(location=(3, -4, 2))
subject = bpy.context.object
subject.scale = (1, 5, 2)
subject.rotation_euler = (0.2, 0.4, 0.7)
modifier = subject.modifiers.new('Expanded geometry', 'SOLIDIFY')
modifier.thickness = 2
bpy.context.view_layer.update()
original_camera = scene.camera
original_render = (scene.render.resolution_x, scene.render.resolution_y,
                   scene.render.resolution_percentage, scene.render.filepath)
camera_count = len(bpy.data.cameras)
checks = 0
with tempfile.TemporaryDirectory() as directory:
    for aspect, (width, height) in {'landscape': (1920, 1080),
                                   'portrait': (1080, 1920), 'square': (1080, 1080)}.items():
        for margin in (1.0, 1.3):
            for lens in (28, 50, 150):
                for pixel_aspect in (1, 2):
                    scene.render.pixel_aspect_x = pixel_aspect
                    settings = Settings(datetime=datetime.datetime.now(), directory=directory,
                                        aspect_ratio=aspect, resolution_x=width, resolution_y=height,
                                        focal_length=lens, margin_scale=margin, shot_angle_list=angles)
                    area = area_for_tests()
                    manager = Manager(area, [subject], settings)
                    manager.prepare()
                    points = provider.get_framing_points([subject], bpy.context.evaluated_depsgraph_get())
                    minimum_edge = 1.0
                    for elevation, orbit in angles:
                        manager.camera_controller.place_camera(elevation, orbit)
                        bpy.context.view_layer.update()
                        camera = manager.camera_controller.camera_obj
                        limit = (1 - 1 / margin) / 2
                        for point in points:
                            ndc = world_to_camera_view(scene, camera, point)
                            assert limit - 2e-5 <= ndc.x <= 1 - limit + 2e-5, (aspect, ndc)
                            assert limit - 2e-5 <= ndc.y <= 1 - limit + 2e-5, (aspect, ndc)
                            assert camera.data.clip_start <= ndc.z <= camera.data.clip_end
                            minimum_edge = min(minimum_edge, ndc.x - limit, ndc.y - limit,
                                               1 - limit - ndc.x, 1 - limit - ndc.y)
                            checks += 1
                    # 共通の撮影距離でも、少なくとも1つの角度では頂点が指定領域の端に接する。
                    assert abs(minimum_edge) < 2e-5, minimum_edge
                    manager.cleanup()
                    assert scene.camera == original_camera
                    assert area.spaces.active.overlay.show_overlays is False
                    assert area.spaces.active.region_3d.view_perspective == 'PERSP'
                    assert len(bpy.data.cameras) == camera_count
                    assert not any(obj.get(AutoCamera.CUSTOM_KEY) for obj in scene.objects)
                    assert original_render == (scene.render.resolution_x, scene.render.resolution_y,
                                               scene.render.resolution_percentage, scene.render.filepath)

    empty = bpy.data.objects.new('Framing region', None)
    scene.collection.objects.link(empty)
    empty.empty_display_type = 'CUBE'
    empty.empty_display_size = 2
    empty.parent = subject
    empty.location = (1, 2, 3)
    empty.rotation_euler.z = 0.5
    empty.scale = (0.5, 2, 1)
    bpy.context.view_layer.update()
    points = provider.get_framing_points([subject, empty], bpy.context.evaluated_depsgraph_get())
    inverse = empty.matrix_world.inverted()
    assert len(points) == 8
    for point in points:
        assert all(abs(abs(v) - 2) < 1e-4 for v in inverse @ point)
    settings.shot_angle_list = angles
    manager = Manager(area_for_tests(), [subject, empty], settings)
    manager.prepare()
    for elevation, orbit in angles:
        manager.camera_controller.place_camera(elevation, orbit)
        bpy.context.view_layer.update()
        for point in points:
            ndc = world_to_camera_view(scene, manager.camera_controller.camera_obj, point)
            assert 0 <= ndc.x <= 1 and 0 <= ndc.y <= 1
    manager.cleanup()

    # 準備に失敗してもシーンを復元し、その撮影で作ったオブジェクトだけを削除する。
    original_camera[AutoCamera.CUSTOM_KEY] = True
    unsupported = bpy.data.objects.new('Non-geometry empty', None)
    scene.collection.objects.link(unsupported)
    area = area_for_tests()
    manager = Manager(area, [unsupported], settings)
    try:
        manager.prepare()
    except ValueError:
        manager.cleanup()
    else:
        raise AssertionError('形状を持たない対象ではエラーになる必要があります')
    assert scene.camera == original_camera
    assert original_camera.name in scene.objects
    assert len(bpy.data.cameras) == camera_count
    assert area.spaces.active.overlay.show_overlays is False
    del original_camera[AutoCamera.CUSTOM_KEY]

assert solve([(1, 0, -5)], 1, 1) == 6
assert solve([(1, 0, -5)], 1, 1, 0.5) >= 5.1
try:
    solve([], 1, 1)
except ValueError:
    pass
else:
    raise AssertionError('頂点がない場合はエラーになる必要があります')
print(f'検証成功: {checks}点の投影位置・フレーミング・変形後の形状・Empty Cube・後片付け')
