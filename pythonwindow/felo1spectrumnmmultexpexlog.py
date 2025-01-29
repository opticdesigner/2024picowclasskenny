import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import datetime

# 設定中文字型
plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei']
plt.rcParams['axes.unicode_minus'] = False

# 檢查程式是否過期
def check_expiry():
    expiry_date = datetime.date(2025, 3, 29)
    today = datetime.date.today()
    if today > expiry_date:
        messagebox.showerror("錯誤", "已經超過使用期限，請聯繫Steve Li")
        exit()

# 驗證登入
def login():
    username = username_entry.get()
    password = password_entry.get()
    if username == "WSL" and password == "50968758":
        login_window.destroy()
        main_program()
    else:
        messagebox.showerror("錯誤", "帳號或密碼錯誤！")

# 主程式
def main_program():
    check_expiry()

    def on_submit():
        try:
            n = int(entry_n.get())
            if n < 1 or n > 10:
                raise ValueError
            create_graphs(n)
        except ValueError:
            messagebox.showerror("錯誤", "請輸入1到10之間的整數！")

    def create_graphs(n):
        for widget in graph_frame.winfo_children():
            widget.destroy()

        # 建立N個空圖表
        for i in range(n):
            frame = ttk.Frame(graph_frame)
            frame.pack(pady=10)
            label = ttk.Label(frame, text=f"光譜圖 {i + 1}")
            label.pack()
            fig, ax = plt.subplots(figsize=(5, 3))
            ax.set_title(f"光譜圖 {i + 1}")
            ax.set_xlabel("nm")
            ax.set_ylabel("mw")
            canvas = FigureCanvasTkAgg(fig, master=frame)
            canvas.get_tk_widget().pack()
            canvas.draw()

            # 加入讀取按鈕
            def load_file(ax=ax, canvas=canvas):
                file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
                if file_path:
                    try:
                        data = pd.read_csv(file_path, delim_whitespace=True)
                        if "nm" not in data.columns or "mw" not in data.columns:
                            raise ValueError("檔案格式錯誤！")
                        x = data["nm"]
                        y = data["mw"]
                        ax.clear()
                        ax.plot(x, y, label="光譜")
                        ax.set_title(f"光譜圖 {i + 1}")
                        ax.set_xlabel("nm")
                        ax.set_ylabel("mw")
                        ax.legend()
                        canvas.draw()
                        spectra_data.append(y)
                        update_summary_graphs()
                    except Exception as e:
                        messagebox.showerror("錯誤", f"讀取檔案失敗：{e}")

            load_button = ttk.Button(frame, text="讀取檔案", command=lambda ax=ax, canvas=canvas: load_file(ax, canvas))
            load_button.pack()

        # 建立總和圖表
        summary_frame = ttk.Frame(graph_frame)
        summary_frame.pack(pady=10)
        summary_label = ttk.Label(summary_frame, text="總和光譜圖")
        summary_label.pack()
        summary_fig, summary_ax = plt.subplots(figsize=(5, 3))
        summary_ax.set_title("總和光譜圖")
        summary_ax.set_xlabel("nm")
        summary_ax.set_ylabel("mw")
        summary_canvas = FigureCanvasTkAgg(summary_fig, master=summary_frame)
        summary_canvas.get_tk_widget().pack()
        summary_canvas.draw()

        # 建立正規化圖表
        normalized_frame = ttk.Frame(graph_frame)
        normalized_frame.pack(pady=10)
        normalized_label = ttk.Label(normalized_frame, text="正規化光譜圖")
        normalized_label.pack()
        normalized_fig, normalized_ax = plt.subplots(figsize=(5, 3))
        normalized_ax.set_title("正規化光譜圖")
        normalized_ax.set_xlabel("nm")
        normalized_ax.set_ylabel("相對強度")
        normalized_canvas = FigureCanvasTkAgg(normalized_fig, master=normalized_frame)
        normalized_canvas.get_tk_widget().pack()
        normalized_canvas.draw()

        # 更新總和與正規化圖表
        def update_summary_graphs():
            if len(spectra_data) == n:
                total_intensity = sum(spectra_data)
                normalized_intensity = total_intensity / max(total_intensity)

                # 更新總和圖表
                summary_ax.clear()
                summary_ax.plot(range(400, 701), total_intensity, label="總和光譜")
                summary_ax.set_title("總和光譜圖")
                summary_ax.set_xlabel("nm")
                summary_ax.set_ylabel("mw")
                summary_ax.legend()
                summary_canvas.draw()

                # 更新正規化圖表
                normalized_ax.clear()
                normalized_ax.plot(range(400, 701), normalized_intensity, label="正規化光譜")
                normalized_ax.set_title("正規化光譜圖")
                normalized_ax.set_xlabel("nm")
                normalized_ax.set_ylabel("相對強度")
                normalized_ax.legend()
                normalized_canvas.draw()

    def exit_program():
        root.destroy()

    # 主視窗
    root = tk.Tk()
    root.title("光譜分析程式")
    root.geometry("800x600")

    # 輸入區塊
    input_frame = ttk.Frame(root)
    input_frame.pack(pady=10)
    ttk.Label(input_frame, text="輸入光譜檔案數量 (1-10):").pack(side=tk.LEFT, padx=5)
    entry_n = ttk.Entry(input_frame, width=5)
    entry_n.pack(side=tk.LEFT, padx=5)
    submit_button = ttk.Button(input_frame, text="確定", command=on_submit)
    submit_button.pack(side=tk.LEFT, padx=5)

    # 圖表區塊
    graph_frame = ttk.Frame(root)
    graph_frame.pack(fill=tk.BOTH, expand=True)
    canvas = tk.Canvas(graph_frame)
    scrollbar = ttk.Scrollbar(graph_frame, orient=tk.VERTICAL, command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    graph_frame = scrollable_frame

    # EXIT按鈕
    exit_button = ttk.Button(root, text="EXIT", command=exit_program)
    exit_button.pack(pady=10)

    spectra_data = []

    root.mainloop()

# 登入視窗
login_window = tk.Tk()
login_window.title("登入")
login_window.geometry("300x150")

ttk.Label(login_window, text="Username:").pack(pady=5)
username_entry = ttk.Entry(login_window)
username_entry.pack(pady=5)

ttk.Label(login_window, text="Password:").pack(pady=5)
password_entry = ttk.Entry(login_window, show="*")
password_entry.pack(pady=5)

login_button = ttk.Button(login_window, text="登入", command=login)
login_button.pack(pady=10)

login_window.mainloop()
