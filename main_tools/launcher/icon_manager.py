# -*- coding: utf-8 -*-
"""
アイコン管理モジュール

ファイル、webサイト、ツールのアイコンを取得・管理する
"""

import hashlib
import os
import sys
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from PIL import Image, ImageDraw, ImageTk

# アイコンキャッシュディレクトリ
ICONS_DIR = Path("launcher_icons")
ICONS_DIR.mkdir(exist_ok=True)

# アイコンサイズ
ICON_SIZE = (32, 32)


def get_default_icon(item_type: str = "file") -> Image.Image:
    """
    デフォルトアイコンを生成

    Args:
        item_type: アイテムタイプ（file, web, tool）

    Returns:
        PIL.Image: アイコン画像
    """
    img = Image.new("RGBA", ICON_SIZE, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # タイプ別の洗練された色（パステルトーン）
    colors = {
        "file": (52, 152, 219, 255),      # ブルー
        "web": (231, 76, 60, 255),        # レッド
        "tool": (46, 204, 113, 255),      # グリーン
    }
    color = colors.get(item_type, (149, 165, 166, 255))

    # グラデーション風の丸を描画
    margin = 6
    draw.ellipse(
        (margin, margin, ICON_SIZE[0] - margin, ICON_SIZE[1] - margin),
        fill=color,
        outline=(color[0]-20, color[1]-20, color[2]-20, 255),
        width=2
    )

    return img


def resolve_shortcut(file_path: str) -> str:
    """
    ショートカットの場合、リンク先のパスを取得

    Args:
        file_path: ファイルパス（.lnkファイルの可能性あり）

    Returns:
        str: リンク先のパス（ショートカットでない場合は元のパス）
    """
    if not file_path.lower().endswith(".lnk"):
        return file_path

    try:
        if sys.platform == "win32":
            import pythoncom
            from win32com.shell import shell, shellcon

            # COMの初期化
            pythoncom.CoInitialize()

            try:
                # ショートカットオブジェクトを作成
                shortcut = pythoncom.CoCreateInstance(
                    shell.CLSID_ShellLink,
                    None,
                    pythoncom.CLSCTX_INPROC_SERVER,
                    shell.IID_IShellLink,
                )

                # IPersistFileインターフェイスを取得
                persist_file = shortcut.QueryInterface(pythoncom.IID_IPersistFile)

                # ショートカットファイルを読み込み
                persist_file.Load(file_path)

                # リンク先のパスを取得
                target_path, _ = shortcut.GetPath(0)

                if target_path:
                    return target_path
            finally:
                pythoncom.CoUninitialize()
    except Exception as e:
        print(f"ショートカット解決エラー: {e}")

    return file_path


def get_file_icon(file_path: str) -> Image.Image:
    """
    ファイルのアイコンを取得

    Args:
        file_path: ファイルパス

    Returns:
        PIL.Image: アイコン画像
    """
    try:
        # ショートカットの場合はリンク先を取得
        resolved_path = resolve_shortcut(file_path)

        # Windowsの場合、SHGetFileInfoを使用してアイコンを取得
        if sys.platform == "win32":
            try:
                import ctypes
                from ctypes import wintypes

                import win32api
                import win32con
                import win32gui
                import win32ui

                # SHGetFileInfo構造体
                class SHFILEINFO(ctypes.Structure):
                    _fields_ = [
                        ("hIcon", wintypes.HANDLE),
                        ("iIcon", ctypes.c_int),
                        ("dwAttributes", wintypes.DWORD),
                        ("szDisplayName", wintypes.WCHAR * 260),
                        ("szTypeName", wintypes.WCHAR * 80),
                    ]

                # SHGetFileInfoを使用（拡張子とUSEFILEATTRIBUTESフラグでファイルタイプのアイコンを取得）
                shell32 = ctypes.windll.shell32
                shfi = SHFILEINFO()

                # SHGFI_USEFILEATTRIBUTES を使用してファイルタイプのアイコンを取得
                flags = (
                    0x000000100  # SHGFI_ICON
                    | 0x000000000  # SHGFI_LARGEICON
                    | 0x000000010  # SHGFI_USEFILEATTRIBUTES
                )

                ret = shell32.SHGetFileInfoW(
                    resolved_path,
                    0x80,  # FILE_ATTRIBUTE_NORMAL
                    ctypes.byref(shfi),
                    ctypes.sizeof(shfi),
                    flags,
                )

                if ret and shfi.hIcon:
                    hicon = shfi.hIcon

                    # アイコンサイズを取得
                    ico_x = win32api.GetSystemMetrics(win32con.SM_CXICON)
                    ico_y = win32api.GetSystemMetrics(win32con.SM_CYICON)

                    # アイコンをビットマップに変換
                    hdc = win32ui.CreateDCFromHandle(win32gui.GetDC(0))
                    hbmp = win32ui.CreateBitmap()
                    hbmp.CreateCompatibleBitmap(hdc, ico_x, ico_y)
                    hdc = hdc.CreateCompatibleDC()

                    hdc.SelectObject(hbmp)
                    hdc.DrawIcon((0, 0), hicon)

                    # ビットマップをPIL Imageに変換
                    bmpstr = hbmp.GetBitmapBits(True)
                    img = Image.frombuffer(
                        "RGBA", (ico_x, ico_y), bmpstr, "raw", "BGRA", 0, 1
                    )

                    # クリーンアップ
                    win32gui.DestroyIcon(hicon)

                    return img.resize(ICON_SIZE, Image.Resampling.LANCZOS)
                else:
                    return get_default_icon("file")
            except Exception as e:
                print(f"Windowsアイコン取得エラー: {e}")
                return get_default_icon("file")
        else:
            # 他のOSの場合はデフォルトアイコン
            return get_default_icon("file")
    except Exception as e:
        print(f"ファイルアイコン取得エラー: {e}")
        return get_default_icon("file")


def get_website_favicon(url: str) -> Image.Image:
    """
    webサイト専用のアイコンを作成（faviconは取得しない）

    Args:
        url: webサイトのURL

    Returns:
        PIL.Image: アイコン画像
    """
    # webサイト専用のアイコンを作成（改善された配色）
    img = Image.new("RGBA", ICON_SIZE, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # 地球のアイコン風の円を描画（より洗練された青）
    margin = 5
    # 外側の円（明るい青）
    draw.ellipse(
        (margin, margin, ICON_SIZE[0] - margin, ICON_SIZE[1] - margin),
        fill=(41, 128, 185, 255),
        outline=(31, 97, 141, 255),
        width=1,
    )

    # 白い線で地球のグリッドを描画
    center_x, center_y = ICON_SIZE[0] // 2, ICON_SIZE[1] // 2
    radius = (ICON_SIZE[0] - margin * 2) // 2

    # 縦線（経度）- より細く
    for offset in [-radius // 2, 0, radius // 2]:
        x = center_x + offset
        draw.ellipse(
            (x - radius // 4, margin, x + radius // 4, ICON_SIZE[1] - margin),
            outline=(255, 255, 255, 180),
            width=1,
        )

    # 横線（緯度）- より細く
    for offset in [-radius // 2, 0, radius // 2]:
        y = center_y + offset
        draw.line(
            (margin + 3, y, ICON_SIZE[0] - margin - 3, y),
            fill=(255, 255, 255, 180),
            width=1,
        )

    return img


def get_tool_icon(tool_name: str) -> Image.Image:
    """
    ツールのアイコンを取得

    Args:
        tool_name: ツール名

    Returns:
        PIL.Image: アイコン画像
    """
    # 将来的にはツール独自のアイコンを返すことができる
    return get_default_icon("tool")


def get_icon_for_item(item_data: dict[str, Any]) -> ImageTk.PhotoImage:
    """
    アイテムに応じたアイコンを取得

    Args:
        item_data: アイテムデータ

    Returns:
        ImageTk.PhotoImage: tkinterで使用できるアイコン画像
    """
    item_type = item_data.get("type", "file")

    if item_type == "file":
        file_path = item_data.get("path", "")
        if file_path and os.path.exists(file_path):
            img = get_file_icon(file_path)
        else:
            img = get_default_icon("file")
    elif item_type == "web":
        url = item_data.get("url", "")
        if url:
            img = get_website_favicon(url)
        else:
            img = get_default_icon("web")
    elif item_type == "tool":
        tool_name = item_data.get("tool_name", "")
        img = get_tool_icon(tool_name)
    else:
        img = get_default_icon("file")

    return ImageTk.PhotoImage(img)


def create_empty_icon() -> ImageTk.PhotoImage:
    """
    空のスロット用のアイコンを作成

    Returns:
        ImageTk.PhotoImage: 空のアイコン画像
    """
    img = Image.new("RGBA", ICON_SIZE, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # 破線の枠を描画（より洗練された色）
    color = (173, 181, 189, 255)  # グレー
    dash_length = 3
    for i in range(0, ICON_SIZE[0], dash_length * 2):
        draw.line((i, 0, min(i + dash_length, ICON_SIZE[0] - 1), 0), fill=color, width=1)
        draw.line((i, ICON_SIZE[1] - 1, min(i + dash_length, ICON_SIZE[0] - 1), ICON_SIZE[1] - 1), fill=color, width=1)
    for i in range(0, ICON_SIZE[1], dash_length * 2):
        draw.line((0, i, 0, min(i + dash_length, ICON_SIZE[1] - 1)), fill=color, width=1)
        draw.line((ICON_SIZE[0] - 1, i, ICON_SIZE[0] - 1, min(i + dash_length, ICON_SIZE[1] - 1)), fill=color, width=1)

    # プラス記号を描画（より小さく、洗練された色）
    center_x, center_y = ICON_SIZE[0] // 2, ICON_SIZE[1] // 2
    line_len = 8
    line_width = 2
    plus_color = (108, 117, 125, 255)  # ダークグレー
    # 縦線
    draw.rectangle(
        (center_x - line_width // 2, center_y - line_len,
         center_x + line_width // 2, center_y + line_len),
        fill=plus_color
    )
    # 横線
    draw.rectangle(
        (center_x - line_len, center_y - line_width // 2,
         center_x + line_len, center_y + line_width // 2),
        fill=plus_color
    )

    return ImageTk.PhotoImage(img)
