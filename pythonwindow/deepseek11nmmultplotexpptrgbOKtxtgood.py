import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# 設定全局樣式
BG_COLOR = "#F0F0F0"
PRIMARY_COLOR = "#2C3E50"
SECONDARY_COLOR = "#3498DB"
ACCENT_COLOR = "#E74C3C"
TEXT_COLOR = "#2C3E50"

try:
    plt.style.use('seaborn-v0_8')  # 修正樣式名稱
except Exception:
    plt.style.use('ggplot')  # 備用樣式

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
        self.root.configure(bg=PRIMARY_COLOR)
        
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TLabel', background=PRIMARY_COLOR, foreground='white', font=('Microsoft JhengHei', 12))
        style.configure('TEntry', font=('Microsoft JhengHei', 12), padding=5)
        style.configure('TButton', font=('Microsoft JhengHei', 12, 'bold'), 
                       background=SECONDARY_COLOR, foreground='white', padding=10)
        
        # 修正frame名稱
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
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("光譜分析工具 - 專業版")
        self.root.geometry("1280x800")
        self.root.configure(bg=BG_COLOR)
        
        self.setup_style()
        self.spectra_data = []
        self.figures = []
        self.canvases = []
        self.current_n = 0
        
        self.create_widgets()
        self.root.protocol("WM_DELETE_WINDOW", self.exit_program)
        
    def setup_style(self):
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
        control_frame = ttk.Frame(self.root, padding=(20, 10))
        control_frame.pack(fill=tk.X)
        
        ttk.Label(control_frame, text="光譜數量 (1-10):", font=('Microsoft JhengHei', 11)).pack(side=tk.LEFT, padx=10)
        self.n_entry = ttk.Entry(control_frame, width=5, font=('Microsoft JhengHei', 11))
        self.n_entry.pack(side=tk.LEFT)
        
        ttk.Button(control_frame, text="生成圖表", command=self.generate_plots).pack(side=tk.LEFT, padx=20)
        ttk.Button(control_frame, text="退出系統", command=self.exit_program).pack(side=tk.RIGHT)
        
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.left_canvas = tk.Canvas(main_frame, bg=BG_COLOR, highlightthickness=0)
        self.left_scroll = ttk.Scrollbar(main_frame, orient="vertical", command=self.left_canvas.yview)
        self.left_frame = ttk.Frame(self.left_canvas)
        
        self.left_canvas.configure(yscrollcommand=self.left_scroll.set)
        self.left_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.left_scroll.pack(side=tk.LEFT, fill=tk.Y)
        self.left_canvas.create_window((0,0), window=self.left_frame, anchor="nw")
        
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=10)
        
        chart_frame = ttk.Frame(right_frame)
        chart_frame.pack(fill=tk.BOTH, expand=True)
        
        self.sum_fig = plt.figure(figsize=(6,3.5), facecolor=BG_COLOR)
        self.sum_ax = self.sum_fig.add_subplot(111)
        self.sum_ax.set_facecolor(BG_COLOR)
        self.sum_canvas = FigureCanvasTkAgg(self.sum_fig, master=chart_frame)
        self.sum_canvas.get_tk_widget().pack(fill=tk.BOTH, pady=5)
        
        self.norm_fig = plt.figure(figsize=(6,3.5), facecolor=BG_COLOR)
        self.norm_ax = self.norm_fig.add_subplot(111)
        self.norm_ax.set_facecolor(BG_COLOR)
        self.norm_canvas = FigureCanvasTkAgg(self.norm_fig, master=chart_frame)
        self.norm_canvas.get_tk_widget().pack(fill=tk.BOTH, pady=5)
        
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
        try:
            n = int(self.n_entry.get())
            if n < 1 or n > 10:
                raise ValueError("數值超出範圍")
        except ValueError as e:
            messagebox.showerror("輸入錯誤", "請輸入1-10之間的整數")
            return
        except Exception as e:
            messagebox.showerror("系統錯誤", f"發生未預期錯誤: {str(e)}")
            return
        
        for widget in self.left_frame.winfo_children():
            widget.destroy()
        
        self.figures = []
        self.canvases = []
        self.spectra_data = []
        self.current_n = n
        
        try:
            for i in range(n):
                frame = ttk.Frame(self.left_frame, padding=10)
                frame.pack(fill=tk.X, pady=5, padx=5)
                frame.config(relief='groove', borderwidth=1)
                
                fig = plt.figure(figsize=(8,2.5), facecolor=BG_COLOR)
                ax = fig.add_subplot(111)
                ax.set_facecolor(BG_COLOR)
                ax.tick_params(colors=TEXT_COLOR)
                for spine in ax.spines.values():
                    spine.set_color(TEXT_COLOR)
                
                canvas = FigureCanvasTkAgg(fig, master=frame)
                canvas.get_tk_widget().pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
                
                btn_frame = ttk.Frame(frame)
                btn_frame.pack(side=tk.LEFT, padx=10)
                ttk.Button(btn_frame, text=f"載入光譜 {i+1}", 
                          command=lambda idx=i: self.load_file(idx)).pack(pady=5)
                
                self.figures.append(fig)
                self.canvases.append(canvas)
                self.spectra_data.append(None)
                
            self.left_frame.update_idletasks()
            self.left_canvas.configure(scrollregion=self.left_canvas.bbox("all"))
        except Exception as e:
            messagebox.showerror("系統錯誤", f"生成圖表失敗: {str(e)}")
        
    def load_file(self, index):
        filepath = filedialog.askopenfilename(filetypes=[("文字檔案", "*.txt")])
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
                ax.plot(data['nm'], data['mw'], color=SECONDARY_COLOR, linewidth=1.5)
                ax.set_title(f"光譜圖 {index+1}", fontname='Microsoft JhengHei', 
                            color=TEXT_COLOR, pad=10)
                ax.set_xlabel("波長 (nm)", fontname='Microsoft JhengHei', color=TEXT_COLOR)
                ax.set_ylabel("強度 (mw)", fontname='Microsoft JhengHei', color=TEXT_COLOR)
                ax.grid(True, alpha=0.3)
                self.canvases[index].draw()
                self.update_sum_plots()
                
        except Exception as e:
            messagebox.showerror("檔案錯誤", f"讀取失敗: {str(e)}")
            
    def update_sum_plots(self):
        if not all(self.spectra_data):
            return
            
        try:
            sum_mw = [0] * 301
            for data in self.spectra_data:
                if data:
                    for i, val in enumerate(data['mw']):
                        sum_mw[i] += val
                        
            self.sum_ax.clear()
            self.sum_ax.plot(range(400,701), sum_mw, color=PRIMARY_COLOR)
            self.sum_ax.set_title("總和光譜圖", fontname='Microsoft JhengHei', 
                                color=TEXT_COLOR, pad=10)
            self.sum_ax.set_xlabel("波長 (nm)", fontname='Microsoft JhengHei', color=TEXT_COLOR)
            self.sum_ax.set_ylabel("強度 (mw)", fontname='Microsoft JhengHei', color=TEXT_COLOR)
            self.sum_ax.grid(True, alpha=0.3)
            self.sum_canvas.draw()
            
            max_val = max(sum_mw) if sum_mw else 1
            norm_mw = [val/max_val for val in sum_mw] if max_val != 0 else [0]*301
            self.norm_ax.clear()
            self.norm_ax.plot(range(400,701), norm_mw, color=SECONDARY_COLOR)
            self.norm_ax.set_title("正規化光譜圖", fontname='Microsoft JhengHei', 
                                 color=TEXT_COLOR, pad=10)
            self.norm_ax.set_xlabel("波長 (nm)", fontname='Microsoft JhengHei', color=TEXT_COLOR)
            self.norm_ax.set_ylabel("相對強度", fontname='Microsoft JhengHei', color=TEXT_COLOR)
            self.norm_ax.grid(True, alpha=0.3)
            self.norm_canvas.draw()
            
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

            self.ppf_label_0.config(text=f"{total_ppf:.2f} μmol/s")
            self.ppf_label_1.config(text=f"{ppf_blue:.2f} μmol/s")
            self.ppf_label_2.config(text=f"{ppf_green:.2f} μmol/s")
            self.ppf_label_3.config(text=f"{ppf_red:.2f} μmol/s")
        except Exception as e:
            messagebox.showerror("計算錯誤", f"更新圖表失敗: {str(e)}")
    
    def exit_program(self):
        try:
            plt.close('all')
            self.root.quit()
            self.root.destroy()
        except Exception as e:
            os._exit(0)  # 强制退出

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    if check_expiration():
        login = LoginWindow()
        try:
            login.root.mainloop()
        except KeyboardInterrupt:
            pass