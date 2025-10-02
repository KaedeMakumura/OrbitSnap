import datetime
import bpy
from dataclasses import dataclass, field
from .property_group import ORBITSNAP_PR_MainSettings

@dataclass
class CaptureSettings:
    """スクリーンショット用の各種設定値

    Attributes:
        datetime: 撮影日時
        resolution_x: 横解像度
        resolution_y: 縦解像度
        sensor_width: センササイズ(mm)
        focal_length: 焦点距離(mm)
        margin_scale: 余白調整
        shot_angle_list: 撮影角度リスト
        w_datetime: スクリーンショットに日時を表示するか
        w_filename: スクリーンショットにファイル名を表示するか
        w_focal_length: スクリーンショットに焦点距離を表示するか
        w_orbit_angle: スクリーンショットに水平角度を表示するか
        w_elevation_angle: スクリーンショットに仰角を表示するか
        w_note: スクリーンショットに備考を表示するか
        note: スクリーンショットに表示する備考のテキスト
    """

    datetime: datetime
    directory: str
    quality: str = 'middle'
    resolution_x: int = 1280
    resolution_y: int = 720
    sensor_width: float = 36.0
    sensor_height: float = 24.0
    focal_length: float = 50
    margin_scale: float = 1.2
    shot_angle_list: list[list[int]] = field(default_factory=list)
    w_datetime: bool = False
    w_filename: bool = False
    w_focal_length: bool = False
    w_orbit_angle: bool = False
    w_elevation_angle: bool = False
    w_note: bool = False
    open_folder_after_capture:bool = False
    note: str = ""

    @classmethod
    def from_props(cls, props: ORBITSNAP_PR_MainSettings):
        """blenderのプロパティから設定クラスを生成するファクトリメソッド

        Args:
            props (ORBITSNAP_PR_MainSettings): プロパティグループ

        Returns:
            CaptureSettings: 設定クラスのインスタンス
        """
        # フォルダの絶対パス化
        save_dir = props.directory or "//"
        abs_save_dir = bpy.path.abspath(save_dir)

        # 画質の設定
        quality = props.quality
        if props.quality == 'high':
            resolution_x = 1920
            resolution_y = 1080
        elif props.quality == 'middle':
            resolution_x = 1280
            resolution_y = 720
        elif props.quality == 'low':
            resolution_x = 854
            resolution_y = 480

        # 仰角リストを初期化

        elevation_angles = []
        if props.use_angle_0:   elevation_angles.append(0)
        if props.use_angle_30:  elevation_angles.append(30)
        if props.use_angle_45:  elevation_angles.append(45)
        if props.use_angle_60:  elevation_angles.append(60)
        if props.use_angle_m30: elevation_angles.append(-30)
        if props.use_angle_m45: elevation_angles.append(-45)
        if props.use_angle_m60: elevation_angles.append(-60)

        elevation_angles = elevation_angles or [0]

        # 撮影角度リストを初期化
        orbit_step = int(props.orbit_step)
        shot_angle_list = []

        for x_angle in elevation_angles:
            z_angles = [i * orbit_step for i in range(360 // orbit_step)]

            for z_angle in z_angles:
                shot_angle_list.append([x_angle, z_angle])

        return cls(
            datetime=datetime.datetime.now(),
            directory=abs_save_dir,
            quality=quality,
            resolution_x=resolution_x,
            resolution_y=resolution_y,
            focal_length=props.focal_length,
            margin_scale=props.margin_scale,
            shot_angle_list=shot_angle_list,
            w_datetime=props.w_datetime,
            w_filename=props.w_filename,
            w_focal_length=props.w_focal_length,
            w_orbit_angle=props.w_orbit_angle,
            w_elevation_angle=props.w_elevation_angle,
            w_note=props.w_note,
            note=props.note,
            open_folder_after_capture=props.open_folder_after_capture,
        )
