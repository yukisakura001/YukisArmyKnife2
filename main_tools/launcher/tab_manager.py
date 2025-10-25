# -*- coding: utf-8 -*-
"""
タブ管理モジュール

責務:
- ランチャーのタブ作成と管理
- タブフレームの生成とノートブックへの追加
- タブの再構築処理

ロジック:
- configからタブ情報を取得してタブフレームを作成
- 各タブ内にグリッドを配置するためgrid_managerを呼び出す
"""

import tkinter as tk
from tkinter import ttk
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .launcher_ui import LauncherUI


class TabManager:
    """タブ管理クラス"""

    def __init__(self, launcher_ui: "LauncherUI"):
        """
        初期化

        Args:
            launcher_ui: LauncherUIインスタンス
                        - タブ管理のために必要な情報を保持
        """
        self.launcher_ui = launcher_ui
        self.config = launcher_ui.config
        self.notebook = launcher_ui.notebook
        self.tabs = launcher_ui.tabs

    def create_tabs(self) -> None:
        """
        タブを作成

        処理:
        1. configからタブ数を取得
        2. 各タブのフレームを作成しnotebookに追加
        3. grid_managerを呼び出して各タブ内にグリッドを配置
        """
        tab_count = self.config.get_tab_count()

        for tab_index in range(tab_count):
            tab_name = self.config.get_tab_name(tab_index)

            # タブフレームを作成（改善された色合い）
            tab_frame = tk.Frame(self.notebook, bg="#ffffff")
            self.tabs.append(tab_frame)
            self.notebook.add(tab_frame, text=tab_name)

            # grid_managerを呼び出してグリッドを作成
            # 理由: グリッド構築の責務はgrid_managerにあるため
            self.launcher_ui.grid_manager.create_grid(tab_frame, tab_index)

    def rebuild_tabs(self) -> None:
        """
        すべてのタブを再構築

        処理:
        1. 既存のタブを全て削除
        2. create_tabs()を呼び出して再作成

        用途: タブ編集後やグリッドサイズ変更時に使用
        """
        # アイコンキャッシュをクリア
        self.launcher_ui.icon_cache.clear()

        # すべてのタブを削除
        for tab in self.tabs:
            tab.destroy()
        self.tabs.clear()

        # タブを再作成
        self.create_tabs()
