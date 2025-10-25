# -*- coding: utf-8 -*-
"""
タブ編集ダイアログモジュール

責務:
- タブの追加・編集・削除ダイアログの表示と操作
- ダイアログ中は自動非表示機能を無効化

ロジック:
- Toplevelウィンドウでダイアログを作成
- リストボックスでタブ一覧を表示
- ボタンでタブの追加・編集・削除操作を実行
- configに変更を保存し、tab_managerで再構築
"""

import tkinter as tk
from tkinter import messagebox, simpledialog
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .launcher_ui import LauncherUI


class TabEditDialog:
    """タブ編集ダイアログクラス"""

    def __init__(
        self, root: tk.Tk, config: Any, app: Any, launcher_ui: "LauncherUI"
    ):
        """
        初期化

        Args:
            root: tkinterのルートウィンドウ
                  - ダイアログの親ウィンドウとして使用
            config: LauncherConfigインスタンス
                    - タブ情報の取得と保存に使用
            app: TrayApplicationインスタンス
                 - 自動非表示機能の制御に使用
            launcher_ui: LauncherUIインスタンス
                        - タブ再構築時に使用
        """
        self.root = root
        self.config = config
        self.app = app
        self.launcher_ui = launcher_ui

    def show(self) -> None:
        """
        タブ編集ダイアログを表示

        処理:
        1. 自動非表示機能を無効化（ダイアログ操作中に隠れないように）
        2. ダイアログウィンドウを作成
        3. タブリストとボタンを配置
        """
        # 自動非表示機能を無効化
        # 理由: ダイアログ操作中にウィンドウが隠れるのを防ぐ
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
            """タブ一覧を更新"""
            listbox.delete(0, tk.END)
            for i in range(self.config.get_tab_count()):
                tab_name = self.config.get_tab_name(i)
                listbox.insert(tk.END, f"{i+1}. {tab_name}")

        refresh_list()

        # ボタンフレーム
        button_frame = tk.Frame(dialog)
        button_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)

        def add_tab():
            """タブ追加処理"""
            name = simpledialog.askstring(
                "タブ追加", "新しいタブの名前を入力してください:", parent=dialog
            )
            if name:
                # configにタブを追加して保存
                # 理由: 設定の変更はconfigの責務
                tabs = self.config.config.get("tabs", [])
                tabs.append({"name": name, "slots": {}})
                self.config.save()
                refresh_list()

        def edit_tab():
            """タブ編集処理"""
            selection = listbox.curselection()
            if not selection:
                messagebox.showwarning(
                    "警告", "編集するタブを選択してください", parent=dialog
                )
                return

            tab_index = selection[0]
            current_name = self.config.get_tab_name(tab_index)
            new_name = simpledialog.askstring(
                "タブ編集",
                "新しいタブ名を入力してください:",
                initialvalue=current_name,
                parent=dialog,
            )
            if new_name:
                # configでタブ名を更新して保存
                # 理由: 設定の変更はconfigの責務
                tabs = self.config.config.get("tabs", [])
                if 0 <= tab_index < len(tabs):
                    tabs[tab_index]["name"] = new_name
                    self.config.save()
                    refresh_list()

        def delete_tab():
            """タブ削除処理"""
            selection = listbox.curselection()
            if not selection:
                messagebox.showwarning(
                    "警告", "削除するタブを選択してください", parent=dialog
                )
                return

            tab_index = selection[0]
            if self.config.get_tab_count() <= 1:
                messagebox.showerror(
                    "エラー", "最後のタブは削除できません", parent=dialog
                )
                return

            tab_name = self.config.get_tab_name(tab_index)
            if messagebox.askyesno(
                "確認", f"タブ「{tab_name}」を削除しますか？", parent=dialog
            ):
                # configからタブを削除して保存
                # 理由: 設定の変更はconfigの責務
                tabs = self.config.config.get("tabs", [])
                tabs.pop(tab_index)
                self.config.save()
                refresh_list()

        def apply_changes():
            """変更を適用してダイアログを閉じる"""
            # tab_managerを呼び出してタブを再構築
            # 理由: タブ再構築の責務はtab_managerにあるため
            self.launcher_ui.tab_manager.rebuild_tabs()

            # 自動非表示を再有効化
            if self.app:
                self.app.enable_auto_hide()

            dialog.destroy()

        # ボタン配置
        tk.Button(button_frame, text="追加", command=add_tab, width=10).pack(pady=5)
        tk.Button(button_frame, text="編集", command=edit_tab, width=10).pack(pady=5)
        tk.Button(button_frame, text="削除", command=delete_tab, width=10).pack(pady=5)
        tk.Button(
            button_frame, text="適用して閉じる", command=apply_changes, width=12
        ).pack(pady=20)
