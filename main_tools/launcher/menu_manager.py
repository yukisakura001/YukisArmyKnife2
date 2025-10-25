# -*- coding: utf-8 -*-
"""
メニュー管理モジュール

責務:
- ランチャーのメニューバー作成
- コンテキストメニュー（右クリックメニュー）の表示

ロジック:
- メニューバーにツールメニューと設定メニューを追加
- tool_managerから全ツールを取得してツールメニューに追加（理由: ツール管理はtool_managerの責務）
- タブ編集はtab_edit_dialogを呼び出す（理由: ダイアログ表示はtab_edit_dialogの責務）
- スロットの右クリックメニューでslot_managerの機能を呼び出す（理由: スロット操作はslot_managerの責務）
"""

import tkinter as tk
from typing import TYPE_CHECKING

from .tab_edit_dialog import TabEditDialog

if TYPE_CHECKING:
    from .launcher_ui import LauncherUI


class MenuManager:
    """メニュー管理クラス"""

    def __init__(self, launcher_ui: "LauncherUI"):
        """
        初期化

        Args:
            launcher_ui: LauncherUIインスタンス
                        - メニュー作成に必要な情報を保持
        """
        self.launcher_ui = launcher_ui
        self.root = launcher_ui.root
        self.config = launcher_ui.config
        self.tool_manager = launcher_ui.tool_manager
        self.app = launcher_ui.app

    def create_menubar(self) -> None:
        """
        メニューバーを作成

        処理:
        1. ツールメニューを作成（tool_managerから全ツールを取得）
        2. 設定メニューを作成（タブの編集）

        理由:
        - tool_managerから全ツールを取得してメニューに追加
          （ツール一覧の取得はtool_managerの責務）
        - メニューからツールを起動する際はslot_managerを呼び出す
          （ツール起動の処理はslot_managerの責務）
        """
        # メニューバーを作成（フォントサイズを調整して見切れを防ぐ）
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # ツールメニュー
        if self.tool_manager:
            # tool_managerから全ツールを取得
            # 理由: ツール管理はtool_managerの責務
            tools = self.tool_manager.get_all_tools()
            if tools:
                tools_menu = tk.Menu(menubar, tearoff=0)
                menubar.add_cascade(label="ツール  ", menu=tools_menu)
                for tool in tools:
                    tools_menu.add_command(
                        label=tool["name"],
                        # slot_managerを呼び出してツールを起動
                        # 理由: ツール起動処理はslot_managerの責務
                        command=lambda t=tool: self.launcher_ui.slot_manager.launch_tool_from_menu(
                            t
                        ),
                    )

        # 設定メニュー
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(
            label="設定  ",
            menu=settings_menu,
        )

        settings_menu.add_command(label="タブの編集", command=self.edit_tabs)

    def edit_tabs(self) -> None:
        """
        タブ編集ダイアログを表示

        理由: tab_edit_dialogを呼び出す
              （ダイアログ表示はtab_edit_dialogの責務）
        """
        dialog = TabEditDialog(self.root, self.config, self.app, self.launcher_ui)
        dialog.show()

    def show_slot_menu(
        self, event: tk.Event, tab_index: int, row: int, col: int
    ) -> str:
        """
        スロットの右クリックメニューを表示

        Args:
            event: イベント
            tab_index: タブインデックス
            row: 行
            col: 列

        Returns:
            "break": イベント伝播を止める

        処理:
        - スロットのデータの有無でメニュー項目を変更
        - 登録済みの場合は「起動」メニューを追加
        - 常に「ファイル/Webサイト/ツールを登録」メニューを表示
        - 登録済みの場合は「削除」メニューを追加

        理由:
        - スロット操作（登録、削除、起動）はslot_managerを呼び出す
          （スロット操作の責務はslot_managerにあるため）
        """
        menu = tk.Menu(self.root, tearoff=0, font=("", 9))

        slot_data = self.config.get_slot(tab_index, row, col)

        if slot_data:
            # slot_managerを呼び出して起動
            # 理由: アイテム起動処理はslot_managerの責務
            menu.add_command(
                label="起動",
                command=lambda: self.launcher_ui.slot_manager.launch_item(
                    tab_index, row, col
                ),
            )
            menu.add_separator()

        # slot_managerを呼び出してファイルを登録
        # 理由: スロット登録処理はslot_managerの責務
        menu.add_command(
            label="ファイルを登録",
            command=lambda: self.launcher_ui.slot_manager.register_file(
                tab_index, row, col
            ),
        )
        menu.add_command(
            label="Webサイトを登録",
            command=lambda: self.launcher_ui.slot_manager.register_website(
                tab_index, row, col
            ),
        )

        # ツールがある場合はツールメニューを追加
        if self.tool_manager:
            # tool_managerから全ツールを取得
            # 理由: ツール一覧の取得はtool_managerの責務
            tools = self.tool_manager.get_all_tools()
            if tools:
                tools_menu = tk.Menu(menu, tearoff=0, font=("", 9))
                for tool in tools:
                    # slot_managerを呼び出してツールを登録
                    # 理由: ツール登録処理はslot_managerの責務
                    tools_menu.add_command(
                        label=tool["name"],
                        command=lambda t=tool: self.launcher_ui.slot_manager.register_tool(
                            tab_index, row, col, t
                        ),
                    )
                menu.add_cascade(label="ツールを登録", menu=tools_menu)

        if slot_data:
            menu.add_separator()
            # slot_managerを呼び出してスロットをクリア
            # 理由: スロット削除処理はslot_managerの責務
            menu.add_command(
                label="削除",
                command=lambda: self.launcher_ui.slot_manager.clear_slot(
                    tab_index, row, col
                ),
            )

        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

        return "break"  # イベント伝播を止める
