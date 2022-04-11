from helper import outlined_text_img, require_input
from my_helper import cut_by_content

W, H = 1920, 1080
text = require_input("サムネの行き先を入力")
font_family = "/System/Library/Fonts/ヒラギノ丸ゴ ProN W4.ttc"
red = (255, 0, 0)
white = (255, 255, 255)

text_img = outlined_text_img(
    text,
    font_family,
    font_size=250,
    text_position=(W/2, H/2),
    font_color=red,
    inner_color=white,
    inner_width=15,
    outer_color=red,
    outer_width=5
)
save_path = f"./output/{text}.png"
text_img.save(save_path)
cut_by_content(save_path)
