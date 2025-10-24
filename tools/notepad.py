# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import scrolledtext


def create_notepad_app():
    """シンプルメモ帳アプリ起動関数"""
    window = tk.Toplevel()
    window.title("メモ帳ツール")
    window.geometry("500x400")

    # タイトルラベル
    tk.Label(
        window,
        text="シンプルメモ帳",
        font=("Arial", 14, "bold"),
        pady=10,
    ).pack()

    # テキストエリア
    text_area = scrolledtext.ScrolledText(
        window,
        wrap=tk.WORD,
        width=60,
        height=20,
        font=("Arial", 10),
    )
    text_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    # ボタン用フレーム
    button_frame = tk.Frame(window)
    button_frame.pack(pady=5)

    # クリア関数
    def clear_text():
        text_area.delete(1.0, tk.END)

    # クリアボタン
    tk.Button(
        button_frame,
        text="クリア",
        command=clear_text,
        width=15,
        bg="lightyellow",
    ).pack(side=tk.LEFT, padx=5)

    # 閉じるボタン
    tk.Button(
        button_frame,
        text="閉じる",
        command=window.destroy,
        width=15,
        bg="salmon",
    ).pack(side=tk.LEFT, padx=5)

    return window
