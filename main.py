import tkinter as tk
from tkinter import ttk
from api_handler import fetch_data
from datetime import datetime
from dateutil.parser import parse

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

        # スクロール可能なキャンバスを作成
        self.canvas = tk.Canvas(self)
        self.scroll_y = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scroll_y.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.configure(yscrollcommand=self.scroll_y.set)

        # キャンバス内のフレーム
        self.frame = ttk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.frame, anchor="nw")
        
        # ホイール可能
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        # ボタンとイベントバインド
        self.fetch_button = ttk.Button(self, text="データ取得", command=self.load_data)
        self.fetch_button.pack(pady=10)

        self.frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

    def load_data(self):
        """データを取得して表示する"""
        url = "https://spla3.yuu26.com/api/schedule"
        data = fetch_data(url)
        if data and "result" in data:
            self.display_data(data["result"])
        else:
            self.display_data({"error": "データの取得に失敗しました。"})

    def display_data(self, data):
        """JSONデータを整形して表示"""
        for widget in self.frame.winfo_children():
            widget.destroy()

        for category, matches in data.items():
            category_name = CATEGORY_MAP.get(category, category)
            ttk.Label(self.frame, text=f"カテゴリ: {category_name}", font=("Arial", 14, "bold")).pack(anchor="w", pady=5)
            #ttk.Label(self.frame, text=f"カテゴリ: {category}", font=("Arial", 14, "bold")).pack(anchor="w", pady=5)

            if isinstance(matches, list):
                for match in matches:
                    self.display_match(match)

            elif isinstance(matches, dict):
                self.display_match(matches)

            else:
                ttk.Label(self.frame, text="データがありません").pack(anchor="w", padx=20)

    def display_match(self, match):
        """1つのマッチデータを整形して表示"""
        #start_time = match.get("start_time", "N/A")
        #end_time = match.get("end_time", "N/A")
        start_time = format_time(match.get("start_time", "N/A"))
        end_time = format_time(match.get("end_time", "N/A"))

        rule = match.get("rule", {}).get("name", "ルール不明")
        stages = match.get("stages", [])

        #ttk.Label(self.frame, text=f"開始: {start_time}", font=("Arial", 10)).pack(anchor="w", padx=20)
        #ttk.Label(self.frame, text=f"終了: {end_time}", font=("Arial", 10)).pack(anchor="w", padx=20)
        ttk.Label(self.frame, text=f"開始: {start_time}", font=("Arial", 10)).pack(anchor="w", padx=20)
        ttk.Label(self.frame, text=f"終了: {end_time}", font=("Arial", 10)).pack(anchor="w", padx=20)

        ttk.Label(self.frame, text=f"ルール: {rule}", font=("Arial", 10)).pack(anchor="w", padx=20)

        if stages:
            ttk.Label(self.frame, text="ステージ:", font=("Arial", 10, "italic")).pack(anchor="w", padx=30)
            for stage in stages:
                stage_name = stage.get("name", "不明なステージ")
                ttk.Label(self.frame, text=f"- {stage_name}", font=("Arial", 10)).pack(anchor="w", padx=40)

        ttk.Separator(self.frame, orient="horizontal").pack(fill="x", pady=10)
    
    def _on_mousewheel(self, event):
        """マウスホイールでスクロール"""
        self.canvas.yview_scroll(-1 * int(event.delta / 120), "units")


if __name__ == "__main__":
    app = MyApp()
    app.mainloop()
