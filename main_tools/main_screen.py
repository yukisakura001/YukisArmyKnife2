# -*- coding: utf-8 -*-
"""
メイン画面モジュール

claunchのようなランチャーアプリケーションのメイン画面
"""

import tkinter as tk

from .gui_runcher_window import TrayApplication


def my_custom_widgets(app: TrayApplication, root: tk.Tk):
    """
    カスタムウィジェットを作成（ランチャーUI）

    Args:
        app: TrayApplicationインスタンス
        root: tkinter.Tkのルートウィンドウ
    """
    try:
        # ツールマネージャーをインポート
        from tools import tool_manager

        # ランチャーUIを作成
        from .launcher import LauncherUI

        launcher = LauncherUI(root, tool_manager, app)

    except ImportError as e:
        # モジュールが見つからない場合のエラーメッセージ
        error_label = tk.Label(
            root,
            text=f"必要なモジュールがインポートできません:\n{e}",
            fg="red",
            pady=20,
        )
        error_label.pack()
    except Exception as e:
        # その他のエラー
        error_label = tk.Label(
            root, text=f"ランチャーの初期化に失敗しました:\n{e}", fg="red", pady=20
        )
        error_label.pack()
