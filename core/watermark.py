import bpy
from ..properties.capture_settings import CaptureSettings
from ..utils.utils import get_font_path


from PIL import Image, ImageDraw, ImageFont


class Watermark:
    settings: CaptureSettings
    font: ImageFont
    x: int = 20
    y: int = 10
    outline_color = (0, 0, 0, 200)
    fill_color = (255, 255, 255, 200)
    font_size = 32

    def __init__(self, settings: CaptureSettings):
        self.settings = settings

        # フォントパス
        font_path = get_font_path()
        self.font = ImageFont.truetype(font_path, self.font_size)

    def draw(self, filepath:str, orbit_angle:int, elevation_angle:int):
        """_summary_

        Args:
            filepath (str): 情報を書き込みたいスクリーンショットのパス
            orbit_angle (int):水平角
            elevation_angle (int): 仰角

            水平角と仰角以外はどのショットでも固定なので設定から取得｡
            水平角と仰角は引数で渡す｡
        """
        # 書き込みテキストの作成
        text = self.generate_text(orbit_angle, elevation_angle)

        if not text:
            return

        # --- Pillowでテキスト描き込み ---
        # 画像を開く
        try:
            img = Image.open(filepath).convert("RGBA")
        except FileNotFoundError as e:
            raise e

        # 透明レイヤーを作成
        txt_layer = Image.new("RGBA", img.size, (255,255,255,0))
        draw = ImageDraw.Draw(txt_layer)

        # --- 縁取りを描く ---
        draw.multiline_text((self.x, self.y), text, font=self.font, fill=self.fill_color, stroke_width=2, stroke_fill=self.outline_color)

        # レイヤー合成
        combined = Image.alpha_composite(img, txt_layer)

        # 保存
        combined.save(filepath)


    def generate_text(self, orbit_angle: int, elevation_angle: int) -> str:
        lines = []
        if self.settings.w_datetime:
            lines.append(self.settings.datetime.strftime("%Y-%m-%d %H:%M:%S"))
        if self.settings.w_filename:
            lines.append(bpy.path.basename(bpy.data.filepath))
        if self.settings.w_focal_length:
            lines.append(f"{self.settings.focal_length:.1f}mm")
        if self.settings.w_orbit_angle:
            lines.append(f"Orbit Angle: {orbit_angle}°")
        if self.settings.w_elevation_angle:
            lines.append(f"Elevation Angle: {elevation_angle}°")
        if self.settings.w_note:
            lines.append(self.settings.note)
        return "\n".join(lines)


