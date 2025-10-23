# gui_runcher_window.py 使用方法

## 概要

`TrayApplication`クラスは、トレイアイコンに格納できるTkinterアプリケーションを作成するためのクラスです。ウィジェットを外部で定義できるように改良されています。

## 基本的な使い方

### 1. デフォルトのウィジェットを使用

```python
from runchers.gui_runcher_window import TrayApplication

app = TrayApplication()
app.run()
```

### 2. カスタムウィジェットを外部で定義

```python
import tkinter as tk
from runchers.gui_runcher_window import TrayApplication

def my_widgets(app, root):
    """
    カスタムウィジェット定義関数

    Args:
        app: TrayApplicationインスタンス（メソッドにアクセス可能）
        root: tkinter.Tkルートウィンドウ
    """
    tk.Label(root, text="カスタムウィジェット").pack()

    # appのメソッドを使用できる
    tk.Button(root, text="トレイへ", command=app.hide_to_tray).pack()
    tk.Button(root, text="終了", command=app.quit_app).pack()

# カスタムウィジェットを使用してアプリを作成
app = TrayApplication(
    create_widgets=my_widgets,
    title="マイアプリ",
    geometry="400x300"
)
app.run()
```

## コンストラクタの引数

### `TrayApplication(create_widgets=None, title="トレイ格納Tkinter", geometry="320x180")`

- **create_widgets**: ウィジェット作成用のコールバック関数
  - 関数シグネチャ: `def my_widgets(app, root):`
  - `app`: `TrayApplication`のインスタンス
  - `root`: `tkinter.Tk`のルートウィンドウ
  - `None`の場合はデフォルトウィジェットを使用

- **title**: ウィンドウのタイトル（文字列）

- **geometry**: ウィンドウサイズ（"幅x高さ" 形式の文字列）

## 利用可能なメソッド

外部で定義するウィジェット作成関数内で、`app`引数を通じて以下のメソッドにアクセスできます:

### `app.hide_to_tray()`
ウィンドウをトレイに隠します。

```python
tk.Button(root, text="隠す", command=app.hide_to_tray).pack()
```

### `app.show_window()`
トレイから復帰してウィンドウを表示します。

```python
tk.Button(root, text="表示", command=app.show_window).pack()
```

### `app.quit_app()`
アプリケーションを完全に終了します。

```python
tk.Button(root, text="終了", command=app.quit_app).pack()
```

### `app.root`
`tkinter.Tk`のルートウィンドウにアクセスできます。

```python
app.root.title("新しいタイトル")
```

## サンプルコード

詳細なサンプルは `example_custom_widgets.py` を参照してください。

### 例1: カウンターアプリ

```python
def counter_widgets(app, root):
    counter = {"value": 0}

    def increment():
        counter["value"] += 1
        label.config(text=f"カウント: {counter['value']}")

    label = tk.Label(root, text="カウント: 0")
    label.pack()

    tk.Button(root, text="+1", command=increment).pack()
    tk.Button(root, text="トレイへ", command=app.hide_to_tray).pack()

app = TrayApplication(create_widgets=counter_widgets)
app.run()
```

### 例2: テキスト入力アプリ

```python
def text_widgets(app, root):
    entry = tk.Entry(root, width=30)
    entry.pack(pady=10)

    def show_text():
        text = entry.get()
        label.config(text=f"入力: {text}")

    tk.Button(root, text="表示", command=show_text).pack()

    label = tk.Label(root, text="")
    label.pack()

    tk.Button(root, text="トレイへ", command=app.hide_to_tray).pack()

app = TrayApplication(
    create_widgets=text_widgets,
    title="テキスト入力",
    geometry="350x200"
)
app.run()
```

## トレイ操作

- **トレイアイコン左クリック**: ウィンドウを表示
- **トレイメニュー "Show"**: ウィンドウを表示
- **トレイメニュー "Quit"**: アプリ終了
- **ウィンドウ右クリック**: コンテキストメニュー表示
- **ウィンドウ×ボタン**: トレイに隠す

## 注意事項

1. `create_widgets`関数は必ず`(app, root)`の2つの引数を受け取る必要があります
2. ウィジェットの作成は`create_widgets`関数内で完結させてください
3. `app`を通じてアプリケーションのメソッドやプロパティにアクセスできます
