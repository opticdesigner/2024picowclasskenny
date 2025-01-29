import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import numpy as np
import sys
from datetime import datetime

def check_expiration():
    """檢查程式是否過期"""
    expiration_date = datetime(2025, 3, 19)
    current_date = datetime.now()
    
    if current_date > expiration_date:
        root = tk.Tk()
        root.withdraw()  # 隱藏主窗口
        messagebox.showerror("錯誤", "已經超過使用期限,請聯繫Steve Li")
        sys.exit(1)

class SpectrumAnalyzer:
    def __init__(self, root):
        self.root = root
        self.root.title("光譜分析器")
        self.root.geometry("1200x800")
        
        # 設定 Tkinter 字型
        default_font = ('Microsoft JhengHei UI', 10)
        self.style = ttk.Style()
        self.style.configure('.', font=default_font)
        
        # 設定 Matplotlib 字型
        plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei']
        plt.rcParams['axes.unicode_minus'] = False
        plt.rcParams['font.family'] = 'sans-serif'
        
        # 儲存數據的變數
        self.spectrum_data = []
        self.n_spectrums = 0
        
        # 建立主框架
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 建立輸入區域
        self.create_input_frame()
        
        # 建立捲動區域
        self.create_scrollable_frame()

    # [rest of the class implementation remains the same as before...]
    
    def create_input_frame(self):
        # 輸入框架
        input_frame = ttk.Frame(self.main_frame)
        input_frame.pack(pady=10, fill=tk.X)
        
        ttk.Label(input_frame, text="請輸入光譜數量 (1-10):", 
                 font=('Microsoft JhengHei UI', 10)).pack(side=tk.LEFT, padx=5)
        self.n_entry = ttk.Entry(input_frame, width=10)
        self.n_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(input_frame, text="確認", 
                  command=self.create_plots).pack(side=tk.LEFT, padx=5)
    
    def create_scrollable_frame(self):
        # 建立捲動容器
        self.canvas = tk.Canvas(self.main_frame)
        scrollbar = ttk.Scrollbar(self.main_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        # 配置捲動
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        # 在畫布上創建視窗
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        # 配置滾輪捲動
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        
        # 放置捲動元件
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
    def create_plots(self):
        try:
            n = int(self.n_entry.get())
            if not 1 <= n <= 10:
                raise ValueError("數量必須在1到10之間")
            
            # 清除現有圖表
            for widget in self.scrollable_frame.winfo_children():
                widget.destroy()
            
            self.n_spectrums = n
            self.spectrum_data = []
            
            # 創建個別光譜圖
            self.figures = []
            self.canvases = []
            
            # 為每個光譜圖創建框架
            for i in range(n):
                frame = ttk.Frame(self.scrollable_frame)
                frame.pack(pady=10, padx=10, fill=tk.X)
                
                fig, ax = plt.subplots(figsize=(10, 4))
                ax.set_title(f"光譜 {i+1}", fontproperties='Microsoft JhengHei')
                ax.set_xlabel("波長 (nm)", fontproperties='Microsoft JhengHei')
                ax.set_ylabel("強度 (mw)", fontproperties='Microsoft JhengHei')
                
                canvas = FigureCanvasTkAgg(fig, frame)
                canvas.draw()
                canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
                
                ttk.Button(frame, text="讀取檔案", 
                          command=lambda idx=i: self.load_file(idx)).pack(pady=5)
                
                self.figures.append((fig, ax))
                self.canvases.append(canvas)
            
            # 創建總和圖和正規化圖的框架
            summary_frame = ttk.Frame(self.scrollable_frame)
            summary_frame.pack(pady=10, padx=10, fill=tk.X)
            
            # 總和圖
            sum_fig, sum_ax = plt.subplots(figsize=(10, 4))
            sum_ax.set_title("總和光譜圖", fontproperties='Microsoft JhengHei')
            sum_ax.set_xlabel("波長 (nm)", fontproperties='Microsoft JhengHei')
            sum_ax.set_ylabel("強度 (mw)", fontproperties='Microsoft JhengHei')
            
            self.sum_canvas = FigureCanvasTkAgg(sum_fig, summary_frame)
            self.sum_canvas.draw()
            self.sum_canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True, pady=10)
            
            self.sum_fig = sum_fig
            self.sum_ax = sum_ax
            
            # 正規化圖
            norm_fig, norm_ax = plt.subplots(figsize=(10, 4))
            norm_ax.set_title("正規化光譜圖", fontproperties='Microsoft JhengHei')
            norm_ax.set_xlabel("波長 (nm)", fontproperties='Microsoft JhengHei')
            norm_ax.set_ylabel("相對強度", fontproperties='Microsoft JhengHei')
            
            self.norm_canvas = FigureCanvasTkAgg(norm_fig, summary_frame)
            self.norm_canvas.draw()
            self.norm_canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
            
            self.norm_fig = norm_fig
            self.norm_ax = norm_ax
            
        except ValueError as e:
            tk.messagebox.showerror("錯誤", str(e))
            
    def load_file(self, idx):
        filename = filedialog.askopenfilename(
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        
        if filename:
            try:
                # 讀取數據
                data = pd.read_csv(filename, delimiter='\s+')
                
                # 確保數據格式正確
                if 'nm' not in data.columns or 'mw' not in data.columns:
                    raise ValueError("檔案格式錯誤：需要 'nm' 和 'mw' 欄位")
                
                # 更新對應的圖表
                fig, ax = self.figures[idx]
                ax.clear()
                ax.plot(data['nm'], data['mw'])
                ax.set_title(f"光譜 {idx+1}", fontproperties='Microsoft JhengHei')
                ax.set_xlabel("波長 (nm)", fontproperties='Microsoft JhengHei')
                ax.set_ylabel("強度 (mw)", fontproperties='Microsoft JhengHei')
                self.canvases[idx].draw()
                
                # 儲存數據
                if len(self.spectrum_data) <= idx:
                    self.spectrum_data.append(data)
                else:
                    self.spectrum_data[idx] = data
                
                # 更新總和圖和正規化圖
                self.update_sum_plot()
                self.update_normalized_plot()
                
            except Exception as e:
                tk.messagebox.showerror("錯誤", f"讀取檔案時發生錯誤：{str(e)}")
    
    def update_sum_plot(self):
        if not self.spectrum_data:
            return
            
        self.sum_ax.clear()
        sum_data = pd.DataFrame({'nm': self.spectrum_data[0]['nm'], 'mw': 0})
        
        for data in self.spectrum_data:
            sum_data['mw'] += data['mw']
        
        self.sum_ax.plot(sum_data['nm'], sum_data['mw'])
        self.sum_ax.set_title("總和光譜圖", fontproperties='Microsoft JhengHei')
        self.sum_ax.set_xlabel("波長 (nm)", fontproperties='Microsoft JhengHei')
        self.sum_ax.set_ylabel("強度 (mw)", fontproperties='Microsoft JhengHei')
        self.sum_canvas.draw()
        
    def update_normalized_plot(self):
        if not self.spectrum_data:
            return
            
        self.norm_ax.clear()
        sum_data = pd.DataFrame({'nm': self.spectrum_data[0]['nm'], 'mw': 0})
        
        for data in self.spectrum_data:
            sum_data['mw'] += data['mw']
            
        # 正規化
        normalized_data = sum_data.copy()
        normalized_data['mw'] = normalized_data['mw'] / normalized_data['mw'].max()
        
        self.norm_ax.plot(normalized_data['nm'], normalized_data['mw'])
        self.norm_ax.set_title("正規化光譜圖", fontproperties='Microsoft JhengHei')
        self.norm_ax.set_xlabel("波長 (nm)", fontproperties='Microsoft JhengHei')
        self.norm_ax.set_ylabel("相對強度", fontproperties='Microsoft JhengHei')
        self.norm_canvas.draw()

if __name__ == "__main__":
    # 檢查過期日期
    check_expiration()
    
    # 設定默認編碼為 UTF-8
    sys.stdout.reconfigure(encoding='utf-8')
    
    root = tk.Tk()
    app = SpectrumAnalyzer(root)
    root.mainloop()