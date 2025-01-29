import tkinter as tk
from tkinter import filedialog, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import pandas as pd

plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei']
plt.rcParams['axes.unicode_minus'] = False

class SpectrumApp:
    def __init__(self, master):
        self.master = master
        self.master.title("光譜分析工具")
        self.master.geometry("1200x900")
        
        self.num_spectra = 0
        self.spectra_data = []
        self.sum_spectrum = None
        self.normalized_spectrum = None
        
        self.create_widgets()
    
    def create_widgets(self):
        # 輸入區域
        input_frame = tk.Frame(self.master)
        input_frame.pack(pady=10)
        
        tk.Label(input_frame, text="輸入光譜數量 (1-10):").pack(side=tk.LEFT)
        self.num_entry = tk.Entry(input_frame, width=5)
        self.num_entry.pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            input_frame, 
            text="確認",
            command=self.create_spectrum_frames
        ).pack(side=tk.LEFT)
        
        # 主要內容區域
        self.main_canvas = tk.Canvas(self.master)
        self.main_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.scrollbar = tk.Scrollbar(
            self.master, 
            orient=tk.VERTICAL, 
            command=self.main_canvas.yview
        )
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.main_canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.container = tk.Frame(self.main_canvas)
        self.main_canvas.create_window((0,0), window=self.container, anchor="nw")
        
        # 初始化總結圖表
        self.summary_frame = tk.Frame(self.master)
        self.summary_fig = plt.figure(figsize=(10, 4))
        self.summary_ax1 = self.summary_fig.add_subplot(121)
        self.summary_ax2 = self.summary_fig.add_subplot(122)
        self.summary_canvas = FigureCanvasTkAgg(self.summary_fig, master=self.summary_frame)
        self.summary_canvas.get_tk_widget().pack()
    
    def create_spectrum_frames(self):
        try:
            self.num_spectra = int(self.num_entry.get())
            if not 1 <= self.num_spectra <= 10:
                raise ValueError
        except ValueError:
            messagebox.showerror("錯誤", "請輸入1-10之間的整數")
            return
        
        # 清除舊內容
        for widget in self.container.winfo_children():
            widget.destroy()
        
        self.spectra_data = []
        self.spectrum_frames = []
        
        # 創建光譜圖區域
        for i in range(self.num_spectra):
            frame = tk.Frame(self.container)
            frame.pack(pady=5, fill=tk.X)
            
            fig = plt.figure(figsize=(8, 3))
            ax = fig.add_subplot(111)
            ax.set_title(f"光譜圖 {i+1}")
            ax.set_xlabel("nm")
            ax.set_ylabel("mw")
            
            canvas = FigureCanvasTkAgg(fig, master=frame)
            canvas.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            
            btn_frame = tk.Frame(frame)
            btn_frame.pack(side=tk.RIGHT, padx=5)
            
            tk.Button(
                btn_frame,
                text="選擇檔案",
                command=lambda idx=i: self.load_file(idx)
            ).pack(pady=5)
            
            self.spectrum_frames.append({
                "fig": fig,
                "ax": ax,
                "canvas": canvas,
                "data": None
            })
        
        self.summary_frame.pack_forget()
        self.summary_frame.pack(pady=10, fill=tk.BOTH, expand=True)
        self.container.update_idletasks()
        self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all"))
    
    def load_file(self, index):
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if not file_path:
            return
        
        try:
            df = pd.read_csv(file_path, sep='\t')
            if 'nm' not in df.columns or 'mw' not in df.columns:
                raise ValueError("檔案格式錯誤")
            
            if not (df['nm'].min() == 400 and 
                    df['nm'].max() == 700 and 
                    len(df) == 301):
                raise ValueError("nm值應為400-700且步長為1")
            
            self.spectrum_frames[index]["data"] = df
            self.plot_spectrum(index, df)
            
            if all(frame["data"] is not None for frame in self.spectrum_frames):
                self.calculate_summary()
        
        except Exception as e:
            messagebox.showerror("錯誤", str(e))
    
    def plot_spectrum(self, index, df):
        ax = self.spectrum_frames[index]["ax"]
        ax.clear()
        ax.plot(df['nm'], df['mw'])
        ax.set_title(f"光譜圖 {index+1}")
        ax.set_xlabel("nm")
        ax.set_ylabel("mw")
        self.spectrum_frames[index]["canvas"].draw()
    
    def calculate_summary(self):
        sum_mw = np.zeros(301)
        
        for frame in self.spectrum_frames:
            sum_mw += frame["data"]['mw'].values
        
        self.sum_spectrum = sum_mw
        self.normalized_spectrum = sum_mw / np.max(sum_mw)
        
        self.update_summary_plots()
    
    def update_summary_plots(self):
        nm = self.spectrum_frames[0]["data"]['nm'].values
        
        self.summary_ax1.clear()
        self.summary_ax1.plot(nm, self.sum_spectrum)
        self.summary_ax1.set_title("總和光譜圖")
        self.summary_ax1.set_xlabel("nm")
        self.summary_ax1.set_ylabel("總和強度")
        
        self.summary_ax2.clear()
        self.summary_ax2.plot(nm, self.normalized_spectrum)
        self.summary_ax2.set_title("正規化總和光譜圖")
        self.summary_ax2.set_xlabel("nm")
        self.summary_ax2.set_ylabel("正規化強度")
        
        self.summary_fig.tight_layout()
        self.summary_canvas.draw()

if __name__ == "__main__":
    root = tk.Tk()
    app = SpectrumApp(root)
    root.mainloop()