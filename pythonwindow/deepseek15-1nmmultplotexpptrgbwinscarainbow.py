import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.collections import PolyCollection

plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei']
plt.rcParams['axes.unicode_minus'] = False

class StyledApp:
    def __init__(self, master):
        self.master = master
        self.master.title("高精度光譜分析工具")
        
        # 視窗設定
        window_width = 1400
        window_height = 900
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.master.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.spectrum_data = []
        self.spectrum_plots = []
        self.spectrum_scales = []
        self.create_precise_colormap()  # 創建精確顏色映射
        self.create_widgets()
    
    def create_precise_colormap(self):
        # 精確顏色節點定義
        color_bands = [
            (400, (0.5, 0, 0.5)),    # 紫色 (400nm)
            (440, (0, 0, 1)),        # 藍色 (440nm)
            (490, (0, 1, 1)),        # 青色 (490nm)
            (510, (0, 1, 0)),        # 綠色 (510nm)
            (580, (1, 1, 0)),        # 黃色 (580nm)
            (645, (1, 0.5, 0)),      # 橙色 (645nm)
            (700, (1, 0, 0))         # 紅色 (700nm)
        ]
        
        # 建立漸變色映射
        cdict = {'red': [], 'green': [], 'blue': []}
        for nm, (r, g, b) in color_bands:
            pos = (nm - 400) / 300  # 歸一化到0-1範圍
            cdict['red'].append((pos, r, r))
            cdict['green'].append((pos, g, g))
            cdict['blue'].append((pos, b, b))
        
        self.wavelength_cmap = LinearSegmentedColormap('precise_spectrum', cdict)

    def create_widgets(self):
        # 主界面佈局
        main_frame = ttk.Frame(self.master, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 標題與控制面板
        title_label = ttk.Label(main_frame, text="高精度光譜分析工具", 
                              font=('Microsoft JhengHei', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(control_frame, text="光譜數量 (1-10):", 
                font=('Microsoft JhengHei', 10)).pack(side=tk.LEFT)
        self.num_var = tk.StringVar()
        ttk.Entry(control_frame, textvariable=self.num_var, width=10).pack(side=tk.LEFT, padx=10)
        
        ttk.Button(control_frame, text="確認", command=self.validate_and_create_plots).pack(side=tk.LEFT)
        ttk.Button(control_frame, text="退出", command=self.master.quit).pack(side=tk.RIGHT)
        
        # PPF顯示
        ppf_frame = ttk.LabelFrame(main_frame, text="光量子通量分析", padding=10)
        ppf_frame.pack(fill=tk.X, pady=10)
        
        ppf_labels = [
            ('總 PPF (400-700nm):', 'total_ppf'),
            ('紫藍光 PPF (400-440nm):', 'violet_blue_ppf'),
            ('藍青光 PPF (440-490nm):', 'blue_cyan_ppf'),
            ('青綠光 PPF (490-510nm):', 'cyan_green_ppf'),
            ('綠黃光 PPF (510-580nm):', 'green_yellow_ppf'),
            ('黃橙光 PPF (580-645nm):', 'yellow_orange_ppf'),
            ('橙紅光 PPF (645-700nm):', 'orange_red_ppf')
        ]
        for text, attr in ppf_labels:
            frame = ttk.Frame(ppf_frame)
            frame.pack(fill=tk.X, pady=2)
            ttk.Label(frame, text=text, width=25).pack(side=tk.LEFT)
            label = ttk.Label(frame, text='0.0000', font=('Microsoft JhengHei', 10, 'bold'))
            label.pack(side=tk.LEFT)
            setattr(self, f'{attr}_label', label)
        
        # 光譜顯示區
        content_pane = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        content_pane.pack(fill=tk.BOTH, expand=True)
        
        # 左側個別光譜
        left_frame = ttk.Frame(content_pane)
        self.spectrum_canvas = tk.Canvas(left_frame)
        scrollbar = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=self.spectrum_canvas.yview)
        self.spectrum_frame = ttk.Frame(self.spectrum_canvas)
        self.spectrum_canvas.create_window((0,0), window=self.spectrum_frame, anchor="nw")
        self.spectrum_canvas.configure(yscrollcommand=scrollbar.set)
        self.spectrum_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        content_pane.add(left_frame)
        
        # 右側總和光譜
        right_frame = ttk.Frame(content_pane)
        self.sum_fig = Figure(figsize=(8,4), dpi=100)
        self.sum_ax = self.sum_fig.add_subplot(111)
        self.sum_canvas = FigureCanvasTkAgg(self.sum_fig, right_frame)
        self.sum_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        self.norm_fig = Figure(figsize=(8,4), dpi=100)
        self.norm_ax = self.norm_fig.add_subplot(111)
        self.norm_canvas = FigureCanvasTkAgg(self.norm_fig, right_frame)
        self.norm_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        content_pane.add(right_frame)

    def validate_and_create_plots(self):
        try:
            n = int(self.num_var.get())
            if not 1 <= n <= 10:
                raise ValueError
            
            # 初始化數據
            self.spectrum_data = [None]*n
            self.spectrum_plots.clear()
            self.spectrum_scales.clear()
            for widget in self.spectrum_frame.winfo_children():
                widget.destroy()
            
            # 創建光譜區域
            for i in range(n):
                frame = ttk.Frame(self.spectrum_frame)
                frame.pack(fill=tk.X, pady=5)
                
                # 控制面板
                control_panel = ttk.Frame(frame)
                control_panel.pack(fill=tk.X)
                ttk.Label(control_panel, text=f"光譜 {i+1}", 
                         font=('Microsoft JhengHei', 10, 'bold')).pack(side=tk.LEFT)
                
                # 倍率控制
                scale_var = tk.DoubleVar(value=1.0)
                self.spectrum_scales.append(scale_var)
                ttk.Entry(control_panel, textvariable=scale_var, width=6).pack(side=tk.RIGHT)
                ttk.Label(control_panel, text="倍率:").pack(side=tk.RIGHT)
                scale_var.trace_add('write', lambda *_, idx=i: self.update_total_spectrum())
                
                # 載入按鈕
                ttk.Button(control_panel, text="載入檔案", 
                         command=lambda idx=i: self.load_spectrum(idx)).pack(side=tk.RIGHT, padx=5)
                
                # 繪圖區
                fig = Figure(figsize=(6,2), dpi=100)
                ax = fig.add_subplot(111)
                canvas = FigureCanvasTkAgg(fig, frame)
                canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
                self.spectrum_plots.append((fig, ax, canvas))
        
        except ValueError:
            messagebox.showerror("輸入錯誤", "請輸入1到10之間的整數")

    def load_spectrum(self, index):
        filename = filedialog.askopenfilename(filetypes=[("文字檔", "*.csv")])
        if filename:
            try:
                df = pd.read_csv(filename, names=['nm', 'mw'], skiprows=1)
                self.spectrum_data[index] = df
                fig, ax, canvas = self.spectrum_plots[index]
                ax.clear()
                ax.plot(df['nm'], df['mw'], color='#2c3e50')
                ax.set_title(f"光譜 {index+1}")
                ax.set_xlabel("波長 (nm)")
                ax.set_ylabel("強度 (mW)")
                canvas.draw()
                self.update_total_spectrum()
            except Exception as e:
                messagebox.showerror("檔案錯誤", f"檔案讀取失敗: {str(e)}")

    def update_total_spectrum(self):
        self.sum_ax.clear()
        self.norm_ax.clear()
        
        # 計算加權總和
        valid_data = []
        for i, df in enumerate(self.spectrum_data):
            if df is not None:
                try:
                    scale = float(self.spectrum_scales[i].get())
                except:
                    scale = 1.0
                valid_data.append(df.copy().assign(mw=df['mw']*scale))
        
        if valid_data:
            # 合併數據
            sum_df = pd.concat(valid_data).groupby('nm', as_index=False).sum()
            sum_df = sum_df.sort_values('nm')
            x = sum_df['nm'].values
            y = sum_df['mw'].values
            
            if len(x) > 1:
                # 創建填色多邊形
                verts = []
                colors = []
                for i in range(len(x)-1):
                    # 計算每個區間的中間波長
                    mid_nm = (x[i] + x[i+1]) / 2
                    # 轉換為顏色
                    color = self.wavelength_cmap((mid_nm - 400) / 300)
                    # 建立多邊形頂點
                    verts.append([(x[i], 0), (x[i], y[i]), (x[i+1], y[i+1]), (x[i+1], 0)])
                    colors.append(color)
                
                # 繪製填色光譜
                poly = PolyCollection(
                    verts,
                    facecolors=colors,
                    edgecolors='none',
                    alpha=0.8
                )
                self.sum_ax.add_collection(poly)
                self.sum_ax.set_xlim(380, 720)
                self.sum_ax.set_ylim(0, y.max()*1.1)
                self.sum_ax.set_title("光譜強度分佈（精確填色）", pad=20)
                self.sum_ax.set_xlabel("波長 (nm)", labelpad=10)
                self.sum_ax.set_ylabel("強度 (mW)", labelpad=10)
            
            # 正規化光譜
            norm_y = y / y.max()
            self.norm_ax.plot(x, norm_y, color='#34495e', linewidth=1.5)
            self.norm_ax.fill_between(x, norm_y, color='#bdc3c7', alpha=0.3)
            self.norm_ax.set_title("正規化光譜對比", pad=15)
            self.norm_ax.set_xlabel("波長 (nm)", labelpad=10)
            self.norm_ax.set_ylabel("相對強度", labelpad=10)
            
            # 計算PPF
            self.calculate_ppf_values(x, y)
            
            self.sum_canvas.draw()
            self.norm_canvas.draw()

    def calculate_ppf_values(self, wavelengths, intensities):
        ppf = wavelengths * intensities * 0.008359 / 1000
        
        # 各波段範圍
        bands = [
            ('violet_blue', (400, 440)),
            ('blue_cyan', (440, 490)),
            ('cyan_green', (490, 510)),
            ('green_yellow', (510, 580)),
            ('yellow_orange', (580, 645)),
            ('orange_red', (645, 700))
        ]
        
        total_ppf = ppf.sum()
        self.total_ppf_label.config(text=f"{total_ppf:.4f}")
        
        for prefix, (start, end) in bands:
            mask = (wavelengths >= start) & (wavelengths < end)
            band_ppf = ppf[mask].sum()
            getattr(self, f'{prefix}_ppf_label').config(text=f"{band_ppf:.4f}")

class LoginWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("系統登入")
        self.root.geometry("320x240")
        
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(expand=True, fill=tk.BOTH)
        
        ttk.Label(main_frame, text="光譜分析系統", 
                 font=('Microsoft JhengHei', 14, 'bold')).pack(pady=10)
        
        ttk.Label(main_frame, text="使用者名稱:").pack()
        self.username = ttk.Entry(main_frame)
        self.username.pack()
        
        ttk.Label(main_frame, text="密碼:").pack(pady=(10,0))
        self.password = ttk.Entry(main_frame, show="•")
        self.password.pack()
        
        ttk.Button(main_frame, text="登入", 
                  command=self.check_login, style='TButton').pack(pady=15)
        
        self.root.mainloop()
    
    def check_login(self):
        if datetime.now() > datetime(2025, 3, 29):
            messagebox.showerror("授權到期", "系統已過期，請聯繫技術支援")
            return
        
        if self.username.get() == "WSL" and self.password.get() == "50968758":
            self.root.destroy()
            root = tk.Tk()
            StyledApp(root)
            root.mainloop()
        else:
            messagebox.showerror("登入失敗", "帳號或密碼錯誤")

if __name__ == "__main__":
    LoginWindow()