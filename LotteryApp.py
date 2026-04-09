import tkinter as tk
from tkinter import messagebox
import random
import os
import sys
from datetime import datetime

BG_COLOR = "#1e1e2e"
CARD_COLOR = "#2a2a3d"
ACCENT = "#7c5cff"
TEXT_COLOR = "#ffffff"

def get_base_path():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(__file__)

class LotteryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("抽獎小幫手")
        self.root.geometry("520x520")
        self.root.configure(bg=BG_COLOR)

        self.guilds = {
            "貓樂園": self.load_list("貓樂園.txt"),
            "遊樂園": self.load_list("遊樂園.txt")
        }

        self.today_winners = self.load_today_log()

        self.current_list = []
        self.winners = []
        self.is_animating = False

        main = tk.Frame(root, bg=BG_COLOR)
        main.pack(padx=20, pady=20, fill="both", expand=True)

        tk.Label(main, text="🎰 抽獎小幫手",
                 font=("Arial", 20, "bold"),
                 bg=BG_COLOR, fg=TEXT_COLOR).pack(pady=10)

        # 控制區
        control = tk.Frame(main, bg=CARD_COLOR)
        control.pack(fill="x", pady=10)

        self.guild_var = tk.StringVar(value="貓樂園")
        tk.OptionMenu(control, self.guild_var, *self.guilds.keys()).pack(pady=5)

        self.count_entry = tk.Entry(control, justify="center")
        self.count_entry.pack(pady=5)

        # 顯示
        self.result_label = tk.Label(main,
                                     text="",
                                     font=("Arial", 28, "bold"),
                                     bg=BG_COLOR,
                                     fg="#ffd166")
        self.result_label.pack(pady=15)

        # 按鈕
        btn = tk.Label(main, text="開始抽籤",
                       bg=ACCENT, fg="white",
                       font=("Arial", 14),
                       padx=20, pady=10,
                       cursor="hand2")
        btn.pack(pady=10)
        btn.bind("<Button-1>", lambda e: self.start_draw())

        # ===== 中獎名單（可滾動）=====
        result_frame = tk.Frame(main, bg=BG_COLOR)
        result_frame.pack(fill="both", expand=True)

        scrollbar = tk.Scrollbar(result_frame)
        scrollbar.pack(side="right", fill="y")

        self.winner_box = tk.Text(
            result_frame,
            bg="#1a1a2e",
            fg="#00ffcc",
            insertbackground="white",
            yscrollcommand=scrollbar.set,
            font=("Consolas", 12),
            spacing1=5,   # 上間距（像卡片）
            spacing3=5    # 下間距
        )

        self.winner_box.pack(fill="both", expand=True, padx=5, pady=5)
        scrollbar.config(command=self.winner_box.yview)

    def load_list(self, filename):
        base_path = get_base_path()
        filepath = os.path.join(base_path, filename)

        if not os.path.exists(filepath):
            return []

        with open(filepath, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]

    def load_today_log(self):
        today = datetime.now().strftime("%Y-%m-%d")
        filename = os.path.join(get_base_path(), f"log_{today}.txt")
        winners = set()

        if os.path.exists(filename):
            with open(filename, "r", encoding="utf-8") as f:
                for line in f:
                    if "中獎:" in line:
                        names = line.split("中獎:")[1].strip()
                        for n in names.split(","):
                            winners.add(n.strip())
        return winners

    def start_draw(self):
        if self.is_animating:
            return

        guild = self.guild_var.get()
        self.current_list = [
            name for name in self.guilds[guild]
            if name not in self.today_winners
        ]

        try:
            count = int(self.count_entry.get())
        except:
            messagebox.showerror("錯誤", "請輸入數字")
            return

        if len(self.current_list) == 0:
            messagebox.showerror("提示", "今日此公會已全部抽過了")
            return

        if count > len(self.current_list):
            messagebox.showerror("錯誤", f"剩餘可抽人數不足（剩 {len(self.current_list)} 人）")
            return

        self.winners = []

        # 清空卡片
        self.winner_box.delete("1.0", tk.END)

        self.draw_multiple(count)

    def draw_multiple(self, count):
        if count == 0:
            self.save_log()
            return

        self.animate_draw(lambda: self.finish_one_draw(count))

    def animate_draw(self, callback):
        self.is_animating = True
        self.animate_count = 0

        def animation():
            if self.animate_count < 25:
                name = random.choice(self.current_list)
                self.result_label.config(text=name)
                self.animate_count += 1
                self.root.after(40, animation)
            else:
                self.is_animating = False
                callback()

        animation()

    def finish_one_draw(self, remaining):
        winner = random.choice(self.current_list)
        self.current_list.remove(winner)
        self.winners.append(winner)

        self.result_label.config(text=f"🎉 {winner}")

        self.add_card(winner)

        self.root.after(400, lambda: self.draw_multiple(remaining - 1))

    def add_card(self, name):
        is_repeat = name in self.today_winners

        text = f"  ✔ {name}"
        if is_repeat:
            text += "  ⚠ 今日已中"

        tag = "repeat" if is_repeat else "normal"

        self.winner_box.insert(tk.END, text + "\n", tag)

        # 設定樣式（像卡片）
        self.winner_box.tag_config(
            "normal",
            foreground="#00ffcc",
            background="#2a2a3d"
        )

        self.winner_box.tag_config(
            "repeat",
            foreground="#ff6b6b",
            background="#2a2a3d"
        )

    def save_log(self):
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H:%M:%S")

        filename = f"log_{date_str}.txt"
        guild = self.guild_var.get()
        winners_str = ", ".join(self.winners)

        with open(filename, "a", encoding="utf-8") as f:
            f.write(f"[{time_str}] 公會: {guild} | 中獎: {winners_str}\n")

        # 更新今日紀錄
        self.today_winners.update(self.winners)

        messagebox.showinfo("完成", f"已記錄到 {filename}")


if __name__ == "__main__":
    root = tk.Tk()
    app = LotteryApp(root)
    root.mainloop()