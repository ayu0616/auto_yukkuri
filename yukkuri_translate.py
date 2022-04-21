import re
from my_helper import MyList


def exclude_pattern(word: str, *excludes: str):
    exclude_list = MyList(excludes)
    # 除外したい単語がなかったらそのままreturn
    if not exclude_list:
        return word
    # 除外したい単語に変数wordが含まれていなかったらエラー
    for exclude in exclude_list:
        if word not in exclude:
            raise Exception(f'"{exclude}"は{word}を含んでいません')

    exclude_split = exclude_list.map(lambda x: MyList(x.split(word)))
    or_sign = "|"
    exclude_before = exclude_split.map(lambda x: x[0]).filter(lambda x: x)
    exclude_after = exclude_split.map(lambda x: x[1]).filter(lambda x: x)
    pattern = word
    if exclude_before:
        pattern = f"(?<!{exclude_before.join(or_sign)}){pattern}"
    if exclude_after:
        pattern = f"{pattern}(?!{exclude_after.join(or_sign)})"
    return pattern


def yukkuri_translate(string: str):
    "ゆっくりで読み間違えがある単語を変換"
    trans_dict = {
        r"(\s*[｜|]\s*)": "。",
        r"([!?！？]+)": r"\1。",
        r"(は)後(で)": r"\1あと\2",
        r"〜": "ー",
        "一度": "いちど",
        "うp主": "うぷ主",
        exclude_pattern("米", "タイ米", "米国", "雑穀米", "米価"): "こめ",
        "皆さん": "みなさん",
        "港町": "みなとまち",
        "幕領": "ばくりょう",
        r"行って(おきたい|いない)": r"いって\1",
        "小難しい": "こむずかしい",
        "理想形": "理想けい",
        r"得(しない|する)": r"とく\1",
        "豊国神社": "ほうこく神社",
        "豊臣秀吉": "とよとみひでよし",
        "百間堂": "ひゃっけんどう",
        r"敵(う|わない)": r"かな\1",
        "では": "でわ",
        "竹串": "たけぐし",
        "弥山": "みせん",
        "多すぎ": "おおすぎ",
        r"奉([らりるれろ])": r"たてまつ\1",
        "七佛": "しちぶつ",
        "西國寺": "さいこくじ",
        "海龍寺": "かいりゅうじ",
        r"主(として)": r"しゅ\1"
    }
    for key, value in trans_dict.items():
        pattern = re.compile(key)
        string = pattern.sub(value, string)
    return string
