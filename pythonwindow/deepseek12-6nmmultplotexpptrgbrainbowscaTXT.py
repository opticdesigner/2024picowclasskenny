import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.path import Path
from matplotlib.patches import PathPatch
import numpy as np

# 全局樣式設定
BG_COLOR = "#F0F0F0"
PRIMARY_COLOR = "#2C3E50"
SECONDARY_COLOR = "#3498DB"
ACCENT_COLOR = "#E74C3C"
TEXT_COLOR = "#2C3E50"

def wavelength_to_rgb(wavelength, gamma=0.8):
    """精確對應可見光譜顏色分布（400-700nm）"""
    wavelength = float(wavelength)
    if wavelength < 400: wavelength = 400
    if wavelength > 700: wavelength = 700
    
    red = green = blue = 0.0
    
    # 分段顏色計算
    if 400 <= wavelength < 440:
        red = -(wavelength - 440) / 40
        blue = 1.0
    elif 440 <= wavelength < 490:
        green = (wavelength - 440) / 50
        blue = 1.0
    elif 490 <= wavelength < 510:
        green = 1.0
        blue = -(wavelength - 510) / 20
    elif 510 <= wavelength < 580:
        red = (wavelength - 510) / 70
        green = 1.0
    elif 580 <= wavelength < 645:
        red = 1.0
        green = -(wavelength - 645) / 65
    elif 645 <= wavelength <= 700:
        red = 1.0

    # 強度衰減調整（400-420nm）
    attenuation = 1.0
    if 400 <= wavelength < 420:
        attenuation = 0.3 + 0.7 * (wavelength - 400) / 20

    # Gamma校正
    rgb = (
        np.clip((red * attenuation)**gamma, 0, 1),
        np.clip((green * attenuation)**gamma, 0, 1),
        np.clip((blue * attenuation)**gamma, 0, 1)
    )
    
    return rgb

# 創建自定義顏色映射
cmap_colors = [wavelength_to_rgb(w) for w in np.linspace(400, 700, 512)]
spectrum_cmap = plt.matplotlib.colors.LinearSegmentedColormap.from_list("spectrum", cmap_colors)

def check_expiration():
    """檢查軟件使用期限"""
    expire_date = datetime(2025, 3, 29)
    if datetime.now() > expire_date:
        messagebox.showerror("錯誤", "已經超過使用期限，請聯繫Steve Li")
        return False
    return True

class LoginWindow:
    """登入窗口類別"""
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("登入")
        self.root.geometry("400x250")
        self.root.configure(bg=PRIMARY_COLOR)
        
        self.setup_style()
        self.create_widgets()

    def setup_style(self):
        """設定登入界面樣式"""
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TLabel', background=PRIMARY_COLOR, foreground='white', font=('Microsoft JhengHei', 12))
        style.configure('TEntry', font=('Microsoft JhengHei', 12), padding=5)
        style.configure('TButton', font=('Microsoft JhengHei', 12, 'bold'), 
                       background=SECONDARY_COLOR, foreground='white', padding=10)

    def create_widgets(self):
        """創建登入界面組件"""
        login_frame = ttk.Frame(self.root)
        login_frame.pack(pady=40, padx=20, fill=tk.BOTH, expand=True)
        
        ttk.Label(login_frame, text="光譜分析系統", font=('Microsoft JhengHei', 16, 'bold')).pack(pady=10)
        
        ttk.Label(login_frame, text="使用者名稱:").pack(pady=5)
        self.username_entry = ttk.Entry(login_frame)
        self.username_entry.pack()
        
        ttk.Label(login_frame, text="密碼:").pack(pady=5)
        self.password_entry = ttk.Entry(login_frame, show="*")
        self.password_entry.pack()
        
        ttk.Button(login_frame, text="登入", command=self.check_credentials).pack(pady=20)

    def check_credentials(self):
        """驗證登入信息"""
        try:
            if self.username_entry.get() == "WSL" and self.password_entry.get() == "50968758":
                self.root.destroy()
                main_window = MainWindow()
                main_window.run()
            else:
                messagebox.showerror("錯誤", "使用者名稱或密碼錯誤")
        except Exception as e:
            messagebox.showerror("系統錯誤", f"發生未預期錯誤: {str(e)}")

