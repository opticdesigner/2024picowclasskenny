import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib import rcParams

# 設定中文字型
rcParams['font.sans-serif'] = ['Microsoft JhengHei']
rcParams['axes.unicode_minus'] = False

class SpectrumViewer(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("光譜數據分析工具")
        self.geometry("800x600")
        
        # 設定介面字型
        self.option_add("*Font", ("Microsoft JhengHei", 10))
        
        self.create_widgets()
        self.setup_plot()

    def create_widgets(self):
        # 建立按鈕框架
        button_frame = tk.Frame(self)
        button_frame.pack(pady=10)
        
        # 檔案載入按鈕
        self.load_btn = tk.Button(
            button_frame,
            text="載入數據檔案",
            command=self.load_file,
            width=15
        )
        self.load_btn.pack(side=tk.LEFT, padx=5)

    def setup_plot(self):
        # 初始化繪圖區域
        self.figure = Figure(figsize=(6, 4), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, master=self)
        self.canvas.get_tk_widget().pack(
            side=tk.TOP, 
            fill=tk.BOTH, 
            expand=True
        )

    def load_file(self):
        # 開啟檔案對話框
        file_path = filedialog.askopenfilename(
            title="選擇數據檔案",
            filetypes=[
                ("文字檔案", "*.txt"),
                ("CSV檔案", "*.csv"),
                ("所有檔案", "*.*")
            ]
        )
        
        if not file_path:
            return

        try:
            # 自動檢測分隔符讀取檔案
            df = pd.read_csv(file_path, sep=None, engine='python')
        except Exception as e:
            messagebox.showerror("錯誤", f"檔案讀取失敗:\n{str(e)}")
            return

        # 驗證數據格式
        if not {'nm', 'mw'}.issubset(df.columns):
            messagebox.showerror("錯誤", "檔案缺少必要的 'nm' 或 'mw' 欄位")
            return

        # 檢查nm數值範圍
        nm_values = df['nm'].astype(int)
        if not (nm_values.min() >= 400 and nm_values.max() <= 700):
            messagebox.showwarning(
                "警告",
                "nm數值超出正常範圍 (400-700)"
            )

        # 清除舊圖表並繪製新數據
        self.ax.clear()
        df.plot(
            x='nm',
            y='mw',
            ax=self.ax,
            color='blue',
            linewidth=2,
            legend=False
        )
        
        # 設定圖表格式
        self.ax.set_title("光譜吸收曲線", pad=20)
        self.ax.set_xlabel("波長 (nm)", labelpad=10)
        self.ax.set_ylabel("吸收強度 (mw)", labelpad=10)
        self.ax.grid(True, alpha=0.3)
        
        # 更新畫布
        self.canvas.draw()

if __name__ == "__main__":
    app = SpectrumViewer()
    app.mainloop()