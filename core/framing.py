"""基準点とカメラの向きを固定した透視投影のフレーミング計算。

次の記事で解説されている、画面の端に対する制約式を参考にしています。
https://zenn.dev/reality_tech/articles/camera-auto-framing-algorithm
基準点を画面中央に保ち、すべての周回撮影で同じ中心を使います。
"""

import math


def required_distance(points, horizontal_slope, vertical_slope,
                      margin_scale=1.0, clip_start=0.1):
    """カメラ基準の座標（右・上・前方）から、必要な最小距離を返す。

    各点の横方向の投影位置は x / ((depth + distance) * horizontal_slope)。
    余白倍率が1.3なら、画面中央を0、両端を±1とした投影位置を±1/1.3以内に収める。
    1未満では意図的な見切れを許容するが、頂点は近クリップ面より手前に置かない。
    """
    if not all(math.isfinite(v) and v > 0 for v in
               (horizontal_slope, vertical_slope, margin_scale, clip_start)):
        raise ValueError("画角・余白・クリップ距離は正の有限値が必要です")
    distance = 0.0
    found = False
    for right, up, depth in points:
        if not all(math.isfinite(v) for v in (right, up, depth)):
            raise ValueError("撮影対象の座標が不正です")
        found = True
        distance = max(distance,
                       abs(right) * margin_scale / horizontal_slope - depth,
                       abs(up) * margin_scale / vertical_slope - depth,
                       clip_start * 1.01 - depth)
    if not found:
        raise ValueError("撮影範囲を取得できません")
    return distance
