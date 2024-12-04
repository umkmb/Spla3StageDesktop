import tkinter as tk
from tkinter import ttk
from api_handler import fetch_data

class MyApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Splatoon3")
        self.geometry("400x300")

        # ラベルとボタンを配置
        label = ttk.Label(self, text="Splatoon3 ステージ情報", font=("Arial", 16))
        label.pack(pady=20)

        button = ttk.Button(self, text="新規取得", command=self.on_button_click)
        button.pack(pady=10)


    def on_button_click(self):
        url = "https://spla3.yuu26.com/api/schedule"
        data = fetch_data(url)
        if data:
            print(f"Fetched Data: {data}")
        else:
            print("Failed to fetch data.")


if __name__ == "__main__":
    app = MyApp()
    app.mainloop()
