import threading
import tkinter as tk
from collections.abc import Callable

import pystray
from PIL import Image, ImageDraw
from pynput import keyboard, mouse
from pystray import MenuItem
from screeninfo import get_monitors


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

        # ウィンドウサイズを保持（geometryから解析）
        size_parts = geometry.split("+")[0].split("x")
        self.window_width = int(size_parts[0]) if len(size_parts) > 0 else 320
        self.window_height = int(size_parts[1]) if len(size_parts) > 1 else 180

        # トレイアイコンの初期化
        self.icon: pystray.Icon | None = None

        # 外部ウィジェット作成関数を保存
        self._external_create_widgets: (
            Callable[["TrayApplication", tk.Tk], None] | None
        ) = create_widgets

        # 自動非表示のタイマーID
        self._auto_hide_timer: str | None = None

        # 自動非表示機能の有効/無効フラグ
        self._auto_hide_enabled: bool = True

        # ウィジェットの作成
        self._create_widgets()

        # イベントハンドラの設定
        self._setup_handlers()

        # キーボードリスナーの初期化
        self._setup_keyboard_listener()

        # マウストラッキングの設定
        self._setup_mouse_tracking()

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
        """ウィンドウを表示（マウス位置の中心に配置）"""
        # マウスの現在位置を取得
        mouse_controller = mouse.Controller()
        mouse_x, mouse_y = mouse_controller.position

        # マウス位置がウィンドウの中心になるように配置
        x = mouse_x - self.window_width // 2
        y = mouse_y - self.window_height // 2

        # マウスがどのモニターにあるかを判断
        current_monitor = None
        try:
            for monitor in get_monitors():
                if (
                    monitor.x <= mouse_x < monitor.x + monitor.width
                    and monitor.y <= mouse_y < monitor.y + monitor.height
                ):
                    current_monitor = monitor
                    break
        except Exception:
            pass

        # モニターが見つかった場合はそのモニターの境界で制限
        if current_monitor:
            x = max(
                current_monitor.x,
                min(x, current_monitor.x + current_monitor.width - self.window_width),
            )
            y = max(
                current_monitor.y,
                min(y, current_monitor.y + current_monitor.height - self.window_height),
            )
        else:
            # フォールバック: プライマリディスプレイのサイズを使用
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            x = max(0, min(x, screen_width - self.window_width))
            y = max(0, min(y, screen_height - self.window_height))

        # ジオメトリを設定してからウィンドウを表示
        self.root.geometry(f"{self.window_width}x{self.window_height}+{x}+{y}")
        self.root.deiconify()
        self.root.update_idletasks()

        self.root.lift()
        try:
            self.root.focus_force()
            self.root.attributes("-topmost", True)
            self.root.after(100, lambda: self.root.attributes("-topmost", False))
        except Exception:
            pass

        # マウストラッキングを開始
        self._start_mouse_tracking()

    def hide_to_tray(self) -> None:
        """ウィンドウをトレイに隠す"""
        # 自動非表示タイマーをキャンセル
        self._cancel_auto_hide_timer()

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
        try:
            if hasattr(self, "keyboard_listener") and self.keyboard_listener:
                self.keyboard_listener.stop()
        except Exception:
            pass
        self.root.after(0, self.root.destroy)

    def _setup_keyboard_listener(self) -> None:
        """キーボードリスナーを設定（Pauseキーでウィンドウ表示）"""

        def on_press(key):
            try:
                # Pauseキーが押された場合
                if key == keyboard.Key.pause:
                    self.root.after(0, self.show_window)
            except Exception:
                pass

        # キーボードリスナーを開始
        self.keyboard_listener = keyboard.Listener(on_press=on_press)
        self.keyboard_listener.daemon = True
        self.keyboard_listener.start()

    def _setup_mouse_tracking(self) -> None:
        """マウストラッキングの初期設定"""
        # 特に初期設定は不要（_start_mouse_trackingで開始）
        pass

    def _start_mouse_tracking(self) -> None:
        """マウストラッキングを開始（ウィンドウ外で3秒後に隠す）"""
        # 既存のタイマーをキャンセル
        self._cancel_auto_hide_timer()

        # マウス位置をチェック
        self._check_mouse_position()

    def _check_mouse_position(self) -> None:
        """マウス位置をチェックしてウィンドウの外なら3秒後に隠す"""
        try:
            # ウィンドウが表示されていない場合は何もしない
            if not self.root.winfo_viewable():
                return

            # 自動非表示が無効の場合はタイマーをキャンセルするだけ
            if not self._auto_hide_enabled:
                self._cancel_auto_hide_timer()
                self.root.after(100, self._check_mouse_position)
                return

            # マウスの現在位置を取得
            mouse_controller = mouse.Controller()
            mouse_x, mouse_y = mouse_controller.position

            # ウィンドウの位置とサイズを取得
            win_x = self.root.winfo_x()
            win_y = self.root.winfo_y()
            win_width = self.root.winfo_width()
            win_height = self.root.winfo_height()

            # マウスがウィンドウ内にあるかチェック（左右と下側は少し余裕を持たせる）
            SIDE_TOLERANCE = 70  # 左右の許容範囲（ピクセル）
            BOTTOM_TOLERANCE = 70  # 下側の許容範囲（ピクセル）
            is_inside = (
                win_x - SIDE_TOLERANCE <= mouse_x <= win_x + win_width + SIDE_TOLERANCE
                and win_y <= mouse_y <= win_y + win_height + BOTTOM_TOLERANCE
            )

            if is_inside:
                # マウスがウィンドウ内にある場合、タイマーをキャンセル
                self._cancel_auto_hide_timer()
            else:
                # マウスがウィンドウ外にある場合、タイマーを開始（まだ開始していない場合）
                if self._auto_hide_timer is None:
                    self._auto_hide_timer = self.root.after(1000, self.hide_to_tray)

            # 100msごとにチェック
            self.root.after(100, self._check_mouse_position)
        except Exception:
            pass

    def _cancel_auto_hide_timer(self) -> None:
        """自動非表示タイマーをキャンセル"""
        if self._auto_hide_timer is not None:
            try:
                self.root.after_cancel(self._auto_hide_timer)
            except Exception:
                pass
            self._auto_hide_timer = None

    def disable_auto_hide(self) -> None:
        """自動非表示機能を無効化"""
        self._auto_hide_enabled = False
        self._cancel_auto_hide_timer()

    def enable_auto_hide(self) -> None:
        """自動非表示機能を有効化"""
        self._auto_hide_enabled = True

    def update_window_size(self, width: int, height: int) -> None:
        """ウィンドウサイズを更新

        Args:
            width: ウィンドウの幅
            height: ウィンドウの高さ
        """
        self.window_width = width
        self.window_height = height

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