class MainWindow:
    """主應用程序窗口類別"""
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("光譜分析工具 - 專業版")
        self.root.geometry("1280x800")
        self.root.configure(bg=BG_COLOR)
        
        self.setup_style()
        self.spectra_data = []
        self.figures = []
        self.canvases = []
        self.scale_entries = []  # 新增：存儲倍率輸入框
        self.current_n = 0
        
        self.create_widgets()
        self.root.protocol("WM_DELETE_WINDOW", self.exit_program)

    def setup_style(self):
        """設定主界面樣式"""
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('.', background=BG_COLOR, foreground=TEXT_COLOR)
        style.configure('TFrame', background=BG_COLOR)
        style.configure('TLabel', font=('Microsoft JhengHei', 10), background=BG_COLOR)
        style.configure('TButton', font=('Microsoft JhengHei', 10, 'bold'), 
                       background=SECONDARY_COLOR, foreground='white', borderwidth=0)
        style.map('TButton', background=[('active', PRIMARY_COLOR)])
        style.configure('TLabelframe', background=BG_COLOR, relief='groove')
        style.configure('TLabelframe.Label', background=BG_COLOR, foreground=PRIMARY_COLOR)
        style.configure('TEntry', relief='flat', padding=5)

    def create_widgets(self):
        """創建主界面組件"""
        # 控制面板
        control_frame = ttk.Frame(self.root, padding=(20, 10))
        control_frame.pack(fill=tk.X)
        
        ttk.Label(control_frame, text="光譜數量 (1-10):", font=('Microsoft JhengHei', 11)).pack(side=tk.LEFT, padx=10)
        self.n_entry = ttk.Entry(control_frame, width=5, font=('Microsoft JhengHei', 11))
        self.n_entry.pack(side=tk.LEFT)
        
        ttk.Button(control_frame, text="生成圖表", command=self.generate_plots).pack(side=tk.LEFT, padx=20)
        ttk.Button(control_frame, text="更新倍率", command=self.update_scales).pack(side=tk.LEFT, padx=10)  # 新增：更新倍率按鈕
        ttk.Button(control_frame, text="退出系統", command=self.exit_program).pack(side=tk.RIGHT)

        # 主內容區域
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # 左側滾動區域
        self.left_canvas = tk.Canvas(main_frame, bg=BG_COLOR, highlightthickness=0)
        self.left_scroll = ttk.Scrollbar(main_frame, orient="vertical", command=self.left_canvas.yview)
        self.left_frame = ttk.Frame(self.left_canvas)
        
        self.left_canvas.configure(yscrollcommand=self.left_scroll.set)
        self.left_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.left_scroll.pack(side=tk.LEFT, fill=tk.Y)
        self.left_canvas.create_window((0,0), window=self.left_frame, anchor="nw")

        # 右側資訊面板
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=10)

        # 圖表區域
        chart_frame = ttk.Frame(right_frame)
        chart_frame.pack(fill=tk.BOTH, expand=True)

        # 總和光譜圖
        self.sum_fig = plt.figure(figsize=(6,3.5), facecolor=BG_COLOR)
        self.sum_ax = self.sum_fig.add_subplot(111)
        self.sum_ax.set_facecolor(BG_COLOR)
        self.sum_canvas = FigureCanvasTkAgg(self.sum_fig, master=chart_frame)
        self.sum_canvas.get_tk_widget().pack(fill=tk.BOTH, pady=5)

        # 正規化光譜圖
        self.norm_fig = plt.figure(figsize=(6,3.5), facecolor=BG_COLOR)
        self.norm_ax = self.norm_fig.add_subplot(111)
        self.norm_ax.set_facecolor(BG_COLOR)
        self.norm_canvas = FigureCanvasTkAgg(self.norm_fig, master=chart_frame)
        self.norm_canvas.get_tk_widget().pack(fill=tk.BOTH, pady=5)

        # PPF計算結果面板
        self.ppf_frame = ttk.LabelFrame(right_frame, text="PPF 計算結果", padding=15)
        self.ppf_frame.pack(fill=tk.BOTH, pady=10)
        
        ppf_labels = [
            ("總PPF:", "0.00", PRIMARY_COLOR),
            ("藍光PPF (400-499nm):", "0.00", "#2980B9"),
            ("綠光PPF (500-599nm):", "0.00", "#27AE60"),
            ("紅光PPF (600-700nm):", "0.00", "#C0392B")
        ]
        
        for i, (label, value, color) in enumerate(ppf_labels):
            row_frame = ttk.Frame(self.ppf_frame)
            row_frame.pack(fill=tk.X, pady=3)
            ttk.Label(row_frame, text=label, width=20, anchor=tk.W, 
                     font=('Microsoft JhengHei', 10, 'bold'), foreground=color).pack(side=tk.LEFT)
            ttk.Label(row_frame, text=value, width=10, anchor=tk.E, 
                     font=('Microsoft JhengHei', 10, 'bold')).pack(side=tk.RIGHT)
            setattr(self, f"ppf_label_{i}", row_frame.winfo_children()[1])

    def generate_plots(self):
        """生成光譜圖表框架"""
        try:
            n = int(self.n_entry.get())
            if not 1 <= n <= 10:
                raise ValueError("數值超出範圍")
        except ValueError:
            messagebox.showerror("輸入錯誤", "請輸入1-10之間的整數")
            return
        except Exception as e:
            messagebox.showerror("系統錯誤", f"發生未預期錯誤: {str(e)}")
            return

        # 清除舊圖表
        for widget in self.left_frame.winfo_children():
            widget.destroy()
        
        self.figures = []
        self.canvases = []
        self.spectra_data = []
        self.scale_entries = []  # 清空倍率輸入框列表
        self.current_n = n

        try:
            for i in range(n):
                frame = ttk.Frame(self.left_frame, padding=10)
                frame.pack(fill=tk.X, pady=5, padx=5)
                frame.config(relief='groove', borderwidth=1)
                
                # 創建Matplotlib圖形
                fig = plt.figure(figsize=(8,2.5), facecolor=BG_COLOR)
                ax = fig.add_subplot(111)
                ax.set_facecolor(BG_COLOR)
                ax.tick_params(colors=TEXT_COLOR)
                for spine in ax.spines.values():
                    spine.set_color(TEXT_COLOR)
                
                # 嵌入Canvas
                canvas = FigureCanvasTkAgg(fig, master=frame)
                canvas.get_tk_widget().pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
                
                # 添加載入按鈕和倍率輸入
                btn_frame = ttk.Frame(frame)
                btn_frame.pack(side=tk.LEFT, padx=10)
                
                ttk.Label(btn_frame, text="倍率:").pack()
                scale_entry = ttk.Entry(btn_frame, width=5)
                scale_entry.insert(0, "1.0")  # 初始倍率為1
                scale_entry.pack()
                self.scale_entries.append(scale_entry)  # 存儲輸入框
                
                ttk.Button(btn_frame, text=f"載入光譜 {i+1}", 
                          command=lambda idx=i: self.load_file(idx)).pack(pady=5)
                
                # 存儲圖形對象
                self.figures.append(fig)
                self.canvases.append(canvas)
                self.spectra_data.append({'data': None, 'scale': 1.0})  # 存儲數據和倍率
                
            self.left_frame.update_idletasks()
            self.left_canvas.configure(scrollregion=self.left_canvas.bbox("all"))
        except Exception as e:
            messagebox.showerror("系統錯誤", f"生成圖表失敗: {str(e)}")

    def update_scales(self):
        """更新所有光譜的倍率"""
        try:
            for i, entry in enumerate(self.scale_entries):
                scale = float(entry.get())
                if scale < 0:
                    raise ValueError("倍率不能為負數")
                self.spectra_data[i]['scale'] = scale
            self.update_sum_plots()
        except ValueError as e:
            messagebox.showerror("輸入錯誤", f"無效的倍率值: {str(e)}")
        except Exception as e:
            messagebox.showerror("系統錯誤", f"更新倍率失敗: {str(e)}")

    def load_file(self, index):
        """載入光譜數據文件"""
        filepath = filedialog.askopenfilename(filetypes=[("文字檔案", "*.txt")])
        if not filepath:
            return
        
        try:
            with open(filepath, 'r') as f:
                # 驗證文件格式
                header = f.readline().strip().split()
                if header != ['nm', 'mw']:
                    raise ValueError("檔案格式不正確")
                    
                # 讀取數據
                data = {'nm': [], 'mw': []}
                for line in f:
                    values = line.strip().split()
                    if len(values) != 2:
                        continue  # 跳過格式錯誤的行
                    data['nm'].append(float(values[0]))
                    data['mw'].append(float(values[1]))
                    
                self.spectra_data[index]['data'] = data
                
                # 更新圖表
                ax = self.figures[index].get_axes()[0]
                ax.clear()
                
                # 繪製光譜圖
                self.draw_spectrum(ax, data['nm'], data['mw'])
                self.canvases[index].draw()
                self.update_sum_plots()
                
        except Exception as e:
            messagebox.showerror("檔案錯誤", f"讀取失敗: {str(e)}")

    def draw_spectrum(self, ax, x, y):
        """繪製帶有漸變填充的光譜圖"""
        # 生成漸變層
        xx = np.linspace(400, 700, 512)
        yy = np.linspace(0, max(y) if max(y) > 0 else 1, 512)
        X, Y = np.meshgrid(xx, yy)
        Z = X  # 顏色由X軸決定

        # 使用自定義光譜顏色映射
        im = ax.imshow(Z, cmap=spectrum_cmap, 
                      extent=[400, 700, 0, max(y) if max(y) > 0 else 1], 
                      aspect='auto', origin='lower', 
                      alpha=0.7, interpolation='spline36')

        # 創建裁剪路徑
        path = Path(np.column_stack([x, y]))
        patch = PathPatch(path, facecolor='none', edgecolor='none')
        ax.add_patch(patch)
        im.set_clip_path(patch)

        # 繪製白色邊框曲線
        ax.plot(x, y, color='white', linewidth=1.5, alpha=0.8)
        
        # 設置坐標軸樣式
        ax.set_title(f"光譜圖", fontname='Microsoft JhengHei', 
                    color=TEXT_COLOR, pad=10)
        ax.set_xlabel("波長 (nm)", fontname='Microsoft JhengHei', color=TEXT_COLOR)
        ax.set_ylabel("強度 (mw)", fontname='Microsoft JhengHei', color=TEXT_COLOR)
        ax.grid(True, alpha=0.3)

    def update_sum_plots(self):
        """更新總和圖表和PPF計算"""
        if not all(data['data'] for data in self.spectra_data):
            return
            
        try:
            # 計算總和光譜（考慮倍率）
            sum_mw = [0] * 301
            for data in self.spectra_data:
                if data['data']:
                    scale = data['scale']
                    for i, val in enumerate(data['data']['mw']):
                        sum_mw[i] += val * scale
                        
            x = list(range(400, 701))
            
            # 更新總和光譜圖
            self.sum_ax.clear()
            self.draw_spectrum(self.sum_ax, x, sum_mw)
            self.sum_ax.set_title("總和光譜圖", fontname='Microsoft JhengHei')
            self.sum_canvas.draw()

            # 更新正規化光譜圖
            max_val = max(sum_mw) if sum_mw else 1
            norm_mw = [val/max_val for val in sum_mw] if max_val != 0 else [0]*301
            self.norm_ax.clear()
            self.norm_ax.plot(x, norm_mw, color=SECONDARY_COLOR)
            self.norm_ax.fill_between(x, 0, norm_mw, color=SECONDARY_COLOR, alpha=0.3)
            self.norm_ax.set_title("正規化光譜圖", fontname='Microsoft JhengHei')
            self.norm_ax.grid(True, alpha=0.3)
            self.norm_canvas.draw()

            # 計算PPF值
            total_ppf = ppf_blue = ppf_green = ppf_red = 0.0
            for i, mw in enumerate(sum_mw):
                wavelength = 400 + i
                ppf_value = wavelength * mw * 0.008359 / 1000.0
                total_ppf += ppf_value

                if 400 <= wavelength <= 499:
                    ppf_blue += ppf_value
                elif 500 <= wavelength <= 599:
                    ppf_green += ppf_value
                elif 600 <= wavelength <= 700:
                    ppf_red += ppf_value

            self.ppf_label_0.config(text=f"{total_ppf:.2f} μmol/s")
            self.ppf_label_1.config(text=f"{ppf_blue:.2f} μmol/s")
            self.ppf_label_2.config(text=f"{ppf_green:.2f} μmol/s")
            self.ppf_label_3.config(text=f"{ppf_red:.2f} μmol/s")
        except Exception as e:
            messagebox.showerror("計算錯誤", f"更新圖表失敗: {str(e)}")
    
    def exit_program(self):
        """安全退出程序"""
        try:
            plt.close('all')
            self.root.quit()
            self.root.destroy()
        except Exception as e:
            import os
            os._exit(0)

    def run(self):
        """運行主程序"""
        self.root.mainloop()

if __name__ == "__main__":
    if check_expiration():
        login = LoginWindow()
        try:
            login.root.mainloop()
        except KeyboardInterrupt:
            pass