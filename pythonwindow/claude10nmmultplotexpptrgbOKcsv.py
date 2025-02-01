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

class StyledApp:
    def __init__(self, master):
        self.master = master
        self.master.title("科學光譜分析工具")
        
        # 視窗大小和置中
        window_width = 1400
        window_height = 900
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.master.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # 設定主題
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # 初始化數據存儲
        self.spectrum_data = []
        self.spectrum_plots = []
        
        self.create_widgets()
    
    def create_widgets(self):
        # 主框架
        main_frame = ttk.Frame(self.master, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 標題
        title_label = ttk.Label(
            main_frame, 
            text="科學光譜分析工具", 
            font=('Microsoft JhengHei', 16, 'bold')
        )
        title_label.pack(pady=(0, 20))
        
        # 輸入區域
        input_frame = ttk.Frame(main_frame)
        input_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(input_frame, text="光譜數量 (1-10):", font=('Microsoft JhengHei', 10)).pack(side=tk.LEFT, padx=(0, 10))
        
        # 數量輸入框
        self.num_var = tk.StringVar()
        num_entry = ttk.Entry(
            input_frame, 
            width=10, 
            textvariable=self.num_var,
            font=('Microsoft JhengHei', 10)
        )
        num_entry.pack(side=tk.LEFT, padx=(0, 10))
        
        # 按鈕框
        button_frame = ttk.Frame(input_frame)
        button_frame.pack(side=tk.LEFT, expand=True)
        
        confirm_btn = ttk.Button(
            button_frame, 
            text="確認",
            command=self.validate_and_create_plots,
            style='Success.TButton'
        )
        confirm_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        exit_btn = ttk.Button(
            button_frame, 
            text="退出",
            command=self.master.quit,
            style='Danger.TButton'
        )
        exit_btn.pack(side=tk.LEFT)
        
        # 自定義按鈕樣式
        self.style.configure('Success.TButton', background='#4CAF50', foreground='white')
        self.style.configure('Danger.TButton', background='#f44336', foreground='white')
        
        # PPF 顯示框
        self.ppf_frame = ttk.LabelFrame(main_frame, text="PPF 分析結果", padding=10)
        self.ppf_frame.pack(fill=tk.X, pady=10)
        
        # PPF 標籤
        ppf_labels = [
            ('總 PPF:', 'total_ppf'), 
            ('藍光區 PPF (400-499nm):', 'blue_ppf'),
            ('綠光區 PPF (500-599nm):', 'green_ppf'),
            ('紅光區 PPF (600-700nm):', 'red_ppf')
        ]
        
        for text, attr in ppf_labels:
            frame = ttk.Frame(self.ppf_frame)
            frame.pack(fill=tk.X, pady=2)
            
            ttk.Label(frame, text=text, width=25).pack(side=tk.LEFT)
            label = ttk.Label(frame, text='尚未計算', font=('Microsoft JhengHei', 10, 'bold'))
            label.pack(side=tk.LEFT, expand=True, fill=tk.X)
            
            setattr(self, f'{attr}_label', label)
        
        # 主內容區
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # 左側區域（個別光譜）
        left_frame = ttk.Frame(content_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        ttk.Label(left_frame, text="個別光譜", font=('Microsoft JhengHei', 12, 'bold')).pack()
        
        # 可捲動的光譜區域
        self.spectrum_canvas = tk.Canvas(left_frame)
        scrollbar = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=self.spectrum_canvas.yview)
        
        self.spectrum_frame = ttk.Frame(self.spectrum_canvas)
        self.spectrum_frame.bind("<Configure>", 
            lambda e: self.spectrum_canvas.configure(scrollregion=self.spectrum_canvas.bbox("all"))
        )
        
        self.spectrum_canvas.create_window((0, 0), window=self.spectrum_frame, anchor="nw")
        self.spectrum_canvas.configure(yscrollcommand=scrollbar.set)
        
        self.spectrum_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 右側區域（總和光譜）
        right_frame = ttk.Frame(content_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        ttk.Label(right_frame, text="總和光譜", font=('Microsoft JhengHei', 12, 'bold')).pack()
        
        # 總和光譜佔位
        self.total_spectrum_frame = ttk.Frame(right_frame)
        self.total_spectrum_frame.pack(fill=tk.BOTH, expand=True)
        
        # 總和光譜和正規化光譜的圖表
        self.create_total_spectrum_plots()
    
    def create_total_spectrum_plots(self):
        # 總和光譜
        self.sum_fig = Figure(figsize=(8, 4), dpi=100)
        self.sum_ax = self.sum_fig.add_subplot(111)
        self.sum_ax.set_title("光譜強度總和")
        self.sum_ax.set_xlabel("波長 (nm)")
        self.sum_ax.set_ylabel("強度 (mW)")
        
        self.sum_canvas = FigureCanvasTkAgg(self.sum_fig, self.total_spectrum_frame)
        self.sum_canvas.draw()
        self.sum_canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        # 正規化光譜
        self.norm_fig = Figure(figsize=(8, 4), dpi=100)
        self.norm_ax = self.norm_fig.add_subplot(111)
        self.norm_ax.set_title("正規化光譜強度")
        self.norm_ax.set_xlabel("波長 (nm)")
        self.norm_ax.set_ylabel("相對強度")
        
        self.norm_canvas = FigureCanvasTkAgg(self.norm_fig, self.total_spectrum_frame)
        self.norm_canvas.draw()
        self.norm_canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
    
    def validate_and_create_plots(self):
        # 清除之前的數據和圖表
        self.spectrum_data.clear()
        self.spectrum_plots.clear()
        
        for widget in self.spectrum_frame.winfo_children():
            widget.destroy()
        
        try:
            n = int(self.num_var.get())
            if not 1 <= n <= 10:
                raise ValueError
            
            # 創建 n 個光譜區域
            for i in range(n):
                self.create_spectrum_area(i)
            
        except ValueError:
            messagebox.showerror("錯誤", "請輸入1-10之間的整數！")
    
    def create_spectrum_area(self, index):
        # 為每個光譜創建一個框架
        frame = ttk.Frame(self.spectrum_frame)
        frame.pack(fill=tk.X, pady=5, padx=5)
        
        # 光譜標題
        ttk.Label(frame, text=f"光譜 {index+1}", 
                  font=('Microsoft JhengHei', 10, 'bold')).pack(side=tk.TOP)
        
        # 讀取檔案按鈕
        read_btn = ttk.Button(frame, text="載入光譜", 
            command=lambda idx=index: self.load_spectrum(idx))
        read_btn.pack(side=tk.BOTTOM, pady=5)
        
        # 預留繪圖區域
        fig = Figure(figsize=(6, 3), dpi=100)
        ax = fig.add_subplot(111)
        ax.set_title(f"光譜 {index+1}")
        ax.set_xlabel("波長 (nm)")
        ax.set_ylabel("強度 (mW)")
        
        canvas = FigureCanvasTkAgg(fig, frame)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        
        # 儲存圖表物件
        self.spectrum_plots.append((fig, ax, canvas, frame))
        # 初始化對應的數據為 None
        self.spectrum_data.append(None)
    
    def load_spectrum(self, index):
        filename = filedialog.askopenfilename(
            title="選擇光譜檔案",
            filetypes=[("文字檔", "*.txt"), ("所有檔案", "*.*")]
        )
        
        if filename:
            try:
                # 讀取檔案
                df = pd.read_csv(filename)
                
                # 驗證數據格式
                if "nm" not in df.columns or "mw" not in df.columns:
                    raise ValueError("檔案格式錯誤！必須包含 'nm' 和 'mw' 欄位")
                
                # 儲存數據
                self.spectrum_data[index] = df
                
                # 獲取對應的圖表
                fig, ax, canvas, frame = self.spectrum_plots[index]
                
                # 清除之前的圖表
                ax.clear()
                
                # 繪製光譜
                ax.plot(df["nm"], df["mw"])
                ax.set_title(f"光譜 {index+1}")
                ax.set_xlabel("波長 (nm)")
                ax.set_ylabel("強度 (mW)")
                
                # 更新圖表
                canvas.draw()
                
                # 更新總和光譜
                self.update_total_spectrum()
                
            except Exception as e:
                messagebox.showerror("錯誤", str(e))
    
    def update_total_spectrum(self):
        # 清除之前的圖表
        self.sum_ax.clear()
        self.norm_ax.clear()
        
        # 篩選有效數據
        valid_data = [d for d in self.spectrum_data if d is not None]
        
        if valid_data:
            # 計算總和光譜
            sum_data = valid_data[0].copy()
            sum_data["mw"] = sum_data["mw"] * 0  # 初始化歸零
            
            # 累加每個光譜的強度
            for df in valid_data:
                sum_data["mw"] += df["mw"]
            
            # 繪製總和光譜
            self.sum_ax.plot(sum_data["nm"], sum_data["mw"])
            self.sum_ax.set_title("光譜強度總和")
            self.sum_ax.set_xlabel("波長 (nm)")
            self.sum_ax.set_ylabel("強度 (mW)")
            
            # 計算並繪製正規化光譜
            norm_data = sum_data.copy()
            norm_data["mw"] = norm_data["mw"] / norm_data["mw"].max()
            
            self.norm_ax.plot(norm_data["nm"], norm_data["mw"])
            self.norm_ax.set_title("正規化光譜強度")
            self.norm_ax.set_xlabel("波長 (nm)")
            self.norm_ax.set_ylabel("相對強度")
            
            # 更新圖表
            self.sum_canvas.draw()
            self.norm_canvas.draw()
            
            # 計算 PPF
            total_ppf, blue_ppf, green_ppf, red_ppf = self.calculate_ppf(
                sum_data["nm"].values, sum_data["mw"].values)
            
            # 更新 PPF 顯示
            self.total_ppf_label.config(text=f"{total_ppf:.4f}")
            self.blue_ppf_label.config(text=f"{blue_ppf:.4f}")
            self.green_ppf_label.config(text=f"{green_ppf:.4f}")
            self.red_ppf_label.config(text=f"{red_ppf:.4f}")

    # 修正重點：將 calculate_ppf 定義在類別內部
    def calculate_ppf(self, wavelengths, intensities):
        # PPF 計算公式：ppf(n) = n * mw * 0.008359 / 1000.0
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

# 登入視窗類別
class LoginWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Copyright (c) 2025 Steve Li")
        
        # 視窗置中
        window_width = 350
        window_height = 250
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # 建立登入框架
        frame = ttk.Frame(self.root, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # 標題
        ttk.Label(
            frame, 
            text="光譜分析工具", 
            font=('Microsoft JhengHei', 16, 'bold')
        ).pack(pady=(0, 20))
        
        # 使用者名稱
        ttk.Label(frame, text="使用者名稱:", font=('Microsoft JhengHei', 10)).pack(fill=tk.X)
        self.username = ttk.Entry(frame, font=('Microsoft JhengHei', 10))
        self.username.pack(fill=tk.X, pady=(0, 10))
        
        # 密碼
        ttk.Label(frame, text="密碼:", font=('Microsoft JhengHei', 10)).pack(fill=tk.X)
        self.password = ttk.Entry(frame, show="*", font=('Microsoft JhengHei', 10))
        self.password.pack(fill=tk.X, pady=(0, 20))
        
        # 登入按鈕
        login_btn = ttk.Button(
            frame, 
            text="登入", 
            command=self.check_login,
            style='Success.TButton'
        )
        login_btn.pack(fill=tk.X)
        
        # 按鈕樣式
        style = ttk.Style()
        style.configure('Success.TButton', background='#4CAF50', foreground='#2C3E50')
        
        self.root.mainloop()
    
    def check_login(self):
        # 檢查日期限制
        if datetime.now() > datetime(2025, 3, 29):
            messagebox.showerror("錯誤", "已經超過使用期限,請聯繫Steve Li")
            return
        
        if self.username.get() == "WSL" and self.password.get() == "50968758":
            self.root.destroy()
            root = tk.Tk()
            StyledApp(root)
            root.mainloop()
        else:
            messagebox.showerror("錯誤", "使用者名稱或密碼錯誤！")

# 程式入口
if __name__ == "__main__":
    LoginWindow()