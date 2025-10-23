"""GUIトレイアプリケーション - シンプルで読みやすい統合版"""

from .gui_runcher_window import TrayApplication
from .main_screen import my_custom_widgets


def gui_runcher_start() -> None:
    """GUIアプリケーションを起動する（エントリーポイント）"""
    app = TrayApplication(
        create_widgets=my_custom_widgets, title="メモアプリ", geometry="500x400"
    )
    app.run()
