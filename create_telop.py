from PIL import Image
# import cv2
import numpy as np
import os
import shutil
import budoux
from helper import create_index, east_asian_len, outlined_text_img, get_yukkuri_dir
from my_helper import MyList
from typing import Dict, Tuple
from get_project_dir import get_project_dir
from get_script_list import get_script_list

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
    font_size = 40
    text_position = (W * 0.5, H * 0.9)

    # draw_img.textsize(text, ImageFont.truetype(font, font_size))

    colors: Dict[str, Tuple[int, int, int]] = {
        "れ": (255, 0, 0),
        "ま": (255, 255, 100)
    }
    font_color = colors[character]
    inner_color = (0, 0, 0)
    outer_color = (255, 255, 255)
    outer_width = 3
    inner_width = 3
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


# def n_line_text(text: str, n: int):
#     # len_text = len(text)
#     # parsed = parser.parse(text)
#     # pre_line1, pre_line2 = "".join(parsed[:0]), "".join(parsed[0:])
#     # for i in range(len(parsed)):
#     #     line1 = "".join(parsed[:i])
#     #     line2 = "".join(parsed[i:])
#     #     if east_asian_len(line1) > east_asian_len(line2):
#     #         if (east_asian_len(line1)-east_asian_len(line2) <= east_asian_len(pre_line2)-east_asian_len(pre_line1)):
#     #             return line1+"\n"+line2
#     #         else:
#     #             return pre_line1+"\n"+pre_line2
#     #     pre_line1, pre_line2 = line1, line2
#     return text


separate_char = "｜"  # 改行の目印となる文字
max_line_len = 30  # 1行の最大文字数
max_line_num = 3  # 最大の行数


class Script():
    def __init__(self, script: str) -> None:
        self.character = script[0]
        self.text_lines = MyList(script[2:].split(separate_char))

    def arrange_text(self):
        "テキストをテロップに合わせて調整する"
        new_lines: MyList[str] = MyList()
        for text in self.text_lines:
            new_lines += self.split_line(text)
        self.text_lines = new_lines

    def split_line(self, text: str):
        "テキストの改行関係を処理する"
        text_length = east_asian_len(text)
        line_num = int(text_length // max_line_len + 1)  # 行数
        if line_num == 1:
            return MyList([text])
        parsed_list = MyList(parser.parse(text))
        parsed_len = parsed_list.map(east_asian_len)
        parsed_accumulate_len: MyList[float] = MyList()
        sum = 0
        for length in parsed_len:
            sum += length
            parsed_accumulate_len.append(sum)
        one_line_len = text_length / line_num
        split_index_list: MyList[int] = MyList()  # 分割するindex
        for i in range(1, line_num):
            near_one_line_len_list = parsed_accumulate_len.map(lambda x: abs(x - one_line_len*i))
            split_index_list.append(near_one_line_len_list.index(min(near_one_line_len_list)))
        new_list: MyList[str] = MyList()
        text_to_add = ""
        for i, parsed_text in enumerate(parsed_list):
            text_to_add += parsed_text
            if (i in split_index_list) or (i == parsed_list.length()-1):
                new_list.append(text_to_add)
                text_to_add = ""
        return new_list

    def split_class(self):
        """
        セリフが4行以上なら2つ以上の画像に分割する\n
        7行以上になる場合については想定していないのでそのようなことがあったら修正しよう
        """
        n = self.text_lines.length()
        if n <= max_line_num:
            return self
        n_mod3 = n % 3
        img_count = (n-1) // 3 + 1

        def two_img_line_nums(n_mod3: int):
            if n_mod3 == 1:
                return MyList([2, 2])
            elif n_mod3 == 2:
                return MyList([3, 2])
            elif n_mod3 == 0:
                return MyList([3, 3])
            raise Exception()
        img_line_nums = MyList.fill(3, img_count-2) + two_img_line_nums(n_mod3)
        new_text_lines = self.text_lines.divide_inside(*img_line_nums).map(lambda x: self.character + "：" + x.join("｜"))
        return new_text_lines.map(Script)

    def to_plain_text(self):
        "コンストラクタの引数に入れる文字列と同じ形式のテキストを返す"
        return self.character + "：" + self.text_lines.join()


def export_script(script_list: MyList[str]):
    """編集後の台本を出力"""
    yukkuri_dir = get_yukkuri_dir(__file__)
    with open(f"{yukkuri_dir}/auto_yukkuri/fixed_script.txt", "w") as f:
        f.write(script_list.join("\n"))


def create_all_telop(script_list: MyList[str], project_dir):
    path = project_dir+"/字幕"
    shutil.rmtree(path)
    os.mkdir(path)

    scripts: MyList[Script] = script_list.map(Script)
    scripts.map(lambda x: x.arrange_text())
    arranged_scripts = scripts.map(lambda x: x.split_class())
    flatten_scripts: MyList[Script] = arranged_scripts.flatten()

    export_script(flatten_scripts.map(lambda x: x.to_plain_text()))

    for i, script in enumerate(flatten_scripts):
        text = script.text_lines.join("\n")
        index = create_index(i+1, 3)
        character = script.character
        create_telop(text, index, character, project_dir)

    # script_dicts_copy = script_dicts[:]
    # inserted = 0  # 挿入された回数を記録する
    # for script_dict in script_dicts_copy:
    #     if east_asian_len(script_dict["text"]) > max_line_len * max_line_num:

    # for i, script in enumerate(script_list):
    #     # 台本データからキャラの部分を除いたものを抽出する
    #     text = script[2:]
    #     max_line_len = 30  # 1行の最大文字数
    #     max_line_num = 3  # 最大の行数
    #     separate_char = "｜"  # 改行の目印となる文字
    #     # 文字数が2行の最大数より大きければエラー
    #     if east_asian_len(text) > max_line_len * max_line_num:
    #         raise ValueError(f"「{text}」は長すぎます")
    #     # 改行の目印が含まれているときとそうでないときで区別
    #     if separate_char in text:
    #         texts = MyList(text.split(separate_char))
    #         over_texts = texts.filter(lambda x: east_asian_len(x) <= max_line_len)  # 1行の文字数がオーバーしているテキストを収納
    #         # 文字数がオーバーしているとエラー
    #         if not over_texts:
    #             raise ValueError(f"「{over_texts.join('')}」は長すぎます")
    #         else:
    #             text = re.sub(r"\s*"+separate_char+r"\s*", "\n", text)
    #     # 文字数が1行の最大数より大きければ良きところで改行する
    #     elif east_asian_len(text) > max_line_len:
    #         text = two_line_text(text)
    #     # キャラクターを取得
    #     character = script[0]
    #     # indexを取得
    #     index = create_index(i+1, 3)
    #     # print(text)
    #     create_telop(text, index, character, project_dir)


if __name__ == "__main__":
    # 動画プロジェクトのディレクトリ
    project_dir = get_project_dir(__file__)
    # セリフ1つ1つを配列にしたもの
    script_list = get_script_list(project_dir)
    # print(script_list)
    create_all_telop(script_list, project_dir)
