# -*- coding: utf-8 -*-
"""
ランチャー設定管理モジュール

ランチャーの設定をJSON形式で保存・読み込みする
"""

import json
from pathlib import Path
from typing import Any

# 定数
NUM_COLS = 8
NUM_ROWS = 3
SLOTS_PER_TAB = NUM_COLS * NUM_ROWS
DEFAULT_NUM_TABS = 4


class LauncherConfig:
    """ランチャーの設定を管理するクラス"""

    def __init__(self, config_file: str = "launcher_config.json"):
        """
        初期化

        Args:
            config_file: 設定ファイルのパス
        """
        self.config_file = Path(config_file)
        self.config: dict[str, Any] = {}
        self.load()

    def load(self) -> None:
        """設定をファイルから読み込む"""
        if self.config_file.exists():
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    self.config = json.load(f)
            except Exception as e:
                print(f"設定ファイルの読み込みに失敗: {e}")
                self.config = self._create_default_config()
        else:
            self.config = self._create_default_config()

    def save(self) -> None:
        """設定をファイルに保存"""
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"設定ファイルの保存に失敗: {e}")

    def _create_default_config(self) -> dict[str, Any]:
        """デフォルトの設定を作成"""
        return {
            "tabs": [
                {"name": f"Tab {i+1}", "slots": {}}  # 辞書形式に変更
                for i in range(DEFAULT_NUM_TABS)
            ],
            "grid_size": {
                "cols": NUM_COLS,
                "rows": NUM_ROWS
            }
        }

    def get_tab_count(self) -> int:
        """タブの数を取得"""
        return len(self.config.get("tabs", []))

    def get_tab_name(self, tab_index: int) -> str:
        """タブ名を取得"""
        tabs = self.config.get("tabs", [])
        if 0 <= tab_index < len(tabs):
            return tabs[tab_index].get("name", f"Tab {tab_index+1}")
        return f"Tab {tab_index+1}"

    def get_slot(self, tab_index: int, row: int, col: int) -> dict[str, Any] | None:
        """指定されたスロットの設定を取得（座標ベース）"""
        tabs = self.config.get("tabs", [])
        if 0 <= tab_index < len(tabs):
            slots = tabs[tab_index].get("slots", {})
            slot_key = f"{row}_{col}"
            return slots.get(slot_key)
        return None

    def set_slot(
        self, tab_index: int, row: int, col: int, slot_data: dict[str, Any] | None
    ) -> None:
        """指定されたスロットに設定を保存（座標ベース）"""
        tabs = self.config.get("tabs", [])
        if 0 <= tab_index < len(tabs):
            if "slots" not in tabs[tab_index]:
                tabs[tab_index]["slots"] = {}

            slot_key = f"{row}_{col}"
            if slot_data is None:
                # Noneの場合は削除
                tabs[tab_index]["slots"].pop(slot_key, None)
            else:
                tabs[tab_index]["slots"][slot_key] = slot_data
            self.save()

    def clear_slot(self, tab_index: int, row: int, col: int) -> None:
        """指定されたスロットをクリア"""
        self.set_slot(tab_index, row, col, None)

    def get_grid_size(self) -> tuple[int, int]:
        """保存されているグリッドサイズを取得"""
        grid_size = self.config.get("grid_size", {})
        cols = grid_size.get("cols", NUM_COLS)
        rows = grid_size.get("rows", NUM_ROWS)
        return cols, rows

    def set_grid_size(self, cols: int, rows: int) -> None:
        """グリッドサイズを保存"""
        self.config["grid_size"] = {"cols": cols, "rows": rows}
        self.save()
