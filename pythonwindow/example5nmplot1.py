import tkinter as tk
from tkinter import filedialog
import pandas as pd
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class SpectrumViewer:
    def __init__(self, master):
        self.master = master
        master.title("光譜數據查看器")
        master.geometry("800x600")

        # 創建UI元素
        self.create_widgets()
        
        # 初始化圖表
        self.fig = Figure(figsize=(7, 5), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=master)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def create_widgets(self):
        # 創建按鈕框架
        button_frame = tk.Frame(self.master)
        button_frame.pack(pady=10)

        # 文件選擇按鈕
        self.open_button = tk.Button(
            button_frame,
            text="打開文件",
            command=self.load_file,
            width=15,
            height=2
        )
        self.open_button.pack(side=tk.LEFT, padx=5)

    def load_file(self):
        file_types = [
            ("文本文件", "*.txt"),
            #("CSV文件", "*.csv"),
            ("所有文件", "*.*")
        ]
        
        file_path = filedialog.askopenfilename(filetypes=file_types)
        if not file_path:
            return

        try:
            # 自動檢測分隔符讀取文件
            df = pd.read_csv(file_path, sep=None, engine='python')
            df.columns = df.columns.str.strip().str.lower()

            # 驗證數據格式
            if not {'nm', 'mw'}.issubset(df.columns):
                raise ValueError("缺少必要的列: 'nm' 或 'mw'")

            # 準備數據
            x = df['nm']
            y = df['mw']

            # 繪製圖表
            self.ax.clear()
            self.ax.plot(x, y, color='blue', linewidth=2)
            self.ax.set_xlabel("Wavelength (nm)", fontsize=12)
            self.ax.set_ylabel("Intensity (mw)", fontsize=12)
            self.ax.set_title("Spectrum", fontsize=14)
            self.ax.grid(True, linestyle='--', alpha=0.7)
            
            # 設置坐標軸範圍
            self.ax.set_xlim(400, 700)
            self.ax.set_ylim(y.min()*0.9, y.max()*1.1)
            
            self.canvas.draw()

        except Exception as e:
            tk.messagebox.showerror("錯誤", f"文件讀取失敗: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = SpectrumViewer(root)
    root.mainloop()