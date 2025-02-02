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

# 新增顏色科學相關套件
import colour
from colour.colorimetry import (SpectralDistribution, MSDS_CMFS,
                                SDS_ILLUMINANTS, sd_to_XYZ)
# from colour.temperature.mccamy_1992 import xy_to_CCT_McCamy
# 修正導入語句
from colour.temperature import xy_to_CCT  # 使用新的函數
from colour.quality import colour_rendering_index

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
EXPIRE_DATE = datetime.datetime(2025, 2, 28)

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
        return self.df['intensity'] * self.multiplier

# =======================
# 登入視窗（保持不變）
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
            label = tk.Label(self, text="軟體已過期，請聯絡著作者:Steve Li", 
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
# 主程式視窗（修改部分）
# =======================
class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("高精度光譜分析工具")
        self.configure(bg=BG_COLOR)
        self.geometry(f"{APP_WIDTH}x{APP_HEIGHT}")
        self.center_window(APP_WIDTH, APP_HEIGHT)
        self.spectra = []
        self.create_menu()
        self.create_widgets()
        # 新增 CCT 和 Ra 的顯示變數
        self.cct_var = tk.StringVar()
        self.ra_var = tk.StringVar()
    
    def center_window(self, width, height):
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = int((screen_width - width) / 2)
        y = int((screen_height - height) / 2)
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

        # 新增 CCT 和 Ra 顯示標籤
        self.ppf_total_var = tk.StringVar()
        self.ppf_blue_var  = tk.StringVar()
        self.ppf_green_var = tk.StringVar()
        self.ppf_red_var   = tk.StringVar()
        self.cct_var       = tk.StringVar()
        self.ra_var        = tk.StringVar()

        labels = [
            tk.Label(self.status_frame, textvariable=self.ppf_total_var, font=(FONT_NAME, 12), bg=BG_COLOR, fg=FG_COLOR),
            tk.Label(self.status_frame, textvariable=self.ppf_blue_var,  font=(FONT_NAME, 12), bg=BG_COLOR, fg=FG_COLOR),
            tk.Label(self.status_frame, textvariable=self.ppf_green_var, font=(FONT_NAME, 12), bg=BG_COLOR, fg=FG_COLOR),
            tk.Label(self.status_frame, textvariable=self.ppf_red_var,   font=(FONT_NAME, 12), bg=BG_COLOR, fg=FG_COLOR),
            tk.Label(self.status_frame, textvariable=self.cct_var,       font=(FONT_NAME, 12), bg=BG_COLOR, fg=FG_COLOR),
            tk.Label(self.status_frame, textvariable=self.ra_var,        font=(FONT_NAME, 12), bg=BG_COLOR, fg=FG_COLOR)
        ]

        for lbl in labels:
            lbl.pack(anchor="w", padx=10)

        self.update_ppf_info()

    def create_left_panel(self):
        self.canvas = tk.Canvas(self.left_frame, bg=BG_COLOR, highlightthickness=0)
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
        try:
            if total_intensity is None or wavelengths is None:
                total_ppf = blue_ppf = green_ppf = red_ppf = 0.0
                self.cct_var.set("相關色溫 (CCT): N/A")
                self.ra_var.set("顯色指數 (Ra): N/A")
            else:
                # PPF 計算（保持原有邏輯）
                mask_total = (wavelengths >= 400) & (wavelengths <= 700)
                mask_blue  = (wavelengths >= 400) & (wavelengths < 500)
                mask_green = (wavelengths >= 500) & (wavelengths < 600)
                mask_red   = (wavelengths >= 600) & (wavelengths <= 700)

                factor = 0.008359 / 1000.0

                total_ppf = np.sum(wavelengths[mask_total] * total_intensity[mask_total] * factor)
                blue_ppf  = np.sum(wavelengths[mask_blue]  * total_intensity[mask_blue]  * factor)
                green_ppf = np.sum(wavelengths[mask_green] * total_intensity[mask_green] * factor)
                red_ppf   = np.sum(wavelengths[mask_red]   * total_intensity[mask_red]   * factor)

                # 新增 CCT 和 Ra 計算
                try:
                    # 將光譜資料轉換為 colour 套件可處理的格式
                    spectral_data = dict(zip(wavelengths, total_intensity))
                    sd = SpectralDistribution(spectral_data, name="Spectrum")

                    # 計算 CCT (相關色溫)
                    cmfs = MSDS_CMFS["CIE 1931 2 Degree Standard Observer"]
                    illuminant = SDS_ILLUMINANTS["D65"]
                    XYZ = sd_to_XYZ(sd, cmfs, illuminant)
                    xy = colour.XYZ_to_xy(XYZ)
                    cct = xy_to_CCT(xy, method="McCamy 1992")
                    self.cct_var.set(f"相關色溫 (CCT): {cct:.1f} K")

                    # 計算 Ra (顯色指數)
                    try:
                        ra = colour_rendering_index(sd, additional_data=True)['CRI']
                        self.ra_var.set(f"顯色指數 (Ra): {ra:.1f}")
                    except Exception as e:
                        self.ra_var.set(f"顯色指數 (Ra): 計算失敗 ({str(e)})")
                except Exception as e:
                    self.cct_var.set(f"相關色溫 (CCT): 計算失敗 ({str(e)})")
                    self.ra_var.set(f"顯色指數 (Ra): 計算失敗 ({str(e)})")

            # 更新 PPF 資訊
            self.ppf_total_var.set(f"總 PPF (400-700nm): {total_ppf:.2f}")
            self.ppf_blue_var.set(f"藍光 PPF (400-499nm): {blue_ppf:.2f}")
            self.ppf_green_var.set(f"綠光 PPF (500-599nm): {green_ppf:.2f}")
            self.ppf_red_var.set(f"紅光 PPF (600-700nm): {red_ppf:.2f}")
        except Exception as e:
            messagebox.showerror("積分計算錯誤", str(e))

# =======================
# 主入口
# =======================
if __name__ == "__main__":
    login = LoginWindow()
    login.mainloop()