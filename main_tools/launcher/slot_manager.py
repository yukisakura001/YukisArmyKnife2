# -*- coding: utf-8 -*-
"""
スロット管理モジュール

ランチャーのスロット操作（登録、削除、起動）を管理
"""

import os
import webbrowser
from tkinter import filedialog, messagebox, simpledialog
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .launcher_ui import LauncherUI


class SlotManager:
    """スロット管理クラス"""

    def __init__(self, launcher_ui: "LauncherUI"):
        """
        初期化

        Args:
            launcher_ui: LauncherUIインスタンス
        """
        self.launcher_ui = launcher_ui
        self.config = launcher_ui.config
        self.tool_manager = launcher_ui.tool_manager
        self.app = launcher_ui.app

    def register_file(self, tab_index: int, row: int, col: int) -> None:
        """
        ファイルを登録

        Args:
            tab_index: タブインデックス
            row: 行
            col: 列
        """
        file_path = filedialog.askopenfilename(title="ファイルを選択")
        if file_path:
            # 名前を入力
            default_name = os.path.basename(file_path)
            name = simpledialog.askstring(
                "名前入力", "表示名を入力してください:", initialvalue=default_name
            )

            if name:
                slot_data = {"type": "file", "path": file_path, "name": name}
                self.config.set_slot(tab_index, row, col, slot_data)

                # キャッシュをクリア
                cache_key = f"{tab_index}_{row}_{col}"
                if cache_key in self.launcher_ui.icon_cache:
                    del self.launcher_ui.icon_cache[cache_key]

                # UIを再構築
                self.launcher_ui.refresh_slot(tab_index, row, col)

    def register_website(self, tab_index: int, row: int, col: int) -> None:
        """
        webサイトを登録

        Args:
            tab_index: タブインデックス
            row: 行
            col: 列
        """
        url = simpledialog.askstring("URL入力", "WebサイトのURLを入力してください:")
        if url:
            # 名前を入力
            name = simpledialog.askstring("名前入力", "表示名を入力してください:")

            if name:
                slot_data = {"type": "web", "url": url, "name": name}
                self.config.set_slot(tab_index, row, col, slot_data)

                # キャッシュをクリア
                cache_key = f"{tab_index}_{row}_{col}"
                if cache_key in self.launcher_ui.icon_cache:
                    del self.launcher_ui.icon_cache[cache_key]

                # UIを再構築
                self.launcher_ui.refresh_slot(tab_index, row, col)

    def register_tool(
        self, tab_index: int, row: int, col: int, tool: dict[str, Any]
    ) -> None:
        """
        ツールを登録

        Args:
            tab_index: タブインデックス
            row: 行
            col: 列
            tool: ツール情報
        """
        slot_data = {
            "type": "tool",
            "tool_name": tool["name"],
            "tool_function": tool["function"].__name__,
            "name": tool["name"],
        }
        self.config.set_slot(tab_index, row, col, slot_data)

        # キャッシュをクリア
        cache_key = f"{tab_index}_{row}_{col}"
        if cache_key in self.launcher_ui.icon_cache:
            del self.launcher_ui.icon_cache[cache_key]

        # UIを再構築
        self.launcher_ui.refresh_slot(tab_index, row, col)

    def clear_slot(self, tab_index: int, row: int, col: int) -> None:
        """
        スロットをクリア

        Args:
            tab_index: タブインデックス
            row: 行
            col: 列
        """
        self.config.clear_slot(tab_index, row, col)

        # キャッシュをクリア
        cache_key = f"{tab_index}_{row}_{col}"
        if cache_key in self.launcher_ui.icon_cache:
            del self.launcher_ui.icon_cache[cache_key]

        # UIを再構築
        self.launcher_ui.refresh_slot(tab_index, row, col)

    def launch_item(self, tab_index: int, row: int, col: int) -> None:
        """
        アイテムを起動

        Args:
            tab_index: タブインデックス
            row: 行
            col: 列
        """
        slot_data = self.config.get_slot(tab_index, row, col)
        if not slot_data:
            return

        item_type = slot_data.get("type", "")

        try:
            if item_type == "file":
                file_path = slot_data.get("path", "")
                if os.path.exists(file_path):
                    # ファイルを開く（Windows専用）
                    os.startfile(file_path)
                else:
                    messagebox.showerror("エラー", "ファイルが見つかりません")
                    return  # エラーの場合は隠さない

            elif item_type == "web":
                url = slot_data.get("url", "")
                if url:
                    webbrowser.open(url)
                else:
                    messagebox.showerror("エラー", "URLが無効です")
                    return  # エラーの場合は隠さない

            elif item_type == "tool":
                tool_function_name = slot_data.get("tool_function", "")
                if self.tool_manager and tool_function_name:
                    # ツール関数を取得して実行
                    tools = self.tool_manager.get_all_tools()
                    for tool in tools:
                        if tool["function"].__name__ == tool_function_name:
                            self.tool_manager.launch_tool(tool["function"])
                            break
                else:
                    messagebox.showerror("エラー", "ツールが見つかりません")
                    return  # エラーの場合は隠さない

            # 起動成功したらウィンドウを隠す
            if self.app:
                self.app.hide_to_tray()

        except Exception as e:
            messagebox.showerror("エラー", f"起動に失敗しました:\n{e}")

    def launch_tool_from_menu(self, tool: dict[str, Any]) -> None:
        """
        メニューからツールを起動

        Args:
            tool: ツール情報
        """
        try:
            if self.tool_manager:
                self.tool_manager.launch_tool(tool["function"])
                # 起動成功したらウィンドウを隠す
                if self.app:
                    self.app.hide_to_tray()
        except Exception as e:
            messagebox.showerror("エラー", f"ツールの起動に失敗しました:\n{e}")
