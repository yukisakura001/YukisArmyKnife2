# -*- coding: utf-8 -*-
"""
ツールマネージャーモジュール

すべてのミニツールアプリケーション機能を管理し、
main_screenから簡単に呼び出せるようにする
"""

from .counter import create_counter_app
from .notepad import create_notepad_app


# ツール定義（名前、説明、アプリ関数）
TOOLS = [
    {
        "name": "カウンター",
        "description": "シンプルなカウンターアプリ",
        "function": create_counter_app,
        "color": "lightgreen",
    },
    {
        "name": "メモ帳",
        "description": "シンプルなメモ帳ツール",
        "function": create_notepad_app,
        "color": "lightyellow",
    },
]


def get_all_tools():
    """
    登録されているすべてのツールを取得

    Returns:
        list: ツール情報のリスト
    """
    return TOOLS


def launch_tool(tool_function):
    """
    ツールを起動

    Args:
        tool_function: ツールの関数
    """
    try:
        tool_function()
    except Exception as e:
        print(f"ツールの起動に失敗: {e}")
