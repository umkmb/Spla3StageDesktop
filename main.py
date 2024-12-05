import tkinter as tk
from tkinter import ttk
import my_icon

from api_handler import fetch_data
from datetime import datetime
from dateutil.parser import parse
from tkinter import PhotoImage

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

class MyApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Splatoon3")
        self.geometry("800x600")

        # icon
        photo = my_icon.get_photo_image4icon()
        self.iconphoto(True, photo)

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
        self.fetch_button = ttk.Button(self, text="データ更新", command=self.load_data, style="Custom.TButton")
        self.fetch_button.pack(pady=10)

        self.frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        self.style = ttk.Style()

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
        """JSONデータを整形して表示"""
        if not data:
            print("Error: result is empty or None")
            return

        for widget in self.frame.winfo_children():
            widget.destroy()

        for category, matches in data.items():
            valid_matches = [match for match in matches if match.get("rule")]
            if valid_matches:
                category_name = CATEGORY_MAP.get(category, category)
                ttk.Label(self.frame, text=f"カテゴリ: {category_name}", font=("Arial", 14, "bold")).pack(anchor="w", pady=5)
                for match in valid_matches:
                    self.display_match(match)

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
            ttk.Label(card_frame, text="ステージ:", font=("Arial", 10, "italic"), style="Card.TLabel").pack(anchor="w", padx=10)
            for stage in stages:
                stage_name = stage.get("name", "不明なステージ")
                ttk.Label(card_frame, text=f"- {stage_name}", font=("Arial", 10), style="Card.TLabel").pack(anchor="w", padx=20)

        ttk.Separator(card_frame, orient="horizontal").pack(fill="x", pady=5)

    def _on_mousewheel(self, event):
        """マウスホイールでスクロール"""
        self.canvas.yview_scroll(-1 * int(event.delta / 120), "units")

if __name__ == "__main__":
    app = MyApp()
    app.mainloop()
