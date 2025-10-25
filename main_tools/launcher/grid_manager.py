# -*- coding: utf-8 -*-
"""
グリッド管理モジュール

責務:
- ランチャーのグリッドレイアウト作成
- ウィンドウサイズの計算と調整
- ウィンドウリサイズ時のグリッド再構築

ロジック:
- グリッドフレームを作成し、その中にスロットを配置
- ウィンドウサイズから適切なグリッドサイズ（行列数）を計算
- グリッドサイズ変更時にタブとスロットを再構築
"""

import tkinter as tk
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .launcher_ui import LauncherUI

# スロットのサイズ定数
SLOT_WIDTH = 72
SLOT_HEIGHT = 64
SLOT_PADDING = 3


class GridManager:
    """グリッド管理クラス"""

    def __init__(self, launcher_ui: "LauncherUI"):
        """
        初期化

        Args:
            launcher_ui: LauncherUIインスタンス
                        - グリッド構築に必要な情報とメソッドを保持
        """
        self.launcher_ui = launcher_ui
        self.root = launcher_ui.root
        self.config = launcher_ui.config
        self.app = launcher_ui.app

    def create_grid(self, parent: tk.Frame, tab_index: int) -> None:
        """
        動的なグリッドを作成（余白を対称に配置）

        Args:
            parent: 親フレーム（タブフレーム）
            tab_index: タブインデックス

        処理:
        1. 外側フレームを作成し親フレームにpack
        2. 内側フレーム（グリッド）を中央配置
        3. slot_ui_builderを呼び出して各スロットを作成
        """
        # 親フレームの中央にグリッドを配置するための外側フレーム
        outer_frame = tk.Frame(parent, bg="#ffffff")
        outer_frame.pack(fill=tk.BOTH, expand=True)

        # グリッドを配置する内側フレーム（中央配置）
        grid_frame = tk.Frame(outer_frame, bg="#ffffff")
        grid_frame.place(relx=0.5, rely=0.5, anchor="center")

        # slot_ui_builderを呼び出して各スロットを作成
        # 理由: スロットのUI構築はslot_ui_builderの責務
        for row in range(self.launcher_ui.num_rows):
            for col in range(self.launcher_ui.num_cols):
                self.launcher_ui.slot_ui_builder.create_slot(
                    grid_frame, tab_index, row, col
                )

    def adjust_window_size(self) -> None:
        """
        ウィンドウサイズをグリッドにぴったり合わせる

        処理:
        1. 現在のグリッドサイズからウィンドウサイズを計算
        2. geometryを設定してウィンドウサイズを変更
        3. TrayApplicationにもサイズを通知
        """
        # タブとメニューバーの高さを考慮
        menubar_height = 22  # メニューバーの高さ
        tab_height = 28  # タブの高さ
        notebook_pady = 4  # notebookのpady=2が上下で4px
        top_padding = 10  # 上部の余白
        side_padding = 5  # 左右の余白
        bottom_padding = 5  # 下部の余白

        # 必要なウィンドウサイズを計算
        content_width = self.launcher_ui.num_cols * (SLOT_WIDTH + SLOT_PADDING * 2)
        content_height = self.launcher_ui.num_rows * (SLOT_HEIGHT + SLOT_PADDING * 2)

        window_width = content_width + side_padding * 2
        window_height = (
            content_height + menubar_height + tab_height + top_padding + bottom_padding + notebook_pady
        )

        # 最小サイズを設定（メニューが見切れないように）
        # 「ツール」「設定」メニューを表示するには最低でも350px必要
        min_width = 380
        min_height = menubar_height + tab_height + top_padding + bottom_padding + notebook_pady + 120

        # 実際のウィンドウサイズは最小値以上にする
        window_width = max(window_width, min_width)
        window_height = max(window_height, min_height)

        # ウィンドウサイズを設定
        self.root.geometry(f"{window_width}x{window_height}")

        # ウィンドウの最小サイズも設定
        self.root.minsize(min_width, min_height)

        # TrayApplicationのウィンドウサイズも更新
        # 理由: トレイから表示する際の正しい位置計算に必要
        if self.app:
            self.app.update_window_size(window_width, window_height)

    def on_window_resize(self, event: tk.Event) -> None:
        """
        ウィンドウサイズ変更イベント

        Args:
            event: tkイベントオブジェクト

        処理:
        - ルートウィンドウのイベントのみ処理
        - タイマーを使って連続イベントを防ぐ
        """
        # ルートウィンドウのイベントのみ処理
        if event.widget != self.root:
            return

        # 既存のタイマーをキャンセル
        if self.launcher_ui._resize_timer is not None:
            self.root.after_cancel(self.launcher_ui._resize_timer)

        # 300ms後にリサイズ処理を実行（連続イベントを防ぐ）
        self.launcher_ui._resize_timer = self.root.after(300, self.rebuild_grid)

    def rebuild_grid(self) -> None:
        """
        グリッドを再構築

        処理:
        1. 新しいウィンドウサイズを取得
        2. 利用可能なスペースから新しいグリッドサイズ（行列数）を計算
        3. グリッドサイズが変わった場合のみタブを再構築
        """
        # 新しいウィンドウサイズを取得
        window_width = self.root.winfo_width()
        window_height = self.root.winfo_height()

        # タブとメニューバーの高さを考慮
        menubar_height = 22  # メニューバーの高さ
        tab_height = 28  # タブの高さ
        notebook_pady = 4  # notebookのpady=2が上下で4px
        top_padding = 10  # 上部の余白
        side_padding = 5  # 左右の余白
        bottom_padding = 5  # 下部の余白

        available_width = window_width - side_padding * 2
        available_height = (
            window_height - menubar_height - tab_height - top_padding - bottom_padding - notebook_pady
        )

        # 新しい列数と行数を計算
        new_cols = max(1, available_width // (SLOT_WIDTH + SLOT_PADDING * 2))
        new_rows = max(1, available_height // (SLOT_HEIGHT + SLOT_PADDING * 2))

        # グリッドサイズが変わった場合のみ再構築
        if (
            new_cols != self.launcher_ui.num_cols
            or new_rows != self.launcher_ui.num_rows
        ):
            self.launcher_ui.num_cols = new_cols
            self.launcher_ui.num_rows = new_rows
            self.launcher_ui.slots_per_tab = new_cols * new_rows

            # グリッドサイズを保存
            # 理由: 次回起動時に同じレイアウトを復元するため
            self.config.set_grid_size(
                self.launcher_ui.num_cols, self.launcher_ui.num_rows
            )

            # tab_managerを呼び出してタブを再構築
            # 理由: タブ再構築の責務はtab_managerにあるため
            self.launcher_ui.tab_manager.rebuild_tabs()

            # ウィンドウサイズをぴったり合わせる
            self.adjust_window_size()
