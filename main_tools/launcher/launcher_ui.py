# -*- coding: utf-8 -*-
"""
ランチャーUIモジュール

責務:
- ランチャー全体の初期化と統合
- 各マネージャー（tab, grid, slot, menu）の統合
- ウィンドウとノートブックの管理

ロジック:
- 各マネージャーを初期化して統合
- menu_managerでメニューバーを作成（理由: メニュー管理はmenu_managerの責務）
- tab_managerでタブを作成（理由: タブ管理はtab_managerの責務）
- grid_managerでウィンドウサイズを調整（理由: サイズ管理はgrid_managerの責務）
"""

import tkinter as tk
from tkinter import ttk
from typing import Any

from .config import LauncherConfig
from .grid_manager import GridManager
from .menu_manager import MenuManager
from .slot_manager import SlotManager
from .slot_ui_builder import SlotUIBuilder
from .tab_manager import TabManager

# スロットのサイズ定数
SLOT_WIDTH = 72
SLOT_HEIGHT = 64
SLOT_PADDING = 1


class LauncherUI:
    """ランチャーのUIクラス"""

    def __init__(self, root: tk.Tk, tool_manager: Any = None, app: Any = None):
        """
        初期化

        Args:
            root: tkinterのルートウィンドウ
                  - ランチャーUIのベースとなるウィンドウ
            tool_manager: ツールマネージャーモジュール
                         - yakプロジェクト内のツールを管理
            app: TrayApplicationインスタンス
                 - トレイアイコンとウィンドウの表示/非表示を制御
        """
        self.root = root
        self.tool_manager = tool_manager
        self.app = app
        # configを読み込み（理由: 設定の管理はconfigの責務）
        self.config = LauncherConfig()

        # アイコンのキャッシュ
        self.icon_cache: dict[str, Any] = {}

        # 保存されているグリッドサイズを読み込み
        saved_cols, saved_rows = self.config.get_grid_size()
        self.num_cols = saved_cols
        self.num_rows = saved_rows
        self.slots_per_tab = self.num_cols * self.num_rows

        # ノートブック（タブ）
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

        # タブのリスト
        self.tabs: list[tk.Frame] = []

        # 各マネージャーの初期化
        # 理由: 各機能を分離して責務を明確にするため
        self.grid_manager = GridManager(self)
        self.tab_manager = TabManager(self)
        self.slot_ui_builder = SlotUIBuilder(self)
        self.menu_manager = MenuManager(self)
        self.slot_manager = SlotManager(self)

        # メニューバーを作成
        # 理由: メニューの管理はmenu_managerの責務
        self.menu_manager.create_menubar()

        # タブの作成
        # 理由: タブの管理はtab_managerの責務
        self.tab_manager.create_tabs()

        # マウスホイールイベントのバインド
        self.bind_mousewheel()

        # ウィンドウサイズを可変に設定
        # self.root.resizable(True, True)

        # ウィンドウサイズをグリッドにぴったり合わせる
        # 理由: サイズ調整はgrid_managerの責務
        self.grid_manager.adjust_window_size()

        # ウィンドウサイズ変更イベントをバインド
        # 理由: リサイズ処理はgrid_managerの責務
        self.root.bind("<Configure>", self.grid_manager.on_window_resize)
        self._resize_timer = None

    def refresh_slot(self, tab_index: int, row: int, col: int) -> None:
        """
        スロットのUIを更新

        Args:
            tab_index: タブインデックス
            row: 行
            col: 列

        理由: slot_ui_builderのrefresh_slotを呼び出す
              （スロットUI更新の責務はslot_ui_builderにあるため）
        """
        self.slot_ui_builder.refresh_slot(tab_index, row, col)

    def bind_mousewheel(self) -> None:
        """
        マウスホイールイベントをバインド

        処理:
        - マウスホイールでタブを切り替え
        - 上スクロールで前のタブへ、下スクロールで次のタブへ
        """

        def on_mousewheel(event: tk.Event) -> None:
            current = self.notebook.index("current")
            tab_count = self.config.get_tab_count()

            if event.delta > 0:  # 上にスクロール（前のタブへ）
                new_index = max(0, current - 1)
            else:  # 下にスクロール（次のタブへ）
                new_index = min(tab_count - 1, current + 1)

            # 端に到達していたら何もしない
            if new_index != current:
                self.notebook.select(new_index)

        # マウスホイールイベントをバインド（Windows専用）
        self.root.bind_all("<MouseWheel>", on_mousewheel)
