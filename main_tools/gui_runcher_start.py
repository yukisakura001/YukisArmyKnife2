"""GUIトレイアプリケーション - シンプルで読みやすい統合版"""

from .gui_runcher_window import TrayApplication
from .launcher.config import LauncherConfig
from .main_screen import my_custom_widgets

# スロットのサイズ定数（launcher_ui.pyと同じ値）
SLOT_WIDTH = 72
SLOT_HEIGHT = 64
SLOT_PADDING = 3


def gui_runcher_start() -> None:
    """GUIアプリケーションを起動する（エントリーポイント）"""
    # 保存されているグリッドサイズを読み込み
    config = LauncherConfig()
    num_cols, num_rows = config.get_grid_size()

    # ウィンドウサイズの計算
    menubar_height = 25
    tab_height = 40
    padding = 20

    content_width = num_cols * (SLOT_WIDTH + SLOT_PADDING * 2)
    content_height = num_rows * (SLOT_HEIGHT + SLOT_PADDING * 2)

    window_width = content_width + padding
    window_height = content_height + menubar_height + tab_height + padding

    geometry = f"{window_width}x{window_height}"

    app = TrayApplication(
        create_widgets=my_custom_widgets, title="Yakランチャー", geometry=geometry
    )
    app.run()
