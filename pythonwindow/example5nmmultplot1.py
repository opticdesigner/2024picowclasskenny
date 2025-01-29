import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
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
        self.title("多光譜分析工具")
        self.geometry("1000x800")
        
        # 設定介面字型
        self.option_add("*Font", ("Microsoft JhengHei", 10))
        
        # 初始化變數
        self.num_spectra = None
        self.spectra_data = []
        self.file_labels = []
        self.figures = []
        
        # 建立介面
        self.ask_spectra_number()
        if not self.num_spectra:
            self.destroy()
            return
        
        self.create_widgets()
        
    def ask_spectra_number(self):
        """詢問光譜數量"""
        self.num_spectra = simpledialog.askinteger(
            "光譜數量",
            "請輸入要分析的光譜數量：",
            parent=self,
            minvalue=1,
            maxvalue=10
        )
        
    def create_widgets(self):
        """建立介面元件"""
        # 主容器
        main_frame = tk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 檔案選擇區
        file_frame = tk.LabelFrame(main_frame, text="光譜檔案選擇")
        file_frame.pack(pady=10, fill=tk.X)
        
        # 建立檔案選擇按鈕
        for i in range(self.num_spectra):
            frame = tk.Frame(file_frame)
            frame.pack(fill=tk.X, pady=2)
            
            btn = tk.Button(
                frame,
                text=f"選擇光譜 {i+1}",
                command=lambda idx=i: self.select_file(idx),
                width=12
            )
            btn.pack(side=tk.LEFT)
            
            label = tk.Label(frame, text="尚未選擇檔案", width=60, anchor='w')
            label.pack(side=tk.LEFT)
            self.file_labels.append(label)
        
        # 控制按鈕區
        btn_frame = tk.Frame(main_frame)
        btn_frame.pack(pady=5)
        
        self.plot_btn = tk.Button(
            btn_frame,
            text="繪製光譜圖",
            command=self.plot_spectra,
            state=tk.DISABLED
        )
        self.plot_btn.pack(side=tk.LEFT, padx=5)
        
        # 圖表滾動區
        canvas_frame = tk.Frame(main_frame)
        canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(canvas_frame)
        scrollbar = tk.Scrollbar(canvas_frame, command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
    def select_file(self, index):
        """選擇單個光譜檔案"""
        file_path = filedialog.askopenfilename(
            title=f"選擇光譜 {index+1} 數據檔案",
            filetypes=[
                ("文字檔案", "*.txt"),
                ("CSV檔案", "*.csv"),
                ("所有檔案", "*.*")
            ]
        )
        
        if not file_path:
            return
        
        try:
            df = pd.read_csv(file_path, sep=None, engine='python')
            
            # 驗證數據格式
            if not {'nm', 'mw'}.issubset(df.columns):
                raise ValueError("缺少必要欄位")
                
            # 檢查nm數值範圍和格式
            expected_nm = list(range(400, 701))
            if not df['nm'].astype(int).equals(pd.Series(expected_nm)):
                raise ValueError("nm數值不符合規範")
                
            self.spectra_data.insert(index, df)
            self.file_labels[index].config(text=file_path)
            
            # 檢查是否全部檔案已選擇
            if len(self.spectra_data) == self.num_spectra:
                self.plot_btn.config(state=tk.NORMAL)
                
        except Exception as e:
            messagebox.showerror("錯誤", f"檔案驗證失敗：\n{str(e)}")
            self.file_labels[index].config(text="檔案無效")
            
    def plot_spectra(self):
        """繪製所有光譜圖"""
        # 清除舊圖表
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        # 繪製個別光譜
        for idx, df in enumerate(self.spectra_data):
            fig = Figure(figsize=(8, 3), dpi=100)
            ax = fig.add_subplot(111)
            
            df.plot(
                x='nm',
                y='mw',
                ax=ax,
                color=f'C{idx}',
                linewidth=1.5,
                legend=False
            )
            
            ax.set_title(f"光譜 {idx+1}", pad=10)
            ax.set_xlabel("波長 (nm)")
            ax.set_ylabel("吸收強度 (mw)")
            ax.grid(alpha=0.2)
            
            canvas = FigureCanvasTkAgg(fig, self.scrollable_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.X, pady=5)
            self.figures.append(fig)
        
        # 計算並繪製總合光譜
        sum_mw = sum(df['mw'] for df in self.spectra_data)
        total_df = pd.DataFrame({
            'nm': self.spectra_data[0]['nm'],
            'mw': sum_mw
        })
        
        total_fig = Figure(figsize=(8, 3), dpi=100)
        ax_total = total_fig.add_subplot(111)
        
        total_df.plot(
            x='nm',
            y='mw',
            ax=ax_total,
            color='red',
            linewidth=2,
            legend=False
        )
        
        ax_total.set_title("總合光譜", pad=10)
        ax_total.set_xlabel("波長 (nm)")
        ax_total.set_ylabel("總吸收強度 (mw)")
        ax_total.grid(alpha=0.2)
        
        total_canvas = FigureCanvasTkAgg(total_fig, self.scrollable_frame)
        total_canvas.draw()
        total_canvas.get_tk_widget().pack(fill=tk.X, pady=5)
        self.figures.append(total_fig)

if __name__ == "__main__":
    app = SpectrumViewer()
    app.mainloop()