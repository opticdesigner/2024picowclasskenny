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
        self.master.title("光谱分析工具")
        
        # 窗口设置
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
        self.create_precise_colormap()
        self.create_widgets()
    
    def create_precise_colormap(self):
        color_bands = [
            (400, (0.5, 0, 0.5)),    # 紫色
            (440, (0, 0, 1)),        # 蓝色
            (490, (0, 1, 1)),        # 青色
            (510, (0, 1, 0)),        # 绿色
            (580, (1, 1, 0)),        # 黄色
            (645, (1, 0.5, 0)),      # 橙色
            (700, (1, 0, 0))         # 红色
        ]
        
        cdict = {'red': [], 'green': [], 'blue': []}
        for nm, (r, g, b) in color_bands:
            pos = (nm - 400) / 300
            cdict['red'].append((pos, r, r))
            cdict['green'].append((pos, g, g))
            cdict['blue'].append((pos, b, b))
        
        self.wavelength_cmap = LinearSegmentedColormap('spectrum', cdict)

    def create_widgets(self):
        main_frame = ttk.Frame(self.master, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        title_label = ttk.Label(main_frame, text="高精度光谱分析系统", 
                              font=('Microsoft JhengHei', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(control_frame, text="光谱数量 (1-10):", 
                font=('Microsoft JhengHei', 10)).pack(side=tk.LEFT)
        self.num_var = tk.StringVar()
        ttk.Entry(control_frame, textvariable=self.num_var, width=10).pack(side=tk.LEFT, padx=10)
        
        ttk.Button(control_frame, text="确认", command=self.validate_and_create_plots).pack(side=tk.LEFT)
        ttk.Button(control_frame, text="退出", command=self.master.quit).pack(side=tk.RIGHT)
        
        # PPF显示区域
        ppf_frame = ttk.LabelFrame(main_frame, text="光量子通量分析", padding=10)
        ppf_frame.pack(fill=tk.X, pady=10)
        
        ppf_labels = [
            ('总 PPF (400-700nm):', 'total_ppf'),
            ('蓝光 PPF (400-499nm):', 'blue_ppf'),
            ('绿光 PPF (500-599nm):', 'green_ppf'),
            ('红光 PPF (600-700nm):', 'red_ppf')
        ]
        for text, attr in ppf_labels:
            frame = ttk.Frame(ppf_frame)
            frame.pack(fill=tk.X, pady=2)
            ttk.Label(frame, text=text, width=25).pack(side=tk.LEFT)
            label = ttk.Label(frame, text='0.0000', font=('Microsoft JhengHei', 10, 'bold'))
            label.pack(side=tk.LEFT)
            setattr(self, f'{attr}_label', label)
        
        content_pane = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        content_pane.pack(fill=tk.BOTH, expand=True)
        
        # 左侧光谱区
        left_frame = ttk.Frame(content_pane)
        self.spectrum_canvas = tk.Canvas(left_frame)
        scrollbar = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=self.spectrum_canvas.yview)
        self.spectrum_frame = ttk.Frame(self.spectrum_canvas)
        self.spectrum_canvas.create_window((0,0), window=self.spectrum_frame, anchor="nw")
        self.spectrum_canvas.configure(yscrollcommand=scrollbar.set)
        self.spectrum_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        content_pane.add(left_frame)
        
        # 右侧光谱区
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
            
            self.spectrum_data = [None]*n
            self.spectrum_plots.clear()
            self.spectrum_scales.clear()
            for widget in self.spectrum_frame.winfo_children():
                widget.destroy()
            
            for i in range(n):
                frame = ttk.Frame(self.spectrum_frame)
                frame.pack(fill=tk.X, pady=5)
                
                control_panel = ttk.Frame(frame)
                control_panel.pack(fill=tk.X)
                ttk.Label(control_panel, text=f"光谱 {i+1}", 
                         font=('Microsoft JhengHei', 10, 'bold')).pack(side=tk.LEFT)
                
                scale_var = tk.DoubleVar(value=1.0)
                self.spectrum_scales.append(scale_var)
                ttk.Entry(control_panel, textvariable=scale_var, width=6).pack(side=tk.RIGHT)
                ttk.Label(control_panel, text="倍率:").pack(side=tk.RIGHT)
                scale_var.trace_add('write', lambda *_, idx=i: self.update_total_spectrum())
                
                ttk.Button(control_panel, text="加载文件", 
                         command=lambda idx=i: self.load_spectrum(idx)).pack(side=tk.RIGHT, padx=5)
                
                fig = Figure(figsize=(6,2), dpi=100)
                ax = fig.add_subplot(111)
                canvas = FigureCanvasTkAgg(fig, frame)
                canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
                self.spectrum_plots.append((fig, ax, canvas))
        
        except ValueError:
            messagebox.showerror("输入错误", "请输入1到10之间的整数")

    def load_spectrum(self, index):
        filename = filedialog.askopenfilename(filetypes=[("文本文件", "*.csv")])
        if filename:
            try:
                df = pd.read_csv(filename, names=['nm', 'mw'], skiprows=1)
                self.spectrum_data[index] = df
                fig, ax, canvas = self.spectrum_plots[index]
                ax.clear()
                ax.plot(df['nm'], df['mw'], color='#2c3e50')
                ax.set_title(f"光谱 {index+1}")
                ax.set_xlabel("波长 (nm)")
                ax.set_ylabel("强度 (mW)")
                canvas.draw()
                self.update_total_spectrum()
            except Exception as e:
                messagebox.showerror("文件错误", f"文件读取失败: {str(e)}")

    def update_total_spectrum(self):
        self.sum_ax.clear()
        self.norm_ax.clear()
        
        valid_data = []
        for i, df in enumerate(self.spectrum_data):
            if df is not None:
                try:
                    scale = float(self.spectrum_scales[i].get())
                except:
                    scale = 1.0
                valid_data.append(df.copy().assign(mw=df['mw']*scale))
        
        if valid_data:
            sum_df = pd.concat(valid_data).groupby('nm', as_index=False).sum()
            sum_df = sum_df.sort_values('nm')
            x = sum_df['nm'].values
            y = sum_df['mw'].values
            
            if len(x) > 1:
                verts = []
                colors = []
                for i in range(len(x)-1):
                    mid_nm = (x[i] + x[i+1]) / 2
                    color = self.wavelength_cmap((mid_nm - 400) / 300)
                    verts.append([(x[i], 0), (x[i], y[i]), (x[i+1], y[i+1]), (x[i+1], 0)])
                    colors.append(color)
                
                poly = PolyCollection(
                    verts,
                    facecolors=colors,
                    edgecolors='none',
                    alpha=0.8
                )
                self.sum_ax.add_collection(poly)
                self.sum_ax.set_xlim(380, 720)
                self.sum_ax.set_ylim(0, y.max()*1.1)
                self.sum_ax.set_title("光谱强度分布（精确填色）", pad=20)
                self.sum_ax.set_xlabel("波长 (nm)", labelpad=10)
                self.sum_ax.set_ylabel("强度 (mW)", labelpad=10)
            
            norm_y = y / y.max()
            self.norm_ax.plot(x, norm_y, color='#34495e', linewidth=1.5)
            self.norm_ax.fill_between(x, norm_y, color='#bdc3c7', alpha=0.3)
            self.norm_ax.set_title("标准化光谱对比", pad=15)
            self.norm_ax.set_xlabel("波长 (nm)", labelpad=10)
            self.norm_ax.set_ylabel("相对强度", labelpad=10)
            
            self.calculate_ppf_values(x, y)
            
            self.sum_canvas.draw()
            self.norm_canvas.draw()

    def calculate_ppf_values(self, wavelengths, intensities):
        ppf = wavelengths * intensities * 0.008359 / 1000
        
        # 定义PPF计算区间
        blue_mask = (wavelengths >= 400) & (wavelengths <= 499)
        green_mask = (wavelengths >= 500) & (wavelengths <= 599)
        red_mask = (wavelengths >= 600) & (wavelengths <= 700)
        
        total_ppf = ppf.sum()
        blue_ppf = ppf[blue_mask].sum()
        green_ppf = ppf[green_mask].sum()
        red_ppf = ppf[red_mask].sum()
        
        self.total_ppf_label.config(text=f"{total_ppf:.4f}")
        self.blue_ppf_label.config(text=f"{blue_ppf:.4f}")
        self.green_ppf_label.config(text=f"{green_ppf:.4f}")
        self.red_ppf_label.config(text=f"{red_ppf:.4f}")

class LoginWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("系统登录")
        self.root.geometry("320x240")
        
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(expand=True, fill=tk.BOTH)
        
        ttk.Label(main_frame, text="光谱分析系统", 
                 font=('Microsoft JhengHei', 14, 'bold')).pack(pady=10)
        
        ttk.Label(main_frame, text="用户名:").pack()
        self.username = ttk.Entry(main_frame)
        self.username.pack()
        
        ttk.Label(main_frame, text="密码:").pack(pady=(10,0))
        self.password = ttk.Entry(main_frame, show="•")
        self.password.pack()
        
        ttk.Button(main_frame, text="登录", 
                  command=self.check_login).pack(pady=15)
        
        self.root.mainloop()
    
    def check_login(self):
        if datetime.now() > datetime(2025, 3, 29):
            messagebox.showerror("授权过期", "系统已过期，请联系技术支持")
            return
        
        if self.username.get() == "WSL" and self.password.get() == "50968758":
            self.root.destroy()
            root = tk.Tk()
            StyledApp(root)
            root.mainloop()
        else:
            messagebox.showerror("登录失败", "用户名或密码错误")

if __name__ == "__main__":
    LoginWindow()