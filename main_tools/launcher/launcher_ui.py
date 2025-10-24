# -*- coding: utf-8 -*-
"""
ランチャーUIモジュール

ランチャーのメインUI（3×8グリッド、タブ、マウスホイール対応）
"""

import os
import subprocess
import tkinter as tk
import webbrowser
from tkinter import filedialog, messagebox, simpledialog, ttk
from typing import Any

from .config import LauncherConfig
from .icon_manager import create_empty_icon, get_icon_for_item

# スロットのサイズ定数
SLOT_WIDTH = 72
SLOT_HEIGHT = 64
SLOT_PADDING = 3


class LauncherUI:
    """ランチャーのUIクラス"""

    def __init__(self, root: tk.Tk, tool_manager: Any = None, app: Any = None):
        """
        初期化

        Args:
            root: tkinterのルートウィンドウ
            tool_manager: ツールマネージャーモジュール
            app: TrayApplicationインスタンス
        """
        self.root = root
        self.tool_manager = tool_manager
        self.app = app
        self.config = LauncherConfig()

        # アイコンのキャッシュ
        self.icon_cache: dict[str, Any] = {}

        # メニューバーを作成
        self.create_menubar()

        # 保存されているグリッドサイズを読み込み
        saved_cols, saved_rows = self.config.get_grid_size()
        self.num_cols = saved_cols
        self.num_rows = saved_rows
        self.slots_per_tab = self.num_cols * self.num_rows

        # ノートブック（タブ）
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # タブの作成
        self.tabs: list[tk.Frame] = []
        self.create_tabs()

        # マウスホイールイベントのバインド
        self.bind_mousewheel()

        # ウィンドウサイズを可変に設定
        self.root.resizable(True, True)

        # ウィンドウサイズをグリッドにぴったり合わせる
        self.adjust_window_size()

        # ウィンドウサイズ変更イベントをバインド
        self.root.bind("<Configure>", self.on_window_resize)
        self._resize_timer = None

    def create_menubar(self) -> None:
        """メニューバーを作成"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # 設定メニュー
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="設定", menu=settings_menu)
        settings_menu.add_command(label="タブの編集", command=self.edit_tabs)

    def edit_tabs(self) -> None:
        """タブ編集ダイアログを表示"""
        # 自動非表示機能を無効化
        if self.app:
            self.app.disable_auto_hide()

        dialog = tk.Toplevel(self.root)
        dialog.title("タブの編集")
        dialog.geometry("400x300")
        dialog.transient(self.root)
        dialog.grab_set()

        # ダイアログが閉じられたときに自動非表示を再有効化
        def on_dialog_close():
            if self.app:
                self.app.enable_auto_hide()
            dialog.destroy()

        dialog.protocol("WM_DELETE_WINDOW", on_dialog_close)

        # タブリストフレーム
        list_frame = tk.Frame(dialog)
        list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        tk.Label(list_frame, text="タブ一覧:").pack(anchor=tk.W)

        # リストボックスとスクロールバー
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set)
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=listbox.yview)

        # 現在のタブを表示
        def refresh_list():
            listbox.delete(0, tk.END)
            for i in range(self.config.get_tab_count()):
                tab_name = self.config.get_tab_name(i)
                listbox.insert(tk.END, f"{i+1}. {tab_name}")

        refresh_list()

        # ボタンフレーム
        button_frame = tk.Frame(dialog)
        button_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)

        def add_tab():
            name = simpledialog.askstring("タブ追加", "新しいタブの名前を入力してください:", parent=dialog)
            if name:
                tabs = self.config.config.get("tabs", [])
                tabs.append({"name": name, "slots": {}})
                self.config.save()
                refresh_list()

        def edit_tab():
            selection = listbox.curselection()
            if not selection:
                messagebox.showwarning("警告", "編集するタブを選択してください", parent=dialog)
                return

            tab_index = selection[0]
            current_name = self.config.get_tab_name(tab_index)
            new_name = simpledialog.askstring(
                "タブ編集",
                "新しいタブ名を入力してください:",
                initialvalue=current_name,
                parent=dialog
            )
            if new_name:
                tabs = self.config.config.get("tabs", [])
                if 0 <= tab_index < len(tabs):
                    tabs[tab_index]["name"] = new_name
                    self.config.save()
                    refresh_list()

        def delete_tab():
            selection = listbox.curselection()
            if not selection:
                messagebox.showwarning("警告", "削除するタブを選択してください", parent=dialog)
                return

            tab_index = selection[0]
            if self.config.get_tab_count() <= 1:
                messagebox.showerror("エラー", "最後のタブは削除できません", parent=dialog)
                return

            tab_name = self.config.get_tab_name(tab_index)
            if messagebox.askyesno("確認", f"タブ「{tab_name}」を削除しますか？", parent=dialog):
                tabs = self.config.config.get("tabs", [])
                tabs.pop(tab_index)
                self.config.save()
                refresh_list()

        def apply_changes():
            # タブを再構築
            self.icon_cache.clear()
            for tab in self.tabs:
                tab.destroy()
            self.tabs.clear()
            self.create_tabs()

            # 自動非表示を再有効化
            if self.app:
                self.app.enable_auto_hide()

            dialog.destroy()

        tk.Button(button_frame, text="追加", command=add_tab, width=10).pack(pady=5)
        tk.Button(button_frame, text="編集", command=edit_tab, width=10).pack(pady=5)
        tk.Button(button_frame, text="削除", command=delete_tab, width=10).pack(pady=5)
        tk.Button(button_frame, text="適用して閉じる", command=apply_changes, width=10).pack(pady=20)

    def create_tabs(self) -> None:
        """タブを作成"""
        tab_count = self.config.get_tab_count()

        for tab_index in range(tab_count):
            tab_name = self.config.get_tab_name(tab_index)

            # タブフレームを作成（改善された色合い）
            tab_frame = tk.Frame(self.notebook, bg="#ffffff")
            self.tabs.append(tab_frame)
            self.notebook.add(tab_frame, text=tab_name)

            # グリッドを作成
            self.create_grid(tab_frame, tab_index)

    def create_grid(self, parent: tk.Frame, tab_index: int) -> None:
        """
        動的なグリッドを作成（余白を対称に配置）

        Args:
            parent: 親フレーム
            tab_index: タブインデックス
        """
        # 親フレームの中央にグリッドを配置するための外側フレーム
        outer_frame = tk.Frame(parent, bg="#ffffff")
        outer_frame.pack(fill=tk.BOTH, expand=True)

        # グリッドを配置する内側フレーム（中央配置）
        grid_frame = tk.Frame(outer_frame, bg="#ffffff")
        grid_frame.place(relx=0.5, rely=0.5, anchor="center")

        for row in range(self.num_rows):
            for col in range(self.num_cols):
                self.create_slot(grid_frame, tab_index, row, col)

    def adjust_window_size(self) -> None:
        """ウィンドウサイズをグリッドにぴったり合わせる"""
        # タブとメニューバーの高さを考慮
        menubar_height = 25
        tab_height = 40
        padding = 20

        # 必要なウィンドウサイズを計算
        content_width = self.num_cols * (SLOT_WIDTH + SLOT_PADDING * 2)
        content_height = self.num_rows * (SLOT_HEIGHT + SLOT_PADDING * 2)

        window_width = content_width + padding
        window_height = content_height + menubar_height + tab_height + padding

        # ウィンドウサイズを設定
        self.root.geometry(f"{window_width}x{window_height}")

        # TrayApplicationのウィンドウサイズも更新
        if self.app:
            self.app.update_window_size(window_width, window_height)

    def on_window_resize(self, event: tk.Event) -> None:
        """ウィンドウサイズ変更イベント"""
        # ルートウィンドウのイベントのみ処理
        if event.widget != self.root:
            return

        # 既存のタイマーをキャンセル
        if self._resize_timer is not None:
            self.root.after_cancel(self._resize_timer)

        # 300ms後にリサイズ処理を実行（連続イベントを防ぐ）
        self._resize_timer = self.root.after(300, self.rebuild_grid)

    def rebuild_grid(self) -> None:
        """グリッドを再構築"""
        # 新しいウィンドウサイズを取得
        window_width = self.root.winfo_width()
        window_height = self.root.winfo_height()

        # タブとメニューバーの高さを考慮
        menubar_height = 25
        tab_height = 40
        available_width = window_width - 20
        available_height = window_height - menubar_height - tab_height - 20

        # 新しい列数と行数を計算
        new_cols = max(1, available_width // (SLOT_WIDTH + SLOT_PADDING * 2))
        new_rows = max(1, available_height // (SLOT_HEIGHT + SLOT_PADDING * 2))

        # グリッドサイズが変わった場合のみ再構築
        if new_cols != self.num_cols or new_rows != self.num_rows:
            self.num_cols = new_cols
            self.num_rows = new_rows
            self.slots_per_tab = self.num_cols * self.num_rows

            # グリッドサイズを保存
            self.config.set_grid_size(self.num_cols, self.num_rows)

            # アイコンキャッシュをクリア
            self.icon_cache.clear()

            # すべてのタブを削除
            for tab in self.tabs:
                tab.destroy()
            self.tabs.clear()

            # タブを再作成
            self.create_tabs()

            # ウィンドウサイズをぴったり合わせる
            self.adjust_window_size()

    def create_slot(
        self, parent: tk.Frame, tab_index: int, row: int, col: int
    ) -> None:
        """
        スロットを作成

        Args:
            parent: 親フレーム
            tab_index: タブインデックス
            row: 行
            col: 列
        """
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
            # アイコン取得
            cache_key = f"{tab_index}_{row}_{col}"
            if cache_key not in self.icon_cache:
                self.icon_cache[cache_key] = get_icon_for_item(slot_data)

            icon = self.icon_cache[cache_key]

            # アイコンラベル（中央配置）
            icon_label = tk.Label(slot_frame, image=icon, bg="#f8f9fa")
            icon_label.image = icon  # 参照を保持
            icon_label.place(x=20, y=3)  # 中央配置: (72-32)/2 = 20

            # 名前ラベル（固定幅、テキストは省略）
            name = slot_data.get("name", "")
            # 最大9文字、それ以上は省略
            display_name = name[:9] if len(name) <= 9 else name[:8] + "…"
            name_label = tk.Label(
                slot_frame,
                text=display_name,
                bg="#f8f9fa",
                fg="#212529",
                font=("Arial", 7),
            )
            name_label.place(x=36, y=51, anchor="center")  # 中央に配置

            # クリックイベント
            icon_label.bind(
                "<Button-1>",
                lambda e, t=tab_index, r=row, c=col: self.launch_item(t, r, c),
            )
            name_label.bind(
                "<Button-1>",
                lambda e, t=tab_index, r=row, c=col: self.launch_item(t, r, c),
            )

            # 右クリックイベント
            icon_label.bind(
                "<Button-3>",
                lambda e, t=tab_index, r=row, c=col: self.show_slot_menu(e, t, r, c),
            )
            name_label.bind(
                "<Button-3>",
                lambda e, t=tab_index, r=row, c=col: self.show_slot_menu(e, t, r, c),
            )
        else:
            # 空のスロット
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
            icon_label.bind(
                "<Button-3>",
                lambda e, t=tab_index, r=row, c=col: self.show_slot_menu(e, t, r, c),
            )
            hint_label.bind(
                "<Button-3>",
                lambda e, t=tab_index, r=row, c=col: self.show_slot_menu(e, t, r, c),
            )

        # スロットフレーム自体にも右クリックメニュー
        slot_frame.bind(
            "<Button-3>",
            lambda e, t=tab_index, r=row, c=col: self.show_slot_menu(e, t, r, c),
        )

    def show_slot_menu(self, event: tk.Event, tab_index: int, row: int, col: int) -> None:
        """
        スロットの右クリックメニューを表示

        Args:
            event: イベント
            tab_index: タブインデックス
            row: 行
            col: 列
        """
        menu = tk.Menu(self.root, tearoff=0)

        slot_data = self.config.get_slot(tab_index, row, col)

        if slot_data:
            menu.add_command(
                label="起動", command=lambda: self.launch_item(tab_index, row, col)
            )
            menu.add_separator()

        menu.add_command(
            label="ファイルを登録",
            command=lambda: self.register_file(tab_index, row, col),
        )
        menu.add_command(
            label="webサイトを登録",
            command=lambda: self.register_website(tab_index, row, col),
        )

        # ツールがある場合はツールメニューを追加
        if self.tool_manager:
            tools = self.tool_manager.get_all_tools()
            if tools:
                tools_menu = tk.Menu(menu, tearoff=0)
                for tool in tools:
                    tools_menu.add_command(
                        label=tool["name"],
                        command=lambda t=tool: self.register_tool(
                            tab_index, row, col, t
                        ),
                    )
                menu.add_cascade(label="ツールを登録", menu=tools_menu)

        if slot_data:
            menu.add_separator()
            menu.add_command(
                label="削除", command=lambda: self.clear_slot(tab_index, row, col)
            )

        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

        return "break"  # イベント伝播を止める

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
                if cache_key in self.icon_cache:
                    del self.icon_cache[cache_key]

                # UIを再構築
                self.refresh_slot(tab_index, row, col)

    def register_website(self, tab_index: int, row: int, col: int) -> None:
        """
        webサイトを登録

        Args:
            tab_index: タブインデックス
            row: 行
            col: 列
        """
        url = simpledialog.askstring("URL入力", "webサイトのURLを入力してください:")
        if url:
            # 名前を入力
            name = simpledialog.askstring("名前入力", "表示名を入力してください:")

            if name:
                slot_data = {"type": "web", "url": url, "name": name}
                self.config.set_slot(tab_index, row, col, slot_data)

                # キャッシュをクリア
                cache_key = f"{tab_index}_{row}_{col}"
                if cache_key in self.icon_cache:
                    del self.icon_cache[cache_key]

                # UIを再構築
                self.refresh_slot(tab_index, row, col)

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
        if cache_key in self.icon_cache:
            del self.icon_cache[cache_key]

        # UIを再構築
        self.refresh_slot(tab_index, row, col)

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
        if cache_key in self.icon_cache:
            del self.icon_cache[cache_key]

        # UIを再構築
        self.refresh_slot(tab_index, row, col)

    def refresh_slot(self, tab_index: int, row: int, col: int) -> None:
        """
        スロットのUIを更新

        Args:
            tab_index: タブインデックス
            row: 行
            col: 列
        """
        # タブフレーム内のgrid_frameを取得
        tab_frame = self.tabs[tab_index]

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
                    # ファイルを開く（ショートカットの場合も元のパスで開く）
                    if os.name == "nt":  # Windows
                        os.startfile(file_path)
                    else:
                        subprocess.call(["xdg-open", file_path])
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

    def bind_mousewheel(self) -> None:
        """マウスホイールイベントをバインド"""

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

        # Windowsの場合
        self.root.bind_all("<MouseWheel>", on_mousewheel)
        # Linux/Macの場合
        self.root.bind_all("<Button-4>", lambda e: on_mousewheel(type("Event", (), {"delta": 1})()))
        self.root.bind_all("<Button-5>", lambda e: on_mousewheel(type("Event", (), {"delta": -1})()))
