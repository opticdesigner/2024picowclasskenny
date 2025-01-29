import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import numpy as np
import sys

class SpectrumAnalyzer:
    def __init__(self, root):
        self.root = root
        self.root.title("光譜分析器")
        self.root.geometry("1200x800")
        
        # 設定 Tkinter 字型
        default_font = ('Microsoft JhengHei UI', 10)  # 使用微軟正黑體
        self.style = ttk.Style()
        self.style.configure('.', font=default_font)
        
        # 設定 Matplotlib 字型
        plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei']  # 設定中文字型
        plt.rcParams['axes.unicode_minus'] = False  # 讓負號正確顯示
        plt.rcParams['font.family'] = 'sans-serif'  # 設定字型家族
        
        # 儲存數據的變數
        self.spectrum_data = []
        self.n_spectrums = 0
        
        self.create_input_frame()
        
    def create_input_frame(self):
        # 輸入框架
        input_frame = ttk.Frame(self.root)
        input_frame.pack(pady=10)
        
        ttk.Label(input_frame, text="請輸入光譜數量 (1-10):", 
                 font=('Microsoft JhengHei UI', 10)).pack(side=tk.LEFT)
        self.n_entry = ttk.Entry(input_frame, width=10)
        self.n_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(input_frame, text="確認", 
                  command=self.create_plots).pack(side=tk.LEFT)
        
    def create_plots(self):
        try:
            n = int(self.n_entry.get())
            if not 1 <= n <= 10:
                raise ValueError("數量必須在1到10之間")
            
            # 清除現有圖表
            for widget in self.root.winfo_children()[1:]:
                widget.destroy()
            
            self.n_spectrums = n
            self.spectrum_data = []
            
            # 創建圖表框架
            plots_frame = ttk.Frame(self.root)
            plots_frame.pack(fill=tk.BOTH, expand=True)
            
            # 創建網格佈局
            rows = (n + 3) // 2  # 包括總和圖和正規化圖
            cols = 2
            
            # 創建個別光譜圖
            self.figures = []
            self.canvases = []
            
            for i in range(n):
                fig, ax = plt.subplots(figsize=(6, 4))
                ax.set_title(f"光譜 {i+1}", fontproperties='Microsoft JhengHei')
                ax.set_xlabel("波長 (nm)", fontproperties='Microsoft JhengHei')
                ax.set_ylabel("強度 (mw)", fontproperties='Microsoft JhengHei')
                
                frame = ttk.Frame(plots_frame)
                frame.grid(row=i//2, column=i%2, padx=5, pady=5)
                
                canvas = FigureCanvasTkAgg(fig, frame)
                canvas.draw()
                canvas.get_tk_widget().pack()
                
                ttk.Button(frame, text="讀取檔案", 
                          command=lambda idx=i: self.load_file(idx)).pack()
                
                self.figures.append((fig, ax))
                self.canvases.append(canvas)
            
            # 創建總和圖
            sum_fig, sum_ax = plt.subplots(figsize=(6, 4))
            sum_ax.set_title("總和光譜圖", fontproperties='Microsoft JhengHei')
            sum_ax.set_xlabel("波長 (nm)", fontproperties='Microsoft JhengHei')
            sum_ax.set_ylabel("強度 (mw)", fontproperties='Microsoft JhengHei')
            
            sum_frame = ttk.Frame(plots_frame)
            sum_frame.grid(row=rows-2, column=0, padx=5, pady=5)
            
            sum_canvas = FigureCanvasTkAgg(sum_fig, sum_frame)
            sum_canvas.draw()
            sum_canvas.get_tk_widget().pack()
            
            self.sum_fig = sum_fig
            self.sum_ax = sum_ax
            self.sum_canvas = sum_canvas
            
            # 創建正規化圖
            norm_fig, norm_ax = plt.subplots(figsize=(6, 4))
            norm_ax.set_title("正規化光譜圖", fontproperties='Microsoft JhengHei')
            norm_ax.set_xlabel("波長 (nm)", fontproperties='Microsoft JhengHei')
            norm_ax.set_ylabel("相對強度", fontproperties='Microsoft JhengHei')
            
            norm_frame = ttk.Frame(plots_frame)
            norm_frame.grid(row=rows-2, column=1, padx=5, pady=5)
            
            norm_canvas = FigureCanvasTkAgg(norm_fig, norm_frame)
            norm_canvas.draw()
            norm_canvas.get_tk_widget().pack()
            
            self.norm_fig = norm_fig
            self.norm_ax = norm_ax
            self.norm_canvas = norm_canvas
            
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
    # 設定默認編碼為 UTF-8
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    
    root = tk.Tk()
    app = SpectrumAnalyzer(root)
    root.mainloop()