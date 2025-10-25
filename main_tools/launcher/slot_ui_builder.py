# -*- coding: utf-8 -*-
"""
スロットUI構築モジュール

責務:
- ランチャーのスロットUI（フレーム、アイコン、ラベル）の構築
- スロットの表示更新（refresh）

ロジック:
- configからスロットデータを取得
- icon_managerを使ってアイコンを取得
- tkinterウィジェットを作成してイベントをバインド
- 空のスロットと登録済みスロットで異なるUIを作成
"""

import tkinter as tk
from typing import TYPE_CHECKING

from .icon_manager import create_empty_icon, get_icon_for_item

if TYPE_CHECKING:
    from .launcher_ui import LauncherUI

# スロットのサイズ定数
SLOT_WIDTH = 72
SLOT_HEIGHT = 64
SLOT_PADDING = 3


class SlotUIBuilder:
    """スロットUI構築クラス"""

    def __init__(self, launcher_ui: "LauncherUI"):
        """
        初期化

        Args:
            launcher_ui: LauncherUIインスタンス
                        - スロットUI構築に必要な情報を保持
        """
        self.launcher_ui = launcher_ui
        self.config = launcher_ui.config
        self.icon_cache = launcher_ui.icon_cache

    def create_slot(
        self, parent: tk.Frame, tab_index: int, row: int, col: int
    ) -> None:
        """
        スロットを作成

        Args:
            parent: 親フレーム（グリッドフレーム）
            tab_index: タブインデックス
            row: 行
            col: 列

        処理:
        1. configからスロットデータを取得
        2. スロットフレームを作成
        3. データの有無で異なるUI構築：
           - データあり: アイコン + 名前ラベル + 起動イベント
           - データなし: 空アイコン + ヒントラベル
        4. menu_managerを使って右クリックメニューをバインド
        """
        # configからスロットデータを取得
        # 理由: 設定の読み込みはconfigの責務
        slot_data = self.config.get_slot(tab_index, row, col)

        # スロットフレーム（改善された色合い）
        slot_frame = tk.Frame(
            parent,
            width=SLOT_WIDTH,
            height=SLOT_HEIGHT,
            relief=tk.FLAT,
            borderwidth=1,
            bg="#f8f9fa",
            highlightbackground="#dee2e6",
            highlightthickness=1,
        )
        slot_frame.grid(row=row, column=col, padx=SLOT_PADDING, pady=SLOT_PADDING)
        slot_frame.grid_propagate(False)

        # アイコンとラベルを配置
        if slot_data:
            self._create_filled_slot(slot_frame, tab_index, row, col, slot_data)
        else:
            self._create_empty_slot(slot_frame, tab_index, row, col)

        # スロットフレーム自体にも右クリックメニュー
        # 理由: メニュー表示はmenu_managerの責務
        slot_frame.bind(
            "<Button-3>",
            lambda e, t=tab_index, r=row, c=col: self.launcher_ui.menu_manager.show_slot_menu(
                e, t, r, c
            ),
        )

    def _create_filled_slot(
        self,
        slot_frame: tk.Frame,
        tab_index: int,
        row: int,
        col: int,
        slot_data: dict,
    ) -> None:
        """
        データが登録されているスロットのUIを作成

        Args:
            slot_frame: スロットフレーム
            tab_index: タブインデックス
            row: 行
            col: 列
            slot_data: スロットデータ
        """
        # アイコン取得（キャッシュを使用）
        # 理由: 同じアイコンを何度も生成しないためにキャッシュを利用
        cache_key = f"{tab_index}_{row}_{col}"
        if cache_key not in self.icon_cache:
            # icon_managerを呼び出してアイコンを取得
            # 理由: アイコン生成はicon_managerの責務
            self.icon_cache[cache_key] = get_icon_for_item(slot_data)

        icon = self.icon_cache[cache_key]

        # アイコンラベル（中央配置）
        icon_label = tk.Label(slot_frame, image=icon, bg="#f8f9fa")
        icon_label.image = icon  # 参照を保持
        icon_label.place(x=20, y=3)  # 中央配置: (72-32)/2 = 20

        # 名前ラベル（固定幅、テキストは省略）
        name = slot_data.get("name", "")
        # 最大10文字、それ以上は省略（スロット幅72pxに対応）
        display_name = name[:10] if len(name) <= 10 else name[:9] + "…"
        name_label = tk.Label(
            slot_frame,
            text=display_name,
            bg="#f8f9fa",
            fg="#212529",
            font=("Arial", 7),
            wraplength=70,  # 自動改行を有効化
        )
        name_label.place(x=36, y=51, anchor="center")  # 中央に配置

        # クリックイベント
        # 理由: アイテム起動はslot_managerの責務
        icon_label.bind(
            "<Button-1>",
            lambda e, t=tab_index, r=row, c=col: self.launcher_ui.slot_manager.launch_item(
                t, r, c
            ),
        )
        name_label.bind(
            "<Button-1>",
            lambda e, t=tab_index, r=row, c=col: self.launcher_ui.slot_manager.launch_item(
                t, r, c
            ),
        )

        # 右クリックイベント
        # 理由: メニュー表示はmenu_managerの責務
        icon_label.bind(
            "<Button-3>",
            lambda e, t=tab_index, r=row, c=col: self.launcher_ui.menu_manager.show_slot_menu(
                e, t, r, c
            ),
        )
        name_label.bind(
            "<Button-3>",
            lambda e, t=tab_index, r=row, c=col: self.launcher_ui.menu_manager.show_slot_menu(
                e, t, r, c
            ),
        )

    def _create_empty_slot(
        self, slot_frame: tk.Frame, tab_index: int, row: int, col: int
    ) -> None:
        """
        空のスロットのUIを作成

        Args:
            slot_frame: スロットフレーム
            tab_index: タブインデックス
            row: 行
            col: 列
        """
        # 空のアイコン
        # 理由: 空アイコンの生成はicon_managerの責務
        empty_icon = create_empty_icon()

        # アイコンラベル（中央配置）
        icon_label = tk.Label(slot_frame, image=empty_icon, bg="#f8f9fa")
        icon_label.image = empty_icon
        icon_label.place(x=20, y=6)

        # ヒントラベル
        hint_label = tk.Label(
            slot_frame,
            text="右クリック",
            bg="#f8f9fa",
            font=("Arial", 6),
            fg="#6c757d",
        )
        hint_label.place(x=36, y=54, anchor="center")

        # 空のスロットにも右クリックイベント
        # 理由: メニュー表示はmenu_managerの責務
        icon_label.bind(
            "<Button-3>",
            lambda e, t=tab_index, r=row, c=col: self.launcher_ui.menu_manager.show_slot_menu(
                e, t, r, c
            ),
        )
        hint_label.bind(
            "<Button-3>",
            lambda e, t=tab_index, r=row, c=col: self.launcher_ui.menu_manager.show_slot_menu(
                e, t, r, c
            ),
        )

    def refresh_slot(self, tab_index: int, row: int, col: int) -> None:
        """
        スロットのUIを更新

        Args:
            tab_index: タブインデックス
            row: 行
            col: 列

        処理:
        1. 既存のスロットを探して削除
        2. create_slotを呼び出して再作成
        """
        # タブフレーム内のgrid_frameを取得
        tab_frame = self.launcher_ui.tabs[tab_index]

        # 既存のウィジェットを削除（grid_frame内のスロットを探す）
        for child in tab_frame.winfo_children():
            if isinstance(child, tk.Frame):
                for grandchild in child.winfo_children():
                    if isinstance(grandchild, tk.Frame):
                        for slot in grandchild.grid_slaves(row=row, column=col):
                            slot.destroy()
                        # スロットを再作成
                        self.create_slot(grandchild, tab_index, row, col)
                        break
                break
