# -*- coding: utf-8 -*-
import tkinter as tk

from tools import get_all_tools, launch_tool

from .gui_runcher_window import TrayApplication


def my_custom_widgets(app: TrayApplication, root: tk.Tk):
    """
    カスタムウィジェットを作成

    Args:
        app: TrayApplicationインスタンス
        root: tkinter.Tkのルートウィンドウ
    """
    # タイトルラベル
    tk.Label(
        root,
        text="Yak2 ツールランチャー",
        font=("Arial", 16, "bold"),
        pady=10,
    ).pack()

    # 説明文
    tk.Label(
        root,
        text="使いたいツールを選んでください",
        pady=5,
    ).pack()

    # ツールボタンセクション
    tk.Label(
        root,
        text="ミニツール",
        font=("Arial", 12, "bold"),
        pady=10,
    ).pack()

    # ツールボタン用フレーム
    tool_frame = tk.Frame(root)
    tool_frame.pack(pady=10)

    # 各ツール用のボタンを動的に生成
    tools = get_all_tools()
    for i, tool in enumerate(tools):
        row = i // 2
        col = i % 2

        def create_launch_command(tool_func):
            return lambda: launch_tool(tool_func)

        btn = tk.Button(
            tool_frame,
            text=f"{tool['name']}\n{tool['description']}",
            command=create_launch_command(tool["function"]),
            bg=tool.get("color", "lightgray"),
            width=20,
            height=3,
        )
        btn.grid(row=row, column=col, padx=5, pady=5)

    # セパレーター
    tk.Frame(root, height=2, bg="gray").pack(fill=tk.X, padx=20, pady=10)

    # システムボタン用フレーム
    system_frame = tk.Frame(root)
    system_frame.pack(pady=5)

    # トレイに隠すボタン（app.hide_to_trayメソッドを使用）
    tk.Button(
        system_frame,
        text="トレイに隠す",
        command=app.hide_to_tray,
        bg="lightblue",
        width=20,
    ).pack(side=tk.LEFT, padx=5)

    # 終了ボタン（app.quit_appメソッドを使用）
    tk.Button(
        system_frame,
        text="終了",
        command=app.quit_app,
        bg="salmon",
        width=20,
    ).pack(side=tk.LEFT, padx=5)
