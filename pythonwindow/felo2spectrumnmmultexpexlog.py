import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import datetime

# 檢查使用期限
current_date = datetime.date.today()
expiry_date = datetime.date(2025, 3, 29)
if current_date > expiry_date:
    print("已經超過使用期限,請聯繫Steve Li")
    exit()

# 主程式
class SpectrumApp:
    def __init__(self, root):
        self.root = root
        self.root.title("光譜分析程式")
        self.root.geometry("1200x800")
        
        # 登入畫面
        self.login_screen()

    def login_screen(self):
        self.clear_screen()
        tk.Label(self.root, text="請輸入使用者名稱和密碼", font=("Arial", 16)).pack(pady=20)
        
        tk.Label(self.root, text="Username:").pack()
        self.username_entry = tk.Entry(self.root)
        self.username_entry.pack()

        tk.Label(self.root, text="Password:").pack()
        self.password_entry = tk.Entry(self.root, show="*")
        self.password_entry.pack()

        tk.Button(self.root, text="登入", command=self.check_login).pack(pady=10)

    def check_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        if username == "WSL" and password == "50968758":
            self.main_screen()
        else:
            messagebox.showerror("錯誤", "使用者名稱或密碼錯誤")

    def main_screen(self):
        self.clear_screen()

        # 輸入區塊
        input_frame = tk.Frame(self.root)
        input_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

        tk.Label(input_frame, text="輸入光譜檔案數量 (1-10):", font=("Arial", 12)).pack(side=tk.LEFT)
        self.num_files_var = tk.IntVar(value=1)
        tk.Spinbox(input_frame, from_=1, to=10, textvariable=self.num_files_var, width=5, command=self.update_plots).pack(side=tk.LEFT, padx=5)

        # 圖表區塊
        self.plot_frame = tk.Frame(self.root)
        self.plot_frame.pack(fill=tk.BOTH, expand=True)

        # 滾動條
        self.canvas = tk.Canvas(self.plot_frame)
        self.scrollbar = ttk.Scrollbar(self.plot_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 初始化圖表
        self.spectrum_axes = []
        self.sum_axis = None
        self.norm_axis = None
        self.update_plots()

        # 退出按鈕
        tk.Button(self.root, text="EXIT", command=self.root.quit, bg="red", fg="white").pack(side=tk.BOTTOM, pady=10)

    def update_plots(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        self.spectrum_axes = []
        num_files = self.num_files_var.get()

        for i in range(num_files):
            frame = tk.Frame(self.scrollable_frame)
            frame.pack(fill=tk.X, pady=5)

            tk.Label(frame, text=f"光譜檔案 {i+1}:", font=("Arial", 12)).pack(side=tk.LEFT)
            tk.Button(frame, text="讀取檔案", command=lambda idx=i: self.load_file(idx)).pack(side=tk.LEFT, padx=5)

            fig, ax = plt.subplots(figsize=(5, 3))
            ax.set_title(f"光譜圖 {i+1}")
            ax.set_xlabel("nm")
            ax.set_ylabel("mw")
            canvas = FigureCanvasTkAgg(fig, master=frame)
            canvas.get_tk_widget().pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
            self.spectrum_axes.append((fig, ax, canvas))

        # 總和圖
        sum_frame = tk.Frame(self.scrollable_frame)
        sum_frame.pack(fill=tk.X, pady=5)

        tk.Label(sum_frame, text="總和光譜圖:", font=("Arial", 12)).pack(side=tk.LEFT)
        fig, ax = plt.subplots(figsize=(5, 3))
        ax.set_title("總和光譜圖")
        ax.set_xlabel("nm")
        ax.set_ylabel("強度總和")
        canvas = FigureCanvasTkAgg(fig, master=sum_frame)
        canvas.get_tk_widget().pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self.sum_axis = (fig, ax, canvas)

        # 正規化圖
        norm_frame = tk.Frame(self.scrollable_frame)
        norm_frame.pack(fill=tk.X, pady=5)

        tk.Label(norm_frame, text="正規化光譜圖:", font=("Arial", 12)).pack(side=tk.LEFT)
        fig, ax = plt.subplots(figsize=(5, 3))
        ax.set_title("正規化光譜圖")
        ax.set_xlabel("nm")
        ax.set_ylabel("正規化強度")
        canvas = FigureCanvasTkAgg(fig, master=norm_frame)
        canvas.get_tk_widget().pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self.norm_axis = (fig, ax, canvas)

    def load_file(self, idx):
        file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if not file_path:
            return

        try:
            data = pd.read_csv(file_path, delim_whitespace=True)
            if "nm" not in data.columns or "mw" not in data.columns:
                raise ValueError("檔案格式錯誤，缺少 'nm' 或 'mw' 欄位")

            x = data["nm"]
            y = data["mw"]

            # 繪製個別光譜圖
            fig, ax, canvas = self.spectrum_axes[idx]
            ax.clear()
            ax.plot(x, y, label=f"光譜 {idx+1}")
            ax.set_xlabel("nm")
            ax.set_ylabel("mw")
            ax.legend()
            canvas.draw()

            # 更新總和圖與正規化圖
            self.update_sum_and_norm()
        except Exception as e:
            messagebox.showerror("錯誤", f"讀取檔案失敗: {e}")

    def update_sum_and_norm(self):
        all_y = []
        for fig, ax, canvas in self.spectrum_axes:
            lines = ax.get_lines()
            if lines:
                all_y.append(lines[0].get_ydata())

        if not all_y:
            return

        sum_y = sum(all_y)
        norm_y = sum_y / max(sum_y)

        # 繪製總和圖
        fig, ax, canvas = self.sum_axis
        ax.clear()
        ax.plot(range(400, 701), sum_y, label="總和光譜")
        ax.set_xlabel("nm")
        ax.set_ylabel("強度總和")
        ax.legend()
        canvas.draw()

        # 繪製正規化圖
        fig, ax, canvas = self.norm_axis
        ax.clear()
        ax.plot(range(400, 701), norm_y, label="正規化光譜")
        ax.set_xlabel("nm")
        ax.set_ylabel("正規化強度")
        ax.legend()
        canvas.draw()

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = SpectrumApp(root)
    root.mainloop()
