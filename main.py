import tkinter as tk
import my_icon
import io, os, sys, time
from tkinter import ttk
from api_handler import fetch_data
from dateutil.parser import parse
from PIL import Image, ImageTk
from pystray import Icon, Menu, MenuItem
import threading

CATEGORY_MAP = {
    "regular": "レギュラーマッチ",
    "bankara_challenge": "バンカラマッチ（チャレンジ）",
    "bankara_open": "バンカラマッチ（オープン）",
    "x": "Xマッチ",
    "event": "イベントマッチ",
    "fest": "フェスマッチ（オープン）",
    "fest_challenge": "フェスマッチ（チャレンジ）"
}


def format_time(iso_time):
    """ISO 8601形式の日時を日本語形式にフォーマットする"""
    try:
        dt = parse(iso_time)  # dateutil.parserを使用して解析
        return dt.strftime("%Y年%m月%d日 %H:%M:%S")  # 例: 2024年12月05日 11:00:00
    except Exception as e:
        print(f"日時フォーマットエラー: {e}")
        return "不明な日時"

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


class MyApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Splatoon3")
        self.geometry("800x600")

        # icon
        # self.icon_img = my_icon.get_photo_image4icon()
        self.icon_img = Image.open(resource_path("icon.png"))
        self.tk_icon_img = ImageTk.PhotoImage(self.icon_img)

        self.iconphoto(True, self.tk_icon_img)

        # スクロール可能なキャンバスを作成
        self.canvas = tk.Canvas(self)
        self.scroll_y = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scroll_y.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.configure(yscrollcommand=self.scroll_y.set)

        # キャンバス内のフレーム
        self.frame = ttk.Frame(self.canvas, style="Custom.TFrame")
        self.canvas.create_window((0, 0), window=self.frame, anchor="nw", width=780)

        # ホイール可能
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        # ボタンとイベントバインド
        self.fetch_button = ttk.Button(self, text="更新", command=self.load_data, style="Custom.TButton")
        self.fetch_button.pack(pady=10)

        self.frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        self.style = ttk.Style()

        # トレイアイコン
        self.protocol("WM_DELETE_WINDOW", self.minimize_to_tray)
        self.bind("<Unmap>", self.on_minimize)
        self.icon = None
        self.tray_thread = None
        self.run_tray = threading.Event()

        # 最小化イベントをバインド
        self.bind("<Unmap>", self.on_minimize)

        # 起動時にAPIをたたく
        self.load_data()

    def load_data(self):
        """データを取得して表示する"""
        try:
            url = "https://spla3.yuu26.com/api/schedule"
            data = fetch_data(url)
            if data and "result" in data:
                self.display_data(data["result"])
            else:
                self.display_data({"error": "データの取得に失敗しました。"})
        except Exception as e:
            print(f"An error occurred: {e}")

    def display_data(self, data):
        """JSONデータを整形して日時順に複数のマッチを表示（Noneチェック付き）"""
        if not data:
            print("Error: result is empty or None")
            return

        for widget in self.frame.winfo_children():
            widget.destroy()

        # 全てのマッチをリスト化し、日時順にソート
        matches = []
        for category, match_list in data.items():
            for match in match_list:
                start_time = match.get("start_time")
                end_time = match.get("end_time")
                rule = match.get("rule")
                stages = match.get("stages")

                # `rule` や `stages` が None の場合はスキップ
                if rule is None or stages is None:
                    continue

                match["category"] = category
                matches.append(match)

        # 開始日時でソート
        matches.sort(key=lambda x: parse(x["start_time"]))

        # 時間帯ごとにグループ化
        grouped_matches = {}
        for match in matches:
            start_time = parse(match["start_time"])
            end_time = parse(match["end_time"])
            time_slot = f"{start_time.strftime('%m/%d %H:%M')} - {end_time.strftime('%H:%M')}"
            if time_slot not in grouped_matches:
                grouped_matches[time_slot] = []
            grouped_matches[time_slot].append(match)

        # グループごとに表示
        for time_slot, slot_matches in grouped_matches.items():
            ttk.Label(self.frame, text=f"・{time_slot}", font=("Arial", 12, "bold")).pack(anchor="w", pady=5)

            # 各カテゴリごとに整理
            category_matches = {}
            for match in slot_matches:
                category = match["category"]
                if category not in category_matches:
                    category_matches[category] = []
                category_matches[category].append(match)

            for category, matches in category_matches.items():
                category_name = CATEGORY_MAP.get(category, category)
                rule = matches[0].get("rule", {}).get("name", "ルール不明")  # 同じカテゴリでルールは共通
                ttk.Label(self.frame, text=f"    ・{category_name}[{rule}]", font=("Arial", 10)).pack(anchor="w",
                                                                                                      pady=2)

                for match in matches:
                    stages = match.get("stages", [])
                    for stage in stages:
                        stage_name = stage.get("name", "不明なステージ")
                        ttk.Label(self.frame, text=f"        ・{stage_name}", font=("Arial", 10)).pack(anchor="w",
                                                                                                       pady=2)

            ttk.Separator(self.frame, orient="horizontal").pack(fill="x", pady=10)

    def display_match(self, match):
        """1つのマッチデータを整形して表示"""
        if not match or not match.get("rule"):
            print("Error: match is None or rule is missing")
            return

        start_time = format_time(match.get("start_time", "N/A"))
        end_time = format_time(match.get("end_time", "N/A"))

        rule = match.get("rule", {}).get("name", "ルール不明") if match.get("rule") else None
        stages = match.get("stages", []) if match.get("stages") else []

        # カードスタイルのフレーム
        card_frame = ttk.Frame(self.frame, style="Card.TFrame")
        card_frame.pack(anchor="w", pady=10, padx=20, fill="x", expand=True)

        ttk.Label(card_frame, text=f"開始: {start_time}", font=("Arial", 10), style="Card.TLabel").pack(anchor="w")
        ttk.Label(card_frame, text=f"終了: {end_time}", font=("Arial", 10), style="Card.TLabel").pack(anchor="w")

        if rule:
            ttk.Label(card_frame, text=f"ルール: {rule}", font=("Arial", 10), style="Card.TLabel").pack(anchor="w")

        if stages:
            ttk.Label(card_frame, text="ステージ:", font=("Arial", 10, "italic"), style="Card.TLabel").pack(anchor="w",
                                                                                                            padx=10)
            for stage in stages:
                stage_name = stage.get("name", "不明なステージ")
                ttk.Label(card_frame, text=f"- {stage_name}", font=("Arial", 10), style="Card.TLabel").pack(anchor="w",
                                                                                                            padx=20)

        ttk.Separator(card_frame, orient="horizontal").pack(fill="x", pady=5)

    def _on_mousewheel(self, event):
        """マウスホイールでスクロール"""
        self.canvas.yview_scroll(-1 * int(event.delta / 120), "units")

    def minimize_to_tray(self):
        """ウィンドウをタスクトレイに移動"""
        self.withdraw()  # ウィンドウを隠す

        if self.icon is None:
            self.icon = Icon(
                "Splatoon3",
                self.icon_img,
                menu=Menu(
                    MenuItem("Restore", self.restore_app, default=True),
                    MenuItem("Quit", self.quit_app)
                )
            )

        self.tray_thread = threading.Thread(target=self.icon.run)
        self.tray_thread.start()

    def restore_app(self, *args):
        """アプリを復元"""
        self.deiconify()  # ウィンドウを表示
        if self.icon:
            self.icon.stop()  # トレイアイコンを停止
            self.icon = None

    def quit_app(self, *args):
        """アプリを終了"""
        if self.icon:
            self.icon.stop()  # アイコンを停止
            self.icon = None

        # トレイアイコンが動作しているスレッドを終了させる
        if self.tray_thread and self.tray_thread.is_alive():
            self.run_tray.set()  # スレッドを停止するフラグを立てる
            try:
                self.tray_thread.join(timeout=1)  # スレッドを待機
            except RuntimeError:
                pass

    def on_minimize(self, event):
        """ウィンドウが最小化されたときにトレイに移動"""
        if self.state() == "iconic":  # 最小化状態をチェック
            self.minimize_to_tray()


if __name__ == "__main__":
    app = MyApp()
    app.mainloop()
