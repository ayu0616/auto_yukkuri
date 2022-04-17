from tkinter import filedialog, Tk
import os
from helper import get_yukkuri_dir


def get_project_dir(current_dir: str = __file__):
    # ダイアログ用のルートウィンドウの作成
    root = Tk()
    # ウィンドウサイズを0にする（Windows用の設定）
    root.geometry("0x0")
    # ウィンドウのタイトルバーを消す（Windows用の設定）
    # root.overrideredirect(1)
    # ウィンドウを非表示に
    root.withdraw()
    root.update()
    # ダイアログを前面に
    root.lift()
    root.focus_force()
    # 動画プロジェクトのディレクトリ
    yukkuri_dir = get_yukkuri_dir(current_dir)
    project_dir = filedialog.askdirectory(initialdir=yukkuri_dir)
    root.update()
    # ディレクトリが選択されなかったらエラーを発生させる
    if not project_dir:
        raise Exception("ディレクトリが選択されていません")
    return project_dir


if __name__ == "__main__":
    print(get_project_dir(os.path.dirname(__file__)))
