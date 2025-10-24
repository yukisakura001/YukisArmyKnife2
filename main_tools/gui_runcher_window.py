import threading
import tkinter as tk
from collections.abc import Callable
from tkinter import Menu
from typing import Any

import pystray
from PIL import Image, ImageDraw
from pystray import MenuItem


class TrayApplication:
    """トレイアプリケーション全体を管理するクラス"""

    def __init__(
        self,
        create_widgets: Callable[["TrayApplication", tk.Tk], None] | None = None,
        title: str = "トレイ格納Tkinter",
        geometry: str = "320x180",
    ) -> None:
        """アプリケーションを初期化

        Args:
            create_widgets: ウィジェット作成用のコールバック関数。
                           引数として(app, root)を受け取る。
                           Noneの場合はデフォルトのウィジェットを作成。
            title: ウィンドウのタイトル
            geometry: ウィンドウのサイズ
        """
        # Tkinterウィンドウの初期化
        self.root: tk.Tk = tk.Tk()
        self.root.title(title)
        self.root.geometry(geometry)

        # トレイアイコンの初期化
        self.icon: pystray.Icon | None = None

        # 外部ウィジェット作成関数を保存
        self._external_create_widgets: (
            Callable[["TrayApplication", tk.Tk], None] | None
        ) = create_widgets

        # ウィジェットの作成
        self._create_widgets()

        # イベントハンドラの設定
        self._setup_handlers()

    def _create_widgets(self) -> None:
        """ウィンドウのウィジェットを作成"""
        # 外部のウィジェット作成関数が指定されている場合はそれを使用
        if self._external_create_widgets is not None:
            self._external_create_widgets(self, self.root)
        else:
            # デフォルトのウィジェット
            # ラベル
            tk.Label(
                self.root,
                text="これはウィンドウです（左クリックでトレイから復帰）",
                pady=16,
            ).pack()

            # トレイへ隠すボタン
            tk.Button(self.root, text="トレイへ隠す", command=self.hide_to_tray).pack()

    def _setup_handlers(self) -> None:
        """イベントハンドラを設定"""
        # ウィンドウを閉じたときの動作
        self.root.protocol("WM_DELETE_WINDOW", self.hide_to_tray)

        # 右クリックメニュー
        context_menu = Menu(self.root, tearoff=0)
        context_menu.add_command(label="トレイへ隠す", command=self.hide_to_tray)
        context_menu.add_separator()
        context_menu.add_command(label="終了", command=self.quit_app)

        def show_context_menu(event: tk.Event[Any]) -> None:
            try:
                context_menu.tk_popup(event.x_root, event.y_root)
            finally:
                context_menu.grab_release()

        self.root.bind("<Button-3>", show_context_menu)

    def _create_tray_icon(self) -> None:
        """トレイアイコンを作成"""
        # アイコン画像の生成
        size = 64
        img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        dc = ImageDraw.Draw(img)
        margin = 8
        dc.ellipse(
            (margin, margin, size - margin, size - margin), fill=(30, 144, 255, 255)
        )

        # トレイアイコンの作成
        self.icon = pystray.Icon(
            "tray_app",
            icon=img,
            title="トレイアプリ",
            menu=pystray.Menu(
                MenuItem("表示", self._on_tray_click, default=True),
                MenuItem("終了", self._on_tray_quit),
            ),
        )

    def _on_tray_click(
        self, icon_obj: pystray.Icon | None = None, item: MenuItem | None = None
    ) -> None:
        """トレイアイコンクリック時の処理"""
        self.root.after(0, self.show_window)

    def _on_tray_quit(
        self, icon_obj: pystray.Icon | None = None, item: MenuItem | None = None
    ) -> None:
        """トレイメニューから終了を選択時の処理"""
        self.quit_app()

    def show_window(self) -> None:
        """ウィンドウを表示"""
        self.root.deiconify()
        self.root.lift()
        try:
            self.root.focus_force()
            self.root.attributes("-topmost", True)
            self.root.after(100, lambda: self.root.attributes("-topmost", False))
        except Exception:
            pass

    def hide_to_tray(self) -> None:
        """ウィンドウをトレイに隠す"""
        try:
            self.root.withdraw()
        except Exception:
            pass
        try:
            if self.icon:
                self.icon.visible = True
        except Exception:
            pass

    def quit_app(self) -> None:
        """アプリケーションを終了"""
        try:
            if self.icon:
                self.icon.stop()
        except Exception:
            pass
        self.root.after(0, self.root.destroy)

    def _start_tray_thread(self) -> None:
        """トレイアイコンを別スレッドで起動"""
        if self.icon is None:
            raise RuntimeError("トレイアイコンが初期化されていません")

        try:
            # pystray 0.19.0以降
            if hasattr(self.icon, "run_detached"):
                self.icon.run_detached()
            else:
                raise AttributeError
        except Exception:
            # 手動でスレッド起動
            t = threading.Thread(target=self.icon.run, daemon=True)
            t.start()

    def _show_startup_toast(self) -> None:
        """起動時にトースト通知を表示"""
        if self.icon:
            try:
                self.icon.notify(
                    title="アプリケーション起動",
                    message="トレイに格納されました。左クリックで表示します。",
                    # アプリ名
                )
            except Exception:
                pass

    def run(self) -> None:
        """アプリケーションを起動"""
        # トレイアイコンを作成
        self._create_tray_icon()

        # トレイアイコンのスレッドを起動
        self._start_tray_thread()

        # 起動時はトレイに隠す
        self.hide_to_tray()

        # 起動時トースト通知を表示（少し遅延させて確実に表示）
        self.root.after(500, self._show_startup_toast)

        # Tkメインループ
        self.root.mainloop()
