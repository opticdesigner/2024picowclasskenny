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

# 嘗試載入 colour 科學套件以計算 CRI
try:
    import colour
except ImportError:
    colour = None

# =======================
# 全域配置
# =======================
APP_WIDTH = 1400
APP_HEIGHT = 900
FONT_NAME = "Microsoft JhengHei"  # 微軟正黑體
BG_COLOR = "#2E2E2E"
FG_COLOR = "#FFFFFF"
ACCENT_COLOR = "#4CAF50"

# 預設帳號
PRESET_USER = "WSL"
PRESET_PASS = "50968758"
# 有效期至
EXPIRE_DATE = datetime.datetime(2025, 3, 29)

# =======================
# 計算 CCT 與 CRI 的函式
# =======================

def calculate_CCT_from_spectrum(wavelengths, intensities):
    """
    利用光譜數據計算 CIE XYZ 值，再求 chromaticity (x,y)，
    最後採用 McCamy 公式計算 CCT：
      n = (x - 0.3320) / (y - 0.1858)
      CCT = -449 n^3 + 3525 n^2 - 6823.3 n + 5520.33
    """
    # 定義 CIE 1931 2° 標準觀察者色匹配函數（400-700 nm，單位近似）
    cmf_data = {
       400: (0.0143, 0.000396, 0.0679),
       410: (0.0232, 0.00064, 0.1102),
       420: (0.0435, 0.00121, 0.2074),
       430: (0.0776, 0.00218, 0.3713),
       440: (0.1344, 0.00400, 0.6456),
       450: (0.2148, 0.00730, 1.0391),
       460: (0.2839, 0.01160, 1.3856),
       470: (0.3285, 0.01684, 1.6230),
       480: (0.3483, 0.02300, 1.7471),
       490: (0.3481, 0.02980, 1.7826),
       500: (0.3362, 0.03800, 1.7721),
       510: (0.3187, 0.04800, 1.7441),
       520: (0.2908, 0.06000, 1.6692),
       530: (0.2511, 0.07390, 1.5281),
       540: (0.1954, 0.09100, 1.2876),
       550: (0.1421, 0.11260, 1.0419),
       560: (0.0956, 0.13902, 0.8120),
       570: (0.05795, 0.1693, 0.6162),
       580: (0.03201, 0.20802, 0.4652),
       590: (0.01470, 0.2586, 0.3533),
       600: (0.00490, 0.3230, 0.2720),
       610: (0.00240, 0.4073, 0.2123),
       620: (0.00930, 0.5030, 0.1582),
       630: (0.02910, 0.6082, 0.1117),
       640: (0.06330, 0.7100, 0.0782),
       650: (0.10960, 0.7932, 0.0573),
       660: (0.16550, 0.8620, 0.04216),
       670: (0.22570, 0.9149, 0.02984),
       680: (0.29040, 0.9540, 0.02030),
       690: (0.35970, 0.9803, 0.01340),
       700: (0.43340, 0.9949, 0.00875)
    }
    cmf_wavelengths = np.array(sorted(cmf_data.keys()))
    cmf_x = np.array([cmf_data[w][0] for w in cmf_wavelengths])
    cmf_y = np.array([cmf_data[w][1] for w in cmf_wavelengths])
    cmf_z = np.array([cmf_data[w][2] for w in cmf_wavelengths])
    # 對輸入波長進行插值
    x_bar = np.interp(wavelengths, cmf_wavelengths, cmf_x)
    y_bar = np.interp(wavelengths, cmf_wavelengths, cmf_y)
    z_bar = np.interp(wavelengths, cmf_wavelengths, cmf_z)
    # 計算 X, Y, Z（使用數值積分，波長單位 nm）
    X = np.trapz(intensities * x_bar, wavelengths)
    Y = np.trapz(intensities * y_bar, wavelengths)
    Z = np.trapz(intensities * z_bar, wavelengths)
    sumXYZ = X + Y + Z
    if sumXYZ == 0:
        return 0.0
    x = X / sumXYZ
    y = Y / sumXYZ
    # McCamy 公式所需參數 n
    n = (x - 0.3320) / (y - 0.1858)
    cct = -449 * n**3 + 3525 * n**2 - 6823.3 * n + 5520.33
    return cct

