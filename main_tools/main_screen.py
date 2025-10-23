"""
gui_runcher_window.pyの使用例
ウィジェットを外部で定義する方法を示すサンプル
"""

import tkinter as tk

from .gui_runcher_window import TrayApplication


def my_custom_widgets(app: TrayApplication, root: tk.Tk):
    """
    カスタムウィジェットを作成する関数

    Args:
        app: TrayApplicationのインスタンス
        root: tkinter.Tkのルートウィンドウ
    """
    # タイトルラベル
    tk.Label(
        root,
        text="カスタムウィジェット例",
        font=("Arial", 16, "bold"),
        pady=10,
    ).pack()

    # 説明文
    tk.Label(
        root,
        text="このウィンドウは外部で定義されたウィジェットです",
        pady=5,
    ).pack()

    # トレイへ隠すボタン（app.hide_to_trayメソッドを使用）
    tk.Button(
        root, text="トレイに隠す", command=app.hide_to_tray, bg="lightblue", width=20
    ).pack(pady=5)

    # カウンター機能の追加
    counter = {"value": 0}

    def increment():
        counter["value"] += 1
        label_counter.config(text=f"カウント: {counter['value']}")

    label_counter = tk.Label(root, text="カウント: 0", pady=5)
    label_counter.pack()

    tk.Button(root, text="カウントアップ", command=increment, width=20).pack(pady=5)

    # 終了ボタン（app.quit_appメソッドを使用）
    tk.Button(root, text="終了", command=app.quit_app, bg="salmon", width=20).pack(
        pady=10
    )
