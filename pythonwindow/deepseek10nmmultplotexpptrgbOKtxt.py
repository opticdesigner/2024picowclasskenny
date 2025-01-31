import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# 設定全局樣式
BG_COLOR = "#F0F0F0"
ACCENT_COLOR = "#2C3E50"
BTN_COLOR = "#3498DB"
FONT_NAME = 'Microsoft JhengHei'

plt.style.use('ggplot')  # 使用更現代的繪圖樣式

def check_expiration():
    expire_date = datetime(2025, 3, 29)
    if datetime.now() > expire_date:
        messagebox.showerror("錯誤", "已經超過使用期限，請聯繫Steve Li")
        return False
    return True

class LoginWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("登入")
        self.root.geometry("400x250")
        self.root.configure(bg=BG_COLOR)
        self.setup_style()
        
        main_frame = ttk.Frame(self.root, style='Main.TFrame')
        main_frame.pack(pady=30, padx=20, fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text="光譜分析系統登入", style='Title.TLabel').pack(pady=15)
        ttk.Label(main_frame, text="Copyright (c) 2025 Steve Li", style='Title.TLabel').pack(pady=15)
        
        form_frame = ttk.Frame(main_frame)
        form_frame.pack(pady=10)
        
        ttk.Label(form_frame, text="使用者名稱:", style='Form.TLabel').grid(row=0, column=0, pady=5, sticky=tk.E)
        self.username_entry = ttk.Entry(form_frame, width=25, style='Form.TEntry')
        self.username_entry.grid(row=0, column=1, padx=10)
        
        ttk.Label(form_frame, text="密碼:", style='Form.TLabel').grid(row=1, column=0, pady=5, sticky=tk.E)
        self.password_entry = ttk.Entry(form_frame, show="*", width=25, style='Form.TEntry')
        self.password_entry.grid(row=1, column=1, padx=10)
        
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=15)
        ttk.Button(btn_frame, text="登入", command=self.check_credentials, style='Accent.TButton').pack(pady=5, ipadx=20)
        
        cp_frame = ttk.Frame(main_frame)
        cp_frame.pack(pady=15)
        ttk.Label(cp_frame, text="Copyright (c) 2025 Steve Li", style='Title.TLabel').pack(pady=15)
        
    def setup_style(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure('Main.TFrame', background=BG_COLOR)
        style.configure('Title.TLabel', font=(FONT_NAME, 14, 'bold'), foreground=ACCENT_COLOR, background=BG_COLOR)
        style.configure('Form.TLabel', font=(FONT_NAME, 10), foreground=ACCENT_COLOR, background=BG_COLOR)
        style.configure('Form.TEntry', fieldbackground='white', padding=5)
        style.configure('Accent.TButton', font=(FONT_NAME, 10, 'bold'), 
                       foreground='white', background=BTN_COLOR, 
                       borderwidth=0, focuscolor=BTN_COLOR)
        style.map('Accent.TButton',
                 background=[('active', '#2980B9'), ('pressed', '#2C3E50')])

    def check_credentials(self):
        if self.username_entry.get() == "WSL" and self.password_entry.get() == "50968758":
            self.root.destroy()
            main_window = MainWindow()
            main_window.run()
        else:
            messagebox.showerror("錯誤", "使用者名稱或密碼錯誤")

class MainWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("光譜分析工具 此程式的所有權屬於 Steve Li. Author: Steve Li. Created on: 2025-01-31")
        self.root.geometry("1280x800")
        self.root.minsize(1024, 600)
        self.setup_style()
        
        self.spectra_data = []
        self.figures = []
        self.canvases = []
        self.current_n = 0
        
        self.create_widgets()
        
    def setup_style(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure('Main.TFrame', background=BG_COLOR)
        style.configure('TButton', font=(FONT_NAME, 9), padding=6)
        style.configure('Accent.TButton', background=BTN_COLOR, foreground='white')
        style.map('Accent.TButton',
                 background=[('active', '#2980B9'), ('pressed', '#2C3E50')])
        style.configure('TLabelframe', font=(FONT_NAME, 10, 'bold'), borderwidth=2)
        style.configure('TLabelframe.Label', foreground=ACCENT_COLOR)
        
    def create_widgets(self):
        # 主容器
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 控制面板
        control_frame = ttk.Frame(main_container)
        control_frame.pack(fill=tk.X, pady=5)
        
        input_group = ttk.Frame(control_frame)
        input_group.pack(side=tk.LEFT, padx=10)
        
        ttk.Label(input_group, text="光譜數量 (1-10):", font=(FONT_NAME, 10)).pack(side=tk.LEFT)
        self.n_entry = ttk.Entry(input_group, width=5)
        self.n_entry.pack(side=tk.LEFT, padx=5)
        ttk.Button(input_group, text="生成圖表", command=self.generate_plots, style='Accent.TButton').pack(side=tk.LEFT, padx=5)
        
        ttk.Button(control_frame, text="退出系統", command=self.root.destroy, style='Accent.TButton').pack(side=tk.RIGHT, padx=10)
        
        # 主內容區
        content_frame = ttk.Frame(main_container)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # 左側可滾動區域
        scroll_frame = ttk.Frame(content_frame)
        scroll_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.left_canvas = tk.Canvas(scroll_frame, highlightthickness=0)
        self.left_scroll = ttk.Scrollbar(scroll_frame, orient="vertical", command=self.left_canvas.yview)
        self.left_frame = ttk.Frame(self.left_canvas)
        
        self.left_canvas.configure(yscrollcommand=self.left_scroll.set)
        self.left_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.left_scroll.pack(side=tk.LEFT, fill=tk.Y)
        self.left_canvas.create_window((0,0), window=self.left_frame, anchor="nw")
        
        # 右側分析區域
        right_frame = ttk.Frame(content_frame, width=400)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=10)
        
        # 圖表分頁
        notebook = ttk.Notebook(right_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # 總和圖表分頁
        sum_tab = ttk.Frame(notebook)
        self.sum_fig = plt.figure(figsize=(6,4), dpi=100)
        self.sum_ax = self.sum_fig.add_subplot(111)
        self.sum_canvas = FigureCanvasTkAgg(self.sum_fig, master=sum_tab)
        self.sum_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        notebook.add(sum_tab, text="總和光譜")
        
        # 正規化分頁
        norm_tab = ttk.Frame(notebook)
        self.norm_fig = plt.figure(figsize=(6,4), dpi=100)
        self.norm_ax = self.norm_fig.add_subplot(111)
        self.norm_canvas = FigureCanvasTkAgg(self.norm_fig, master=norm_tab)
        self.norm_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        notebook.add(norm_tab, text="正規化光譜")
        
        # PPF結果面板
        ppf_frame = ttk.LabelFrame(right_frame, text="PPF 計算結果", padding=(10,5))
        ppf_frame.pack(fill=tk.X, pady=10)
        
        result_grid = ttk.Frame(ppf_frame)
        result_grid.pack(fill=tk.X)
        
        self.create_ppf_row(result_grid, "總PPF:", 0)
        self.create_ppf_row(result_grid, "藍光PPF (400-499nm):", 1)
        self.create_ppf_row(result_grid, "綠光PPF (500-599nm):", 2)
        self.create_ppf_row(result_grid, "紅光PPF (600-700nm):", 3)
        
    def create_ppf_row(self, parent, text, row):
        ttk.Label(parent, text=text, font=(FONT_NAME, 9)).grid(row=row, column=0, sticky=tk.W, pady=2)
        label = ttk.Label(parent, text="0.00", font=(FONT_NAME, 9, 'bold'), foreground=ACCENT_COLOR)
        label.grid(row=row, column=1, sticky=tk.E, padx=10)
        # 修正标签绑定方式
        if row == 0:
            self.total_ppf_label = label
        elif row == 1:
            self.blue_ppf_label = label
        elif row == 2:
            self.green_ppf_label = label
        elif row == 3:
            self.red_ppf_label = label
        
    def generate_plots(self):
        try:
            n = int(self.n_entry.get())
            if n < 1 or n > 10:
                raise ValueError
        except ValueError:
            messagebox.showerror("錯誤", "請輸入1-10之間的數字")
            return
        
        # 清除舊元件
        for widget in self.left_frame.winfo_children():
            widget.destroy()
            
        self.figures = []
        self.canvases = []
        self.spectra_data = []
        self.current_n = n
        
        for i in range(n):
            frame = ttk.Frame(self.left_frame)
            frame.pack(fill=tk.X, pady=5, padx=5)
            
            fig = plt.figure(figsize=(8,3), dpi=100)
            ax = fig.add_subplot(111)
            ax.grid(True, linestyle='--', alpha=0.7)
            ax.set_facecolor('#F5F5F5')
            ax.tick_params(axis='both', which='both', labelsize=8)
            ax.set_title(f"光譜圖 {i+1}", fontname=FONT_NAME)
            ax.set_xlabel("nm", fontname=FONT_NAME)
            ax.set_ylabel("mw", fontname=FONT_NAME)
            
            canvas = FigureCanvasTkAgg(fig, master=frame)
            canvas.get_tk_widget().pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
            
            btn = ttk.Button(frame, text=f"載入檔案 {i+1}", 
                           command=lambda idx=i: self.load_file(idx),
                           style='Accent.TButton')
            btn.pack(side=tk.LEFT, padx=5)
            
            self.figures.append(fig)
            self.canvases.append(canvas)
            self.spectra_data.append(None)
            
        self.left_frame.update_idletasks()
        self.left_canvas.configure(scrollregion=self.left_canvas.bbox("all"))  # 修正滚动区域
        
    def load_file(self, index):
        filepath = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if not filepath:
            return
        
        try:
            with open(filepath, 'r') as f:
                header = f.readline().strip().split()
                if header != ['nm', 'mw']:
                    raise ValueError("檔案格式不正確")
                    
                data = {'nm': [], 'mw': []}
                for line in f:
                    values = line.strip().split()
                    if len(values) != 2:
                        continue
                    data['nm'].append(float(values[0]))
                    data['mw'].append(float(values[1]))
                    
                self.spectra_data[index] = data
                
                ax = self.figures[index].get_axes()[0]
                ax.clear()
                ax.plot(data['nm'], data['mw'], color='#3498DB', linewidth=1.5)
                ax.fill_between(data['nm'], data['mw'], color='#3498DB', alpha=0.3)
                ax.set_title(f"光譜圖 {index+1}", fontname=FONT_NAME)
                ax.set_xlabel("nm", fontname=FONT_NAME)
                ax.set_ylabel("mw", fontname=FONT_NAME)
                self.canvases[index].draw()
                self.update_sum_plots()
                
        except Exception as e:
            messagebox.showerror("錯誤", f"讀取檔案失敗: {str(e)}")
            
    def update_sum_plots(self):
        if not all(self.spectra_data):
            return
            
        sum_mw = [0] * 301
        for data in self.spectra_data:
            if data:
                for i, val in enumerate(data['mw']):
                    if i < len(sum_mw):
                        sum_mw[i] += val
                    
        max_val = max(sum_mw) if sum_mw else 1
        norm_mw = [val/max_val for val in sum_mw] if max_val != 0 else [0]*301
        
        # 更新總和圖
        self.sum_ax.clear()
        self.sum_ax.plot(range(400,701), sum_mw, color='#E74C3C', linewidth=2)
        self.sum_ax.fill_between(range(400,701), sum_mw, color='#E74C3C', alpha=0.3)
        self.sum_ax.set_title("總和光譜圖", fontname=FONT_NAME)
        self.sum_ax.set_xlabel("nm", fontname=FONT_NAME)
        self.sum_ax.set_ylabel("mw", fontname=FONT_NAME)
        self.sum_canvas.draw()
        
        # 更新正規化圖
        self.norm_ax.clear()
        self.norm_ax.plot(range(400,701), norm_mw, color='#27AE60', linewidth=2)
        self.norm_ax.fill_between(range(400,701), norm_mw, color='#27AE60', alpha=0.3)
        self.norm_ax.set_title("正規化光譜圖", fontname=FONT_NAME)
        self.norm_ax.set_xlabel("nm", fontname=FONT_NAME)
        self.norm_ax.set_ylabel("強度", fontname=FONT_NAME)
        self.norm_canvas.draw()
        
        # PPF計算
        total_ppf = 0.0
        ppf_blue = 0.0
        ppf_green = 0.0
        ppf_red = 0.0

        for i in range(len(sum_mw)):
            wavelength = 400 + i
            mw = sum_mw[i]
            ppf_value = wavelength * mw * 0.008359 / 1000.0
            total_ppf += ppf_value

            if 400 <= wavelength <= 499:
                ppf_blue += ppf_value
            elif 500 <= wavelength <= 599:
                ppf_green += ppf_value
            elif 600 <= wavelength <= 700:
                ppf_red += ppf_value

        # 更新PPF顯示
        self.total_ppf_label.config(text=f"{total_ppf:.2f}")
        self.blue_ppf_label.config(text=f"{ppf_blue:.2f}")
        self.green_ppf_label.config(text=f"{ppf_green:.2f}")
        self.red_ppf_label.config(text=f"{ppf_red:.2f}")
        
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    if check_expiration():
        login = LoginWindow()
        login.root.mainloop()