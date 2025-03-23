import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import datetime
import os

import numpy as np
import pandas as pd
import colour
from colour.temperature import CCT_to_xy_CIE_D, xy_to_CCT_CIE_D
from colour.colorimetry import (
    SpectralDistribution,
    SPECTRAL_SHAPE_DEFAULT,
    sd_to_XYZ,
    wavelength_to_XYZ

)
from colour.quality import colour_rendering_index

import matplotlib
matplotlib.use('TkAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt

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
EXPIRE_DATE = datetime.datetime(2025, 3, 30)

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
            # 假設 CSV 檔案有兩欄：wavelength, intensity
            self.df = pd.read_csv(self.filepath)
            # 檢查必要欄位
            if not {'wavelength', 'intensity'}.issubset(self.df.columns):
                raise ValueError("CSV 檔案格式錯誤，必須包含 'wavelength' 與 'intensity' 欄位")
            # 轉換資料型態，確保為數值型
            self.df['wavelength'] = pd.to_numeric(self.df['wavelength'], errors='coerce')
            self.df['intensity'] = pd.to_numeric(self.df['intensity'], errors='coerce')
            self.df.dropna(inplace=True)
            # 依波長排序（由小到大）
            self.df.sort_values('wavelength', inplace=True)
        except Exception as e:
            raise Exception(f"載入檔案 {self.filename} 失敗：{str(e)}")
    
    def get_scaled_intensity(self):
        """回傳倍率調整後的光譜資料"""
        return self.df['intensity'] * self.multiplier
    
    def get_spectral_distribution(self):
        """將光譜資料轉換為 colour-science SpectralDistribution 物件"""
        data = dict(zip(self.df['wavelength'], self.get_scaled_intensity()))
        return SpectralDistribution(data)

# =======================
# 光譜計算功能
# =======================
def calculate_cct_ra(wavelengths, intensity):
    """計算相關色溫(CCT)和顯色指數(Ra)"""
    try:
        # 建立光譜分布物件
        spd = SpectralDistribution(dict(zip(wavelengths, intensity)))
        
        # 計算 XYZ 三刺激值
        # XYZ = spectral_to_XYZ(spd)
        XYZ = sd_to_XYZ(spd)
        # 計算色度座標
        xy = colour.XYZ_to_xy(XYZ)
        
        # 計算相關色溫 (CCT)
        try:
            cct = xy_to_CCT_CIE_D(xy)
        except RuntimeError:
            cct = 0  # 若計算失敗，返回 0
        
        # 計算顯色指數 (Ra)
        try:
            ra = colour_rendering_index(spd)
        except Exception:
            ra = 0  # 若計算失敗，返回 0
        
        return cct, ra
    except Exception as e:
        print(f"CCT/Ra calculation error: {str(e)}")
        return 0, 0

# =======================
# 登入視窗
# =======================
class LoginWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("GrowGenie Spectrum Generator - Copyright (c) 2025 Steve Li  All rights reserved. 此程式碼由 Steve Li 擁有，未經授權不得複製、修改或分發。")
        self.configure(bg=BG_COLOR)
        self.geometry("400x250")
        # self.resizable(False, False)
        self.resizable(True, True)
        # 視窗置中
        self.center_window(400, 250)
        self.create_widgets()
    
    def center_window(self, width, height):
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = int((screen_width - width) / 2)
        y = int((screen_height - height) / 2)
        self.geometry(f"{width}x{height}+{x}+{y}")
    
    def create_widgets(self):
        # 檢查是否已過期
        now = datetime.datetime.now()
        if now > EXPIRE_DATE:
            label = tk.Label(self, text="軟體已過期，請聯絡著作者:Steve Li", 
                             font=(FONT_NAME, 12), bg=BG_COLOR, fg="red")
            label.pack(expand=True)
            return

        # 使用者名稱標籤與輸入框
        lbl_user = tk.Label(self, text="使用者名稱：", font=(FONT_NAME, 12), bg=BG_COLOR, fg=FG_COLOR)
        lbl_user.pack(pady=(30, 5))
        self.entry_user = tk.Entry(self, font=(FONT_NAME, 12))
        self.entry_user.pack(pady=5)
        # 密碼標籤與輸入框
        lbl_pass = tk.Label(self, text="密碼：", font=(FONT_NAME, 12), bg=BG_COLOR, fg=FG_COLOR)
        lbl_pass.pack(pady=5)
        self.entry_pass = tk.Entry(self, font=(FONT_NAME, 12), show="*")
        self.entry_pass.pack(pady=5)
        # 登入按鈕
        btn_login = tk.Button(self, text="登入", font=(FONT_NAME, 12), bg=ACCENT_COLOR, fg=FG_COLOR,
                              command=self.check_login)
        btn_login.pack(pady=(20,10))

        lbl_pass = tk.Label(self, text="Copyright (c) 2025 Steve Li", font=(FONT_NAME, 12), bg=BG_COLOR, fg=FG_COLOR)
        lbl_pass.pack(pady=5)

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
        self.title("高精度光譜分析工具 Copyright (c) 2025 Steve Li  All rights reserved. 此程式碼由 Steve Li 擁有，未經授權不得複製、修改或分發。 ")
        self.configure(bg=BG_COLOR)
        self.geometry(f"{APP_WIDTH}x{APP_HEIGHT}")
        self.center_window(APP_WIDTH, APP_HEIGHT)
        self.spectra = []  # 儲存 SpectrumData 物件
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
        file_menu.add_command(label="載入光譜資料", command=self.load_spectra)
        file_menu.add_separator()
        file_menu.add_command(label="離開", command=self.quit)
        menubar.add_cascade(label="檔案", menu=file_menu)
        self.config(menu=menubar)

    def create_widgets(self):
        # 建立一個 PanedWindow，左右兩邊皆可調整大小
        self.paned = tk.PanedWindow(self, orient=tk.HORIZONTAL, bg=BG_COLOR)
        self.paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 左側區域
        self.left_frame = tk.Frame(self.paned, bg=BG_COLOR)
        self.create_left_panel()  # 建立左側滾動區域
        self.paned.add(self.left_frame, minsize=300)  # 設定最小寬度

        # 右側區域
        self.right_frame = tk.Frame(self.paned, bg=BG_COLOR)
        self.create_right_panel()  # 建立右側 Matplotlib 區域
        self.paned.add(self.right_frame, minsize=500)

        # 底部：顯示積分計算結果，每項單獨一列
        self.status_frame = tk.Frame(self, bg=BG_COLOR)
        self.status_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)

        self.ppf_total_var = tk.StringVar()
        self.ppf_blue_var  = tk.StringVar()
        self.ppf_green_var = tk.StringVar()
        self.ppf_red_var   = tk.StringVar()
        self.cct_var = tk.StringVar()
        self.ra_var = tk.StringVar()

        lbl_total = tk.Label(self.status_frame, textvariable=self.ppf_total_var, font=(FONT_NAME, 12),
                             bg=BG_COLOR, fg=FG_COLOR)
        lbl_blue  = tk.Label(self.status_frame, textvariable=self.ppf_blue_var,  font=(FONT_NAME, 12),
                             bg=BG_COLOR, fg=FG_COLOR)
        lbl_green = tk.Label(self.status_frame, textvariable=self.ppf_green_var, font=(FONT_NAME, 12),
                             bg=BG_COLOR, fg=FG_COLOR)
        lbl_red   = tk.Label(self.status_frame, textvariable=self.ppf_red_var,   font=(FONT_NAME, 12),
                             bg=BG_COLOR, fg=FG_COLOR)
        lbl_cct   = tk.Label(self.status_frame, textvariable=self.cct_var, font=(FONT_NAME, 12),
                             bg=BG_COLOR, fg=FG_COLOR)
        lbl_ra    = tk.Label(self.status_frame, textvariable=self.ra_var, font=(FONT_NAME, 12),
                             bg=BG_COLOR, fg=FG_COLOR)
        
        # 每項單獨一列顯示
        lbl_total.pack(anchor="w", padx=10)
        lbl_blue.pack(anchor="w", padx=10)
        lbl_green.pack(anchor="w", padx=10)
        lbl_red.pack(anchor="w", padx=10)
        lbl_cct.pack(anchor="w", padx=10)
        lbl_ra.pack(anchor="w", padx=10)

        self.update_ppf_info()

    def create_left_panel(self):
        # 使用 Canvas + Scrollbar 實現滾動區域
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
        # 設定 Matplotlib 的深色主題
        plt.style.use('dark_background')

        self.fig = Figure(figsize=(8, 8), dpi=100)
        # 上子圖：精確光譜填色圖
        self.ax_fill = self.fig.add_subplot(211)
        self.ax_fill.set_title("光譜填色圖", fontname=FONT_NAME)
        self.ax_fill.set_xlabel("波長 (nm)", fontname=FONT_NAME)
        self.ax_fill.set_ylabel("強度", fontname=FONT_NAME)
        # 下子圖：標準化光譜對比折線圖
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
            # messagebox.showerror("錯誤", "最多同時
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
        # 每個光譜在左側顯示一個子框架，包含檔名、倍率輸入框及預覽圖
        frame = tk.Frame(self.scrollable_frame, bg=BG_COLOR, bd=1, relief=tk.RIDGE)
        frame.pack(fill=tk.X, padx=5, pady=5)

        lbl_name = tk.Label(frame, text=spectrum.filename, font=(FONT_NAME, 10), bg=BG_COLOR, fg=FG_COLOR)
        lbl_name.pack(side=tk.TOP, anchor="w", padx=5, pady=2)

        # 倍率手動輸入框，預設值為 1.0
        multiplier_var = tk.StringVar(value="1.0")
        entry_multiplier = tk.Entry(frame, textvariable=multiplier_var, font=(FONT_NAME, 9), width=10)
        entry_multiplier.pack(side=tk.TOP, padx=5, pady=2, anchor="w")
        entry_multiplier.insert(0, "1.0")
        # 綁定「Enter」鍵事件，當使用者輸入數字後按下 Enter 進行更新
        entry_multiplier.bind("<Return>", lambda event, sp=spectrum, var=multiplier_var: self.on_multiplier_change(sp, var))
        # 將 multiplier_var 保存到 spectrum 物件中，方便日後參考
        spectrum.multiplier_var = multiplier_var

        # 小型 Matplotlib 圖形顯示該光譜
        fig_small = Figure(figsize=(3, 1.5), dpi=80)
        ax_small = fig_small.add_subplot(111)
        ax_small.plot(spectrum.df['wavelength'], spectrum.get_scaled_intensity(), color=ACCENT_COLOR)
        ax_small.set_title("預覽", fontname=FONT_NAME, fontsize=8)
        ax_small.tick_params(labelsize=6)
        fig_small.tight_layout(pad=1.0)

        canvas_small = FigureCanvasTkAgg(fig_small, master=frame)
        canvas_small.draw()
        canvas_small.get_tk_widget().pack(side=tk.TOP, fill=tk.X, padx=5, pady=2)

        # 將小圖控制元件保存到 spectrum 物件中，方便後續更新
        spectrum.fig_small = fig_small
        spectrum.ax_small = ax_small
        spectrum.canvas_small = canvas_small

    def on_multiplier_change(self, spectrum, var):
        try:
            # 嘗試將手動輸入的倍率轉成浮點數
            new_multiplier = float(var.get())
            spectrum.multiplier = new_multiplier
            # 更新該光譜的小圖
            spectrum.ax_small.cla()
            spectrum.ax_small.plot(spectrum.df['wavelength'], spectrum.get_scaled_intensity(), color=ACCENT_COLOR)
            spectrum.ax_small.set_title("預覽", fontname=FONT_NAME, fontsize=8)
            spectrum.ax_small.tick_params(labelsize=6)
            spectrum.canvas_small.draw()
            # 更新整體圖形與積分資訊
            self.update_all_plots()
        except Exception as e:
            messagebox.showerror("倍率更新錯誤", f"請輸入有效數字。\n錯誤內容：{str(e)}")
    
    def update_all_plots(self):
        # 計算總光譜：各光譜資料疊加（倍率調整後）
        if not self.spectra:
            return
        try:
            # 假設所有光譜覆蓋的波長範圍一致，以第一組為準
            wavelengths = self.spectra[0].df['wavelength'].values
            total_intensity = np.zeros_like(wavelengths, dtype=float)
            for sp in self.spectra:
                total_intensity += sp.get_scaled_intensity().values
            # 更新右側上方填色圖：利用線性分段色階映射（從400nm 紫色漸變至700nm 紅色）
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
            # 更新右側下方：標準化各光譜對比折線圖
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
            # 更新積分資訊
            self.update_ppf_info(total_intensity=total_intensity, wavelengths=wavelengths)
        except Exception as e:
            messagebox.showerror("繪圖更新錯誤", str(e))
    
    def update_ppf_info(self, total_intensity=None, wavelengths=None):
        """
        計算並顯示 PPF、CCT 與 Ra 資訊
        """
        try:
            if total_intensity is None or wavelengths is None:
                total_ppf = blue_ppf = green_ppf = red_ppf = 0.0
                cct = ra = 0.0
            else:
                # PPF 計算
                mask_total = (wavelengths >= 400) & (wavelengths <= 700)
                mask_blue  = (wavelengths >= 400) & (wavelengths < 500)
                mask_green = (wavelengths >= 500) & (wavelengths < 600)
                mask_red   = (wavelengths >= 600) & (wavelengths <= 700)

                factor = 0.008359 / 1000.0

                total_ppf = np.sum(wavelengths[mask_total] * total_intensity[mask_total] * factor)
                blue_ppf  = np.sum(wavelengths[mask_blue]  * total_intensity[mask_blue]  * factor)
                green_ppf = np.sum(wavelengths[mask_green] * total_intensity[mask_green] * factor)
                red_ppf   = np.sum(wavelengths[mask_red]   * total_intensity[mask_red]   * factor)

                # CCT 與 Ra 計算
                cct, ra = calculate_cct_ra(wavelengths[mask_total], total_intensity[mask_total])

            # 更新顯示資訊
            self.ppf_total_var.set(f"總 PPF (400-700nm): {total_ppf:.2f}")
            self.ppf_blue_var.set(f"藍光 PPF (400-499nm): {blue_ppf:.2f}")
            self.ppf_green_var.set(f"綠光 PPF (500-599nm): {green_ppf:.2f}")
            self.ppf_red_var.set(f"紅光 PPF (600-700nm): {red_ppf:.2f}")
            self.cct_var.set(f"相關色溫 (CCT): {cct:.1f}K")
            self.ra_var.set(f"顯色指數 (Ra): {ra:.1f}")

        except Exception as e:
            messagebox.showerror("計算錯誤", str(e))

# =======================
# 主入口
# =======================
if __name__ == "__main__":
    login = LoginWindow()
    login.mainloop()