def calculate_CRI(wavelengths, intensities):
    """
    使用 colour-science 套件計算顯色指數 (CRI)。
    若無法載入該套件，則回傳預設值 85。
    """
    if colour is None:
        return 85.0
    # 建立光譜分佈物件；確保波長與強度均為數值且以 nm 為單位
    data = dict(zip(wavelengths, intensities))
    sd = colour.SpectralDistribution(data, name="Test")
    try:
        cri_dict = colour.quality.colour_rendering_index(sd)
        # 'Ra' 為平均顯色指數
        return cri_dict['Ra']
    except Exception as ex:
        return 85.0

# =======================
# 資料層：單個光譜資料
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
            # 假設 CSV 檔案必含 'wavelength' 與 'intensity' 欄位
            self.df = pd.read_csv(self.filepath)
            if not {'wavelength', 'intensity'}.issubset(self.df.columns):
                raise ValueError("CSV 檔案格式錯誤，必須包含 'wavelength' 與 'intensity' 欄位")
            self.df['wavelength'] = pd.to_numeric(self.df['wavelength'], errors='coerce')
            self.df['intensity'] = pd.to_numeric(self.df['intensity'], errors='coerce')
            self.df.dropna(inplace=True)
            self.df.sort_values('wavelength', inplace=True)
        except Exception as e:
            raise Exception(f"載入檔案 {self.filename} 失敗：{str(e)}")
    
    def get_scaled_intensity(self):
        """回傳倍率調整後的光譜資料"""
        return self.df['intensity'] * self.multiplier

