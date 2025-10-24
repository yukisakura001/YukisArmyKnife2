# -*- coding: utf-8 -*-
import tkinter as tk


def create_counter_app():
    """カウンターアプリ起動関数"""
    window = tk.Toplevel()
    window.title("カウンターアプリ")
    window.geometry("300x200")

    # カウンター変数
    counter = {"value": 0}

    # タイトルラベル
    tk.Label(
        window,
        text="カウンターアプリ",
        font=("Arial", 14, "bold"),
        pady=10,
    ).pack()

    # カウント表示
    label_counter = tk.Label(
        window,
        text="カウント: 0",
        font=("Arial", 12),
        pady=10,
    )
    label_counter.pack()

    # カウントアップ関数
    def increment():
        counter["value"] += 1
        label_counter.config(text=f"カウント: {counter['value']}")

    # リセット関数
    def reset():
        counter["value"] = 0
        label_counter.config(text=f"カウント: {counter['value']}")

    # ボタン用フレーム
    button_frame = tk.Frame(window)
    button_frame.pack(pady=10)

    # カウントアップボタン
    tk.Button(
        button_frame,
        text="カウントアップ",
        command=increment,
        width=15,
        bg="lightgreen",
    ).pack(side=tk.LEFT, padx=5)

    # リセットボタン
    tk.Button(
        button_frame,
        text="リセット",
        command=reset,
        width=15,
        bg="lightblue",
    ).pack(side=tk.LEFT, padx=5)

    # 閉じるボタン
    tk.Button(
        window,
        text="閉じる",
        command=window.destroy,
        width=20,
        bg="salmon",
    ).pack(pady=10)

    return window
