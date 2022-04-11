import math
from typing import Tuple, Union
import unicodedata
import tkinter.simpledialog as simpledialog
from tkinter import Tk
from PIL import Image, ImageFont, ImageDraw
import numpy as np


Number = Union[int, float]


def create_index(i: int, digit: int):
    if math.log10(i) > digit+1:
        return str(i)
    index = str(i)
    for _ in range(digit-1):
        index = "0"+index
    return index[-1*digit:]


def east_asian_len(text: str):
    "全角文字を1、半角文字を0.5として文字数を返す"
    count = 0.0
    for c in text:
        if unicodedata.east_asian_width(c) in 'FWA':
            count += 1.0
        else:
            count += 0.5
    return count


def require_input(ask_text: str):
    "tkinterで入力を要求し、入力された値を返す"
    # ダイアログ用のルートウィンドウの作成
    root = Tk()
    # ウィンドウを非表示に
    root.withdraw()

    inputstr = simpledialog.askstring("入力欄", ask_text)
    # 先頭が空白文字ならそれを削除する
    while inputstr[0] == " ":
        inputstr = inputstr[1:]
    return inputstr


def outlined_text_img(
    text: str,
    font_family: str,
    font_size: int,
    text_position: Tuple[Number, Number],
    font_color: Tuple[int, int, int],
    inner_color: Tuple[int, int, int],
    inner_width: Number,
    outer_color: Tuple[int, int, int] = None,
    outer_width: Number = 0,
):
    """
    外枠があるテキスト画像を生成する
    解像度は(1920, 1080)
    引数の"outer_〜"に指定がなければ1重、指定があれば2重
    """
    W = 1920
    H = 1080
    inner_stroke = inner_width
    outer_stroke = inner_width + outer_width
    img = np.full((H, W, 4), 0, dtype=np.uint8)  # 透明度情報を追加したので保存形式はpngじゃないといけない（jpegはだめ）
    img = Image.fromarray(img)

    # 透過ボックス作成
    a = Image.new('RGBA', (W, H))
    draw_img = ImageDraw.Draw(a)

    draw_img.textsize(text, ImageFont.truetype(font_family, font_size))

    space_size = (outer_stroke + inner_stroke) * 3 / 4

    # 文字入れ・外側の縁用
    if bool(outer_color) and bool(outer_stroke):
        draw_img.multiline_text(
            text_position,
            text,
            fill=outer_color,
            font=ImageFont.truetype(font_family, font_size),
            anchor='mm',
            stroke_width=outer_stroke,
            stroke_fill=outer_color,
            align="center",
            spacing=0
        )
    # 文字入れ・内側の縁用
    draw_img.multiline_text(
        text_position,
        text,
        fill=font_color,
        font=ImageFont.truetype(font_family, font_size),
        anchor='mm',
        stroke_width=inner_stroke,
        stroke_fill=inner_color,
        align="center",
        spacing=space_size
    )

    out_img = Image.alpha_composite(img, a)
    return out_img