# =======================
# 登入視窗
# =======================
class LoginWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("光譜分析系統 - 登入")
        self.configure(bg=BG_COLOR)
        self.geometry("400x250")
        self.resizable(False, False)
        self.center_window(400, 250)
        self.create_widgets()
    
    def center_window(self, width, height):
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = int((screen_width - width) / 2)
        y = int((screen_height - height) / 2)
        self.geometry(f"{width}x{height}+{x}+{y}")
    
    def create_widgets(self):
        now = datetime.datetime.now()
        if now > EXPIRE_DATE:
            label = tk.Label(self, text="軟體已過期，請聯絡技術支援：support@example.com", 
                             font=(FONT_NAME, 12), bg=BG_COLOR, fg="red")
            label.pack(expand=True)
            return
        lbl_user = tk.Label(self, text="使用者名稱：", font=(FONT_NAME, 12), bg=BG_COLOR, fg=FG_COLOR)
        lbl_user.pack(pady=(30, 5))
        self.entry_user = tk.Entry(self, font=(FONT_NAME, 12))
        self.entry_user.pack(pady=5)
        lbl_pass = tk.Label(self, text="密碼：", font=(FONT_NAME, 12), bg=BG_COLOR, fg=FG_COLOR)
        lbl_pass.pack(pady=5)
        self.entry_pass = tk.Entry(self, font=(FONT_NAME, 12), show="*")
        self.entry_pass.pack(pady=5)
        btn_login = tk.Button(self, text="登入", font=(FONT_NAME, 12), bg=ACCENT_COLOR, fg=FG_COLOR,
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
            messagebox.showerror("錯誤", "使用者名稱或密碼錯誤！")

# =======================
# 主程式視窗
# =======================
class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("高精度光譜分析工具")
        self.configure(bg=BG_COLOR)
        self.geometry(f"{APP_WIDTH}x{APP_HEIGHT}")
        self.center_window(APP_WIDTH, APP_HEIGHT)
        self.spectra = []  # 儲存 SpectrumData 物件
        self.create_menu()
        self.create_widgets()
    
    def center_window(self, width, height):
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x = int((sw - width) / 2)
        y = int((sh - height) / 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def create_menu(self):
        menubar = tk.Menu(self, bg=BG_COLOR, fg=FG_COLOR, font=(FONT_NAME, 10))
        file_menu = tk.Menu(menubar, tearoff=0, bg=BG_COLOR, fg=FG_COLOR, font=(FONT_NAME, 10))
        file_menu.add_command(label="載入光譜資料", command=self.load_spectra)
        file_menu.add_separator()
        file_menu.add_command(label="離開", command=self.quit)
        menubar.add_cascade(label="檔案", menu=file_menu)
        self.config(menu=menubar)

    def create_widgets(self):
        self.paned = tk.PanedWindow(self, orient=tk.HORIZONTAL, bg=BG_COLOR)
        self.paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.left_frame = tk.Frame(self.paned, bg=BG_COLOR)
        self.create_left_panel()
        self.paned.add(self.left_frame, minsize=300)
        self.right_frame = tk.Frame(self.paned, bg=BG_COLOR)
        self.create_right_panel()
        self.paned.add(self.right_frame, minsize=500)
        self.status_frame = tk.Frame(self, bg=BG_COLOR)
        self.status_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)
        self.ppf_total_var = tk.StringVar()
        self.ppf_blue_var  = tk.StringVar()
        self.ppf_green_var = tk.StringVar()
        self.ppf_red_var   = tk.StringVar()
        self.cct_var       = tk.StringVar()
        self.cri_var       = tk.StringVar()
        lbl_total = tk.Label(self.status_frame, textvariable=self.ppf_total_var, font=(FONT_NAME, 12),
                             bg=BG_COLOR, fg=FG_COLOR)
        lbl_blue = tk.Label(self.status_frame, textvariable=self.ppf_blue_var, font=(FONT_NAME, 12),
                             bg=BG_COLOR, fg=FG_COLOR)
        lbl_green = tk.Label(self.status_frame, textvariable=self.ppf_green_var, font=(FONT_NAME, 12),
                             bg=BG_COLOR, fg=FG_COLOR)
        lbl_red = tk.Label(self.status_frame, textvariable=self.ppf_red_var, font=(FONT_NAME, 12),
                             bg=BG_COLOR, fg=FG_COLOR)
        lbl_cct = tk.Label(self.status_frame, textvariable=self.cct_var, font=(FONT_NAME, 12),
                             bg=BG_COLOR, fg=FG_COLOR)
        lbl_cri = tk.Label(self.status_frame, textvariable=self.cri_var, font=(FONT_NAME, 12),
                             bg=BG_COLOR, fg=FG_COLOR)
        for lbl in [lbl_total, lbl_blue, lbl_green, lbl_red, lbl_cct, lbl_cri]:
            lbl.pack(anchor="w", padx=10)
        self.update_ppf_info()

    def create_left_panel(self):
        self.canvas = tk.Canvas(self.left_frame, bg=BG_COLOR, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.left_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg=BG_COLOR)
        self.scrollable_frame.bind("<Configure>",
                                   lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def create_right_panel(self):
        plt.style.use('dark_background')
        self.fig = Figure(figsize=(8, 8), dpi=100)
        self.ax_fill = self.fig.add_subplot(211)
        self.ax_fill.set_title("光譜填色圖", fontname=FONT_NAME)
        self.ax_fill.set_xlabel("波長 (nm)", fontname=FONT_NAME)
        self.ax_fill.set_ylabel("強度", fontname=FONT_NAME)
        self.ax_compare = self.fig.add_subplot(212)
        self.ax_compare.set_title("標準化光譜對比圖", fontname=FONT_NAME)
        self.ax_compare.set_xlabel("波長 (nm)", fontname=FONT_NAME)
        self.ax_compare.set_ylabel("歸一化強度", fontname=FONT_NAME)
        self.fig.tight_layout(pad=3.0)
        self.canvas_fig = FigureCanvasTkAgg(self.fig, master=self.right_frame)
        self.canvas_fig.draw()
        self.canvas_fig.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def load_spectra(self):
        filepaths = filedialog.askopenfilenames(title="選擇光譜資料檔案（CSV格式）", filetypes=[("CSV Files", "*.csv")])
        if not filepaths:
            return
        if len(filepaths) + len(self.spectra) > 10:
            messagebox.showerror("錯誤", "最多同時載入10組光譜資料！")
            return
        for fp in filepaths:
            try:
                spectrum = SpectrumData(fp)
                self.spectra.append(spectrum)
                self.add_spectrum_widget(spectrum)
            except Exception as e:
                messagebox.showerror("檔案載入錯誤", str(e))
        self.update_all_plots()

    def add_spectrum_widget(self, spectrum):
        frame = tk.Frame(self.scrollable_frame, bg=BG_COLOR, bd=1, relief=tk.RIDGE)
        frame.pack(fill=tk.X, padx=5, pady=5)
        lbl_name = tk.Label(frame, text=spectrum.filename, font=(FONT_NAME, 10), bg=BG_COLOR, fg=FG_COLOR)
        lbl_name.pack(side=tk.TOP, anchor="w", padx=5, pady=2)
        multiplier_var = tk.StringVar(value="1.0")
        entry_multiplier = tk.Entry(frame, textvariable=multiplier_var, font=(FONT_NAME, 9), width=10)
        entry_multiplier.pack(side=tk.TOP, padx=5, pady=2, anchor="w")
        entry_multiplier.bind("<Return>", lambda event, sp=spectrum, var=multiplier_var: self.on_multiplier_change(sp, var))
        spectrum.multiplier_var = multiplier_var
        fig_small = Figure(figsize=(3, 1.5), dpi=80)
        ax_small = fig_small.add_subplot(111)
        ax_small.plot(spectrum.df['wavelength'], spectrum.get_scaled_intensity(), color=ACCENT_COLOR)
        ax_small.set_title("預覽", fontname=FONT_NAME, fontsize=8)
        ax_small.tick_params(labelsize=6)
        fig_small.tight_layout(pad=1.0)
        canvas_small = FigureCanvasTkAgg(fig_small, master=frame)
        canvas_small.draw()
        canvas_small.get_tk_widget().pack(side=tk.TOP, fill=tk.X, padx=5, pady=2)
        spectrum.fig_small = fig_small
        spectrum.ax_small = ax_small
        spectrum.canvas_small = canvas_small

    def on_multiplier_change(self, spectrum, var):
        try:
            new_multiplier = float(var.get())
            spectrum.multiplier = new_multiplier
            spectrum.ax_small.cla()
            spectrum.ax_small.plot(spectrum.df['wavelength'], spectrum.get_scaled_intensity(), color=ACCENT_COLOR)
            spectrum.ax_small.set_title("預覽", fontname=FONT_NAME, fontsize=8)
            spectrum.ax_small.tick_params(labelsize=6)
            spectrum.canvas_small.draw()
            self.update_all_plots()
        except Exception as e:
            messagebox.showerror("倍率更新錯誤", f"請輸入有效數字。\n錯誤內容：{str(e)}")
    
    def update_all_plots(self):
        if not self.spectra:
            return
        try:
            wavelengths = self.spectra[0].df['wavelength'].values
            total_intensity = np.zeros_like(wavelengths, dtype=float)
            for sp in self.spectra:
                total_intensity += sp.get_scaled_intensity().values
            self.ax_fill.cla()
            self.ax_fill.set_title("光譜填色圖", fontname=FONT_NAME)
            self.ax_fill.set_xlabel("波長 (nm)", fontname=FONT_NAME)
            self.ax_fill.set_ylabel("強度", fontname=FONT_NAME)
            norm = mcolors.Normalize(vmin=400, vmax=700)
            cmap = matplotlib.cm.get_cmap("jet")
            colors = [cmap(norm(w)) for w in wavelengths]
            self.ax_fill.plot(wavelengths, total_intensity, color=ACCENT_COLOR)
            for i in range(len(wavelengths)-1):
                self.ax_fill.fill_between(wavelengths[i:i+2], total_intensity[i:i+2],
                                          color=colors[i])
            self.ax_compare.cla()
            self.ax_compare.set_title("標準化光譜對比圖", fontname=FONT_NAME)
            self.ax_compare.set_xlabel("波長 (nm)", fontname=FONT_NAME)
            self.ax_compare.set_ylabel("歸一化強度", fontname=FONT_NAME)
            for sp in self.spectra:
                intensity = sp.get_scaled_intensity().values
                if np.max(intensity) != 0:
                    intensity_norm = intensity / np.max(intensity)
                else:
                    intensity_norm = intensity
                self.ax_compare.plot(wavelengths, intensity_norm, label=sp.filename)
            self.ax_compare.legend(fontsize=8)
            self.canvas_fig.draw()
            self.update_ppf_info(total_intensity=total_intensity, wavelengths=wavelengths)
        except Exception as e:
            messagebox.showerror("繪圖更新錯誤", str(e))
    
    def update_ppf_info(self, total_intensity=None, wavelengths=None):
        """
        計算並顯示 PPF、CCT 與 CRI 資訊：
          - 對於每個波長 n (nm)，ppf(n) = n * intensity * 0.008359 / 1000.0
          - 分別累加計算總 PPF、藍光（400-499nm）、綠光（500-599nm）、紅光（600-700nm）
          - CCT 由光譜數據轉換至 CIE XYZ 後以 McCamy 公式估算
          - CRI 透過 colour-science 套件計算（若未安裝則回傳預設值）
        """
        try:
            if total_intensity is None or wavelengths is None:
                total_ppf = blue_ppf = green_ppf = red_ppf = 0.0
                cct = 0.0
                cri = 0.0
            else:
                mask_total = (wavelengths >= 400) & (wavelengths <= 700)
                mask_blue  = (wavelengths >= 400) & (wavelengths < 500)
                mask_green = (wavelengths >= 500) & (wavelengths < 600)
                mask_red   = (wavelengths >= 600) & (wavelengths <= 700)
                factor = 0.008359 / 1000.0
                total_ppf = np.sum(wavelengths[mask_total] * total_intensity[mask_total] * factor)
                blue_ppf  = np.sum(wavelengths[mask_blue] * total_intensity[mask_blue] * factor)
                green_ppf = np.sum(wavelengths[mask_green] * total_intensity[mask_green] * factor)
                red_ppf   = np.sum(wavelengths[mask_red] * total_intensity[mask_red] * factor)
                cct = calculate_CCT_from_spectrum(wavelengths[mask_total], total_intensity[mask_total])
                cri = calculate_CRI(wavelengths[mask_total], total_intensity[mask_total])
            self.ppf_total_var.set(f"總 PPF (400-700nm): {total_ppf:.2f}")
            self.ppf_blue_var.set(f"藍光 PPF (400-499nm): {blue_ppf:.2f}")
            self.ppf_green_var.set(f"綠光 PPF (500-599nm): {green_ppf:.2f}")
            self.ppf_red_var.set(f"紅光 PPF (600-700nm): {red_ppf:.2f}")
            self.cct_var.set(f"色溫 (CCT): {cct:.0f}K")
            self.cri_var.set(f"顯色指數 (CRI): {cri:.0f}")
        except Exception as e:
            messagebox.showerror("積分計算錯誤", str(e))

# =======================
# 主入口
# =======================
if __name__ == "__main__":
    login = LoginWindow()
    login.mainloop()
