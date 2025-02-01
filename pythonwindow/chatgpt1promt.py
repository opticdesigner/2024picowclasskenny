#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import datetime
import os

import numpy as np
import pandas as pd

import matplotlib
matplotlib.use('TkAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt

# =======================
# 全局配置
# =======================
APP_WIDTH = 1400
APP_HEIGHT = 900
FONT_NAME = "Microsoft JhengHei"
BG_COLOR = "#2E2E2E"
FG_COLOR = "#FFFFFF"
ACCENT_COLOR = "#4CAF50"

# 预设账号
PRESET_USER = "WSL"
PRESET_PASS = "50968758"
# 有效期至
EXPIRE_DATE = datetime.datetime(2025, 3, 29)

# =======================
# 数据层：单个光谱数据
# =======================
class SpectrumData:
    def __init__(self, filepath):
        self.filepath = filepath
        self.filename = os.path.basename(filepath)
        self.multiplier = 1.0
        self.df = None
        self.load_data()
    
    def load_data(self):
        try:
            # 假设 CSV 文件有两列：wavelength, intensity
            self.df = pd.read_csv(self.filepath)
            # 检查必要列
            if not {'wavelength', 'intensity'}.issubset(self.df.columns):
                raise ValueError("CSV 文件格式错误，必须包含 'wavelength' 和 'intensity' 列")
            # 转换数据类型，确保数值型
            self.df['wavelength'] = pd.to_numeric(self.df['wavelength'], errors='coerce')
            self.df['intensity'] = pd.to_numeric(self.df['intensity'], errors='coerce')
            self.df.dropna(inplace=True)
            # 排序（按波长升序）
            self.df.sort_values('wavelength', inplace=True)
        except Exception as e:
            raise Exception(f"加载文件 {self.filename} 失败：{str(e)}")
    
    def get_scaled_intensity(self):
        """返回倍率调整后的光谱数据"""
        return self.df['intensity'] * self.multiplier

# =======================
# 登录界面
# =======================
class LoginWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("光谱分析系统 - 登录")
        self.configure(bg=BG_COLOR)
        self.geometry("400x250")
        self.resizable(False, False)
        # 居中显示
        self.center_window(400, 250)
        self.create_widgets()
    
    def center_window(self, width, height):
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = int((screen_width - width) / 2)
        y = int((screen_height - height) / 2)
        self.geometry(f"{width}x{height}+{x}+{y}")
    
    def create_widgets(self):
        # 检查是否已过期
        now = datetime.datetime.now()
        if now > EXPIRE_DATE:
            label = tk.Label(self, text="软件已过期，请联系技术支持：support@example.com", 
                             font=(FONT_NAME, 12), bg=BG_COLOR, fg="red")
            label.pack(expand=True)
            return

        # 用户名标签与输入
        lbl_user = tk.Label(self, text="用户名：", font=(FONT_NAME, 12), bg=BG_COLOR, fg=FG_COLOR)
        lbl_user.pack(pady=(30, 5))
        self.entry_user = tk.Entry(self, font=(FONT_NAME, 12))
        self.entry_user.pack(pady=5)
        # 密码标签与输入
        lbl_pass = tk.Label(self, text="密码：", font=(FONT_NAME, 12), bg=BG_COLOR, fg=FG_COLOR)
        lbl_pass.pack(pady=5)
        self.entry_pass = tk.Entry(self, font=(FONT_NAME, 12), show="*")
        self.entry_pass.pack(pady=5)
        # 登录按钮
        btn_login = tk.Button(self, text="登录", font=(FONT_NAME, 12), bg=ACCENT_COLOR, fg=FG_COLOR,
                              command=self.check_login)
        btn_login.pack(pady=(20,10))
    
    def check_login(self):
        username = self.entry_user.get().strip()
        password = self.entry_pass.get().strip()
        if username == PRESET_USER and password == PRESET_PASS:
            self.destroy()
            app = MainApp()
            app.mainloop()
        else:
            messagebox.showerror("错误", "用户名或密码错误！")

# =======================
# 主程序界面
# =======================
class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("高精度光谱分析工具")
        self.configure(bg=BG_COLOR)
        self.geometry(f"{APP_WIDTH}x{APP_HEIGHT}")
        self.center_window(APP_WIDTH, APP_HEIGHT)
        self.spectra = []  # 存储 SpectrumData 对象
        self.create_menu()
        self.create_widgets()
    
    def center_window(self, width, height):
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = int((screen_width - width) / 2)
        y = int((screen_height - height) / 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def create_menu(self):
        menubar = tk.Menu(self, bg=BG_COLOR, fg=FG_COLOR, font=(FONT_NAME, 10))
        file_menu = tk.Menu(menubar, tearoff=0, bg=BG_COLOR, fg=FG_COLOR, font=(FONT_NAME, 10))
        file_menu.add_command(label="加载光谱数据", command=self.load_spectra)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.quit)
        menubar.add_cascade(label="文件", menu=file_menu)
        self.config(menu=menubar)

    def create_widgets(self):
        # 主区域分为左右两个面板
        self.left_frame = tk.Frame(self, bg=BG_COLOR)
        self.right_frame = tk.Frame(self, bg=BG_COLOR)
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        self.right_frame.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH, padx=5, pady=5)

        # 左侧：滚动区域（每个光谱一行）
        self.create_left_panel()

        # 右侧：两个 Matplotlib 图形区域（上：填色图；下：标准化光谱对比图）
        self.create_right_panel()

        # 底部：显示积分计算结果
        self.status_frame = tk.Frame(self, bg=BG_COLOR)
        self.status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        self.ppf_var = tk.StringVar()
        lbl_ppf = tk.Label(self.status_frame, textvariable=self.ppf_var, font=(FONT_NAME, 12), bg=BG_COLOR, fg=FG_COLOR)
        lbl_ppf.pack(padx=10, pady=5)
        self.update_ppf_info()

    def create_left_panel(self):
        # 使用 Canvas + Scrollbar 实现滚动区域
        self.canvas = tk.Canvas(self.left_frame, bg=BG_COLOR, width=400, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.left_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg=BG_COLOR)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def create_right_panel(self):
        # 设置 Matplotlib 的深色主题
        plt.style.use('dark_background')

        self.fig = Figure(figsize=(8, 8), dpi=100)
        # 上子图：精确光谱填色图
        self.ax_fill = self.fig.add_subplot(211)
        self.ax_fill.set_title("光谱填色图", fontname=FONT_NAME)
        self.ax_fill.set_xlabel("波长 (nm)", fontname=FONT_NAME)
        self.ax_fill.set_ylabel("强度", fontname=FONT_NAME)
        # 下子图：标准化光谱对比折线图
        self.ax_compare = self.fig.add_subplot(212)
        self.ax_compare.set_title("标准化光谱对比图", fontname=FONT_NAME)
        self.ax_compare.set_xlabel("波长 (nm)", fontname=FONT_NAME)
        self.ax_compare.set_ylabel("归一化强度", fontname=FONT_NAME)

        self.fig.tight_layout(pad=3.0)
        self.canvas_fig = FigureCanvasTkAgg(self.fig, master=self.right_frame)
        self.canvas_fig.draw()
        self.canvas_fig.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def load_spectra(self):
        filepaths = filedialog.askopenfilenames(title="选择光谱数据文件（CSV格式）", filetypes=[("CSV Files", "*.csv")])
        if not filepaths:
            return
        
        if len(filepaths) + len(self.spectra) > 10:
            messagebox.showerror("错误", "最多同时加载10组光谱数据！")
            return
        
        for fp in filepaths:
            try:
                spectrum = SpectrumData(fp)
                self.spectra.append(spectrum)
                self.add_spectrum_widget(spectrum)
            except Exception as e:
                messagebox.showerror("文件加载错误", str(e))
        
        self.update_all_plots()
    
    def add_spectrum_widget(self, spectrum):
        # 每个光谱在左侧显示一个子框架，包含文件名、倍率调节控件及小型图
        frame = tk.Frame(self.scrollable_frame, bg=BG_COLOR, bd=1, relief=tk.RIDGE)
        frame.pack(fill=tk.X, padx=5, pady=5)

        lbl_name = tk.Label(frame, text=spectrum.filename, font=(FONT_NAME, 10), bg=BG_COLOR, fg=FG_COLOR)
        lbl_name.pack(side=tk.TOP, anchor="w", padx=5, pady=2)

        # 倍率调节控件
        scale_var = tk.DoubleVar(value=1.0)
        scale = tk.Scale(frame, variable=scale_var, from_=0.1, to=10.0, resolution=0.1, orient=tk.HORIZONTAL,
                         label="倍率", font=(FONT_NAME, 9), bg=BG_COLOR, fg=FG_COLOR, highlightbackground=BG_COLOR,
                         command=lambda val, sp=spectrum, var=scale_var: self.on_multiplier_change(sp, var))
        scale.pack(side=tk.TOP, fill=tk.X, padx=5, pady=2)

        # 小型 Matplotlib 图形显示该光谱
        fig_small = Figure(figsize=(3, 1.5), dpi=80)
        ax_small = fig_small.add_subplot(111)
        ax_small.plot(spectrum.df['wavelength'], spectrum.get_scaled_intensity(), color=ACCENT_COLOR)
        ax_small.set_title("预览", fontname=FONT_NAME, fontsize=8)
        ax_small.tick_params(labelsize=6)
        fig_small.tight_layout(pad=1.0)

        canvas_small = FigureCanvasTkAgg(fig_small, master=frame)
        canvas_small.draw()
        canvas_small.get_tk_widget().pack(side=tk.TOP, fill=tk.X, padx=5, pady=2)

        # 将小图控件保存到 spectrum 对象中，方便后续更新
        spectrum.fig_small = fig_small
        spectrum.ax_small = ax_small
        spectrum.canvas_small = canvas_small

    def on_multiplier_change(self, spectrum, var):
        try:
            spectrum.multiplier = float(var.get())
            # 更新该光谱的小图
            spectrum.ax_small.cla()
            spectrum.ax_small.plot(spectrum.df['wavelength'], spectrum.get_scaled_intensity(), color=ACCENT_COLOR)
            spectrum.ax_small.set_title("预览", fontname=FONT_NAME, fontsize=8)
            spectrum.ax_small.tick_params(labelsize=6)
            spectrum.canvas_small.draw()
            # 更新整体图形和积分信息
            self.update_all_plots()
        except Exception as e:
            messagebox.showerror("倍率更新错误", str(e))
    
    def update_all_plots(self):
        # 计算总光谱：各光谱数据叠加（倍率调整后）
        if not self.spectra:
            return
        try:
            # 假设所有光谱覆盖的波长范围一致，以第一个为准
            wavelengths = self.spectra[0].df['wavelength'].values
            total_intensity = np.zeros_like(wavelengths, dtype=float)
            for sp in self.spectra:
                # 使用插值或直接按 index 相加，假设波长一致
                total_intensity += sp.get_scaled_intensity().values
            # 更新右侧上方填色图：利用线性分段色阶映射（从400nm紫色渐变到700nm红色）
            self.ax_fill.cla()
            self.ax_fill.set_title("光谱填色图", fontname=FONT_NAME)
            self.ax_fill.set_xlabel("波长 (nm)", fontname=FONT_NAME)
            self.ax_fill.set_ylabel("强度", fontname=FONT_NAME)
            # 构造色阶映射
            norm = mcolors.Normalize(vmin=400, vmax=700)
            cmap = matplotlib.cm.get_cmap("jet")  # 或自定义 colormap
            colors = [cmap(norm(w)) for w in wavelengths]
            # 用 fill_between 绘制带颜色渐变的图形（模拟填色效果）
            self.ax_fill.plot(wavelengths, total_intensity, color=ACCENT_COLOR)
            for i in range(len(wavelengths)-1):
                self.ax_fill.fill_between(wavelengths[i:i+2], total_intensity[i:i+2],
                                          color=colors[i])
            # 更新右侧下方：标准化各光谱对比折线图
            self.ax_compare.cla()
            self.ax_compare.set_title("标准化光谱对比图", fontname=FONT_NAME)
            self.ax_compare.set_xlabel("波长 (nm)", fontname=FONT_NAME)
            self.ax_compare.set_ylabel("归一化强度", fontname=FONT_NAME)
            for sp in self.spectra:
                intensity = sp.get_scaled_intensity().values
                # 归一化处理：除以最大值
                if np.max(intensity) != 0:
                    intensity_norm = intensity / np.max(intensity)
                else:
                    intensity_norm = intensity
                self.ax_compare.plot(wavelengths, intensity_norm, label=sp.filename)
            self.ax_compare.legend(fontsize=8)
            self.canvas_fig.draw()
            # 更新积分信息
            self.update_ppf_info(total_intensity=total_intensity, wavelengths=wavelengths)
        except Exception as e:
            messagebox.showerror("绘图更新错误", str(e))
    
    def update_ppf_info(self, total_intensity=None, wavelengths=None):
        # 自动计算并显示：
        # 总 PPF（400-700nm），蓝光 PPF（400-499nm），绿光 PPF（500-599nm），红光 PPF（600-700nm）
        try:
            if total_intensity is None or wavelengths is None:
                # 如果没有总数据，则显示0
                total_ppf = blue_ppf = green_ppf = red_ppf = 0
            else:
                # 使用数值积分（例如 trapz），要求波长已按升序排列
                mask_total = (wavelengths >= 400) & (wavelengths <= 700)
                mask_blue  = (wavelengths >= 400) & (wavelengths < 500)
                mask_green = (wavelengths >= 500) & (wavelengths < 600)
                mask_red   = (wavelengths >= 600) & (wavelengths <= 700)
                total_ppf = np.trapz(total_intensity[mask_total], wavelengths[mask_total])
                blue_ppf  = np.trapz(total_intensity[mask_blue], wavelengths[mask_blue])
                green_ppf = np.trapz(total_intensity[mask_green], wavelengths[mask_green])
                red_ppf   = np.trapz(total_intensity[mask_red], wavelengths[mask_red])
            info = f"总 PPF (400-700nm): {total_ppf:.2f}    蓝光 PPF (400-499nm): {blue_ppf:.2f}    " \
                   f"绿光 PPF (500-599nm): {green_ppf:.2f}    红光 PPF (600-700nm): {red_ppf:.2f}"
            self.ppf_var.set(info)
        except Exception as e:
            messagebox.showerror("积分计算错误", str(e))

# =======================
# 主入口
# =======================
if __name__ == "__main__":
    # 先启动登录窗口
    login = LoginWindow()
    login.mainloop()
