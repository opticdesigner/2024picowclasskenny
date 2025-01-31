import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei']
plt.rcParams['axes.unicode_minus'] = False

class LoginWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("登入")
        self.root.geometry("300x150")
        
        # 登入框架
        frame = ttk.Frame(self.root, padding="10")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 使用者名稱
        ttk.Label(frame, text="使用者名稱:").grid(row=0, column=0, pady=5)
        self.username = ttk.Entry(frame)
        self.username.grid(row=0, column=1, pady=5)
        
        # 密碼
        ttk.Label(frame, text="密碼:").grid(row=1, column=0, pady=5)
        self.password = ttk.Entry(frame, show="*")
        self.password.grid(row=1, column=1, pady=5)
        
        # 登入按鈕
        ttk.Button(frame, text="登入", command=self.check_login).grid(row=2, column=0, columnspan=2, pady=10)
        
        self.root.mainloop()
    
    def check_login(self):
        if self.username.get() == "WSL" and self.password.get() == "50968758":
            self.root.destroy()
            MainApp()
        else:
            messagebox.showerror("錯誤", "使用者名稱或密碼錯誤！")

class MainApp:
    def __init__(self):
        # 檢查日期
        if datetime.now() > datetime(2025, 1, 29):
            messagebox.showerror("錯誤", "已經超過使用期限,請聯繫Steve Li")
            return
            
        self.root = tk.Tk()
        self.root.title("光譜分析程式")
        self.root.geometry("1200x800")
        
        # 主框架
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 輸入框架
        input_frame = ttk.Frame(main_frame)
        input_frame.pack(pady=10)
        
        ttk.Label(input_frame, text="請輸入光譜數量 (1-10):").pack(side=tk.LEFT)
        self.num_entry = ttk.Entry(input_frame, width=10)
        self.num_entry.pack(side=tk.LEFT, padx=5)
        ttk.Button(input_frame, text="確認", command=self.create_plots).pack(side=tk.LEFT)
        ttk.Button(input_frame, text="EXIT", command=self.root.quit).pack(side=tk.LEFT, padx=10)
        
        # PPF 顯示框架
        self.ppf_frame = ttk.LabelFrame(main_frame, text="PPF 計算結果")
        self.ppf_frame.pack(pady=5, padx=10, fill=tk.X)
        
        # PPF 標籤
        self.total_ppf_label = ttk.Label(self.ppf_frame, text="總 PPF: ")
        self.total_ppf_label.pack(pady=2)
        self.blue_ppf_label = ttk.Label(self.ppf_frame, text="PPF (Blue, 400-499nm): ")
        self.blue_ppf_label.pack(pady=2)
        self.green_ppf_label = ttk.Label(self.ppf_frame, text="PPF (Green, 500-599nm): ")
        self.green_ppf_label.pack(pady=2)
        self.red_ppf_label = ttk.Label(self.ppf_frame, text="PPF (Red, 600-700nm): ")
        self.red_ppf_label.pack(pady=2)
        
        # 建立可捲動的畫布
        canvas_frame = ttk.Frame(main_frame)
        canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        # 分割左右區域
        self.paned = ttk.PanedWindow(canvas_frame, orient=tk.HORIZONTAL)
        self.paned.pack(fill=tk.BOTH, expand=True)
        
        # 左側捲動區域 - 用於個別光譜圖
        self.left_frame = ttk.Frame(self.paned)
        self.left_canvas = tk.Canvas(self.left_frame)
        left_scrollbar = ttk.Scrollbar(self.left_frame, orient=tk.VERTICAL, command=self.left_canvas.yview)
        self.left_scrollable_frame = ttk.Frame(self.left_canvas)
        
        self.left_scrollable_frame.bind(
            "<Configure>",
            lambda e: self.left_canvas.configure(scrollregion=self.left_canvas.bbox("all"))
        )
        
        self.left_canvas.create_window((0, 0), window=self.left_scrollable_frame, anchor="nw")
        self.left_canvas.configure(yscrollcommand=left_scrollbar.set)
        
        self.left_frame.pack(fill=tk.BOTH, expand=True)
        self.left_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        left_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 右側區域 - 用於總和圖和正規化圖
        self.right_frame = ttk.Frame(self.paned)
        self.right_frame.pack(fill=tk.BOTH, expand=True)
        
        self.paned.add(self.left_frame)
        self.paned.add(self.right_frame)
        
        self.plots = []
        self.data = []
        
        self.root.mainloop()
    
    def calculate_ppf(self, wavelengths, intensities):
        ppf_values = wavelengths * intensities * 0.008359 / 1000.0
        total_ppf = np.sum(ppf_values)
        
        # 計算不同波段的 PPF
        blue_mask = (wavelengths >= 400) & (wavelengths <= 499)
        green_mask = (wavelengths >= 500) & (wavelengths <= 599)
        red_mask = (wavelengths >= 600) & (wavelengths <= 700)
        
        blue_ppf = np.sum(ppf_values[blue_mask])
        green_ppf = np.sum(ppf_values[green_mask])
        red_ppf = np.sum(ppf_values[red_mask])
        
        return total_ppf, blue_ppf, green_ppf, red_ppf
    
    def create_plots(self):
        try:
            n = int(self.num_entry.get())
            if not 1 <= n <= 10:
                raise ValueError
        except ValueError:
            messagebox.showerror("錯誤", "請輸入1-10之間的數字！")
            return
            
        # 清除現有圖表
        for widget in self.left_scrollable_frame.winfo_children():
            widget.destroy()
        for widget in self.right_frame.winfo_children():
            widget.destroy()
            
        self.plots = []
        self.data = []
        
        # 創建個別光譜圖
        for i in range(n):
            frame = ttk.Frame(self.left_scrollable_frame)
            frame.pack(pady=10, padx=10, fill=tk.X)
            
            fig = Figure(figsize=(8, 4))
            ax = fig.add_subplot(111)
            ax.set_title(f"光譜 {i+1}")
            ax.set_xlabel("nm")
            ax.set_ylabel("mw")
            
            canvas = FigureCanvasTkAgg(fig, frame)
            canvas.draw()
            canvas.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            
            btn = ttk.Button(frame, text="讀取檔案", 
                           command=lambda idx=i: self.load_file(idx))
            btn.pack(side=tk.LEFT, padx=5)
            
            self.plots.append((fig, ax, canvas))
            self.data.append(None)
            
        # 創建總和圖和正規化圖
        sum_frame = ttk.Frame(self.right_frame)
        sum_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        
        # 總和圖
        self.sum_fig = Figure(figsize=(8, 4))
        self.sum_ax = self.sum_fig.add_subplot(111)
        self.sum_ax.set_title("光譜強度總和")
        self.sum_ax.set_xlabel("nm")
        self.sum_ax.set_ylabel("mw")
        
        self.sum_canvas = FigureCanvasTkAgg(self.sum_fig, sum_frame)
        self.sum_canvas.draw()
        self.sum_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # 正規化圖
        self.norm_fig = Figure(figsize=(8, 4))
        self.norm_ax = self.norm_fig.add_subplot(111)
        self.norm_ax.set_title("正規化光譜強度")
        self.norm_ax.set_xlabel("nm")
        self.norm_ax.set_ylabel("相對強度")
        
        self.norm_canvas = FigureCanvasTkAgg(self.norm_fig, sum_frame)
        self.norm_canvas.draw()
        self.norm_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def load_file(self, idx):
        filename = filedialog.askopenfilename(
            filetypes=[("Text Files", "*.csv"), ("All Files", "*.*")])
        if filename:
            try:
                df = pd.read_csv(filename)
                if "nm" not in df.columns or "mw" not in df.columns:
                    raise ValueError("檔案格式錯誤！")
                
                self.data[idx] = df
                fig, ax, canvas = self.plots[idx]
                ax.clear()
                ax.plot(df["nm"], df["mw"])
                ax.set_title(f"光譜 {idx+1}")
                ax.set_xlabel("nm")
                ax.set_ylabel("mw")
                canvas.draw()
                
                self.update_sum_plots()
                
            except Exception as e:
                messagebox.showerror("錯誤", f"讀取檔案時發生錯誤：{str(e)}")
    
    def update_sum_plots(self):
        # 更新總和圖
        self.sum_ax.clear()
        self.norm_ax.clear()
        
        valid_data = [d for d in self.data if d is not None]
        if valid_data:
            # 計算總和
            sum_data = valid_data[0].copy()
            sum_data["mw"] = 0
            for df in valid_data:
                sum_data["mw"] += df["mw"]
            
            self.sum_ax.plot(sum_data["nm"], sum_data["mw"])
            self.sum_ax.set_title("光譜強度總和")
            self.sum_ax.set_xlabel("nm")
            self.sum_ax.set_ylabel("mw")
            
            # 計算正規化
            norm_data = sum_data.copy()
            norm_data["mw"] = norm_data["mw"] / norm_data["mw"].max()
            
            self.norm_ax.plot(norm_data["nm"], norm_data["mw"])
            self.norm_ax.set_title("正規化光譜強度")
            self.norm_ax.set_xlabel("nm")
            self.norm_ax.set_ylabel("相對強度")
            
            # 計算 PPF
            total_ppf, blue_ppf, green_ppf, red_ppf = self.calculate_ppf(
                sum_data["nm"].values, sum_data["mw"].values)
            
            # 更新 PPF 顯示
            self.total_ppf_label.config(text=f"總 PPF: {total_ppf:.4f}")
            self.blue_ppf_label.config(text=f"PPF (Blue, 400-499nm): {blue_ppf:.4f}")
            self.green_ppf_label.config(text=f"PPF (Green, 500-599nm): {green_ppf:.4f}")
            self.red_ppf_label.config(text=f"PPF (Red, 600-700nm): {red_ppf:.4f}")
            
            self.sum_canvas.draw()
            self.norm_canvas.draw()

if __name__ == "__main__":
    LoginWindow()