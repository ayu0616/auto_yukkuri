from PIL import Image
# import cv2
import numpy as np
import os
import shutil
import budoux
from helper import create_index, east_asian_len, outlined_text_img
from my_helper import MyList
from typing import List
from get_project_dir import get_project_dir
from get_script_list import get_script_list
import re

parser = budoux.load_default_japanese_parser()

W = 1920
H = 1080

# テロップ背景の黒半透明の長方形
rect_size = 227  # 長方形のサイズ
bg_img = np.full((H, W, 4), 0, dtype=np.uint8)
for row in bg_img[-rect_size:]:
    row[0:] = np.array([[0, 0, 0, 127] for _ in range(W)])  # noqa


def create_telop(text, index, character, project_dir):
    img_dir = project_dir + "/字幕"
    img_title = f"{index}_{text}.png".replace("\n", "")
    img_path = f"{img_dir}/{img_title}"
    # img = np.full((H, W, 4), 0, dtype=np.uint8)  # 透明度情報を追加したので保存形式はpngじゃないといけない（jpegはだめ）
    # img = Image.fromarray(img)

    # # 透過ボックス作成
    # a = Image.new('RGBA', (W, H))
    # draw_img = ImageDraw.Draw(a)

    font = '/Users/OgawaAyumu/Library/Fonts/TanukiMagic.ttf'
    font_size = 60
    text_position = (W * 0.5, H * 0.9)

    # draw_img.textsize(text, ImageFont.truetype(font, font_size))

    colors = {
        "れ": (255, 0, 0),
        "ま": (255, 255, 100)
    }
    font_color = colors[character]
    inner_color = (0, 0, 0)
    outer_color = (255, 255, 255)
    outer_width = 4
    inner_width = 4
    # space_size = (outer_stroke + inner_stroke) * 3 / 4

    # # 文字入れ・外側の縁用
    # draw_img.multiline_text(
    #     text_position,
    #     text,
    #     fill=outer_color,
    #     font=ImageFont.truetype(font, font_size),
    #     anchor='mm',
    #     stroke_width=outer_stroke,
    #     stroke_fill=outer_color,
    #     align="center",
    #     spacing=0
    # )
    # # 文字入れ・内側の縁用
    # draw_img.multiline_text(
    #     text_position,
    #     text,
    #     fill=font_color,
    #     font=ImageFont.truetype(font, font_size),
    #     anchor='mm',
    #     stroke_width=inner_stroke,
    #     stroke_fill=inner_color,
    #     align="center",
    #     spacing=space_size
    # )

    # 合成
    out_img1 = Image.fromarray(bg_img)
    # out_img2 = Image.alpha_composite(img, a)
    out_img2 = outlined_text_img(text, font, font_size, text_position, font_color, inner_color, inner_width, outer_color, outer_width)
    out_img = Image.alpha_composite(out_img1, out_img2)

    # 保存
    out_img.save(img_path)


def two_line_text(text: str):
    # len_text = len(text)
    parsed = parser.parse(text)
    pre_line1, pre_line2 = "".join(parsed[:0]), "".join(parsed[0:])
    for i in range(len(parsed)):
        line1 = "".join(parsed[:i])
        line2 = "".join(parsed[i:])
        if east_asian_len(line1) > east_asian_len(line2):
            if (east_asian_len(line1)-east_asian_len(line2) <= east_asian_len(pre_line2)-east_asian_len(pre_line1)):
                return line1+"\n"+line2
            else:
                return pre_line1+"\n"+pre_line2
        pre_line1, pre_line2 = line1, line2


def create_all_telop(script_list: List[str], project_dir):
    path = project_dir+"/字幕"
    shutil.rmtree(path)
    os.mkdir(path)
    for i, script in enumerate(script_list):
        # 台本データからキャラの部分を除いたものを抽出する
        text = script[2:]

        # 1行の最大文字数
        max_line_len = 30
        # 改行の目印となる文字
        sepalate_char = "｜"
        # 文字数が2行の最大数より大きければエラー
        if east_asian_len(text) > max_line_len * 2:
            raise TypeError(f"「{text}」は長すぎます")
        # 改行の目印が含まれているときとそうでないときで区別
        if sepalate_char in text:
            texts = MyList(text.split(sepalate_char))
            over_texts = texts.filter(lambda x: east_asian_len(x) <= max_line_len)  # 1行の文字数がオーバーしているテキストを収納
            # 文字数がオーバーしているとエラー
            if not over_texts:
                raise TypeError(f"「{over_texts.join('')}」は長すぎます")
            else:
                text = re.sub(r"\s*"+sepalate_char+r"\s*", "\n", text)
        # 文字数が1行の最大数より大きければ良きところで改行する
        elif east_asian_len(text) > max_line_len:
            text = two_line_text(text)
        # キャラクターを取得
        character = script[0]
        # indexを取得
        index = create_index(i+1, 3)
        # print(text)
        create_telop(text, index, character, project_dir)


if __name__ == "__main__":
    # 動画プロジェクトのディレクトリ
    project_dir = get_project_dir(__file__)
    # セリフ1つ1つを配列にしたもの
    script_list = get_script_list(project_dir)
    # print(script_list)
    create_all_telop(script_list, project_dir)
