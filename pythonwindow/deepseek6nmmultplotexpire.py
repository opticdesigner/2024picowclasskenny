import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# 檢查使用期限
def check_expiration():
    expire_date = datetime(2025, 3, 29)
    if datetime.now() > expire_date:
        messagebox.showerror("錯誤", "已經超過使用期限，請聯繫Steve Li")
        return False
    return True

# 登入視窗
class LoginWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("登入")
        self.root.geometry("300x150")
        
        ttk.Label(self.root, text="使用者名稱:", font=('Microsoft JhengHei', 10)).pack(pady=5)
        self.username_entry = ttk.Entry(self.root)
        self.username_entry.pack()
        
        ttk.Label(self.root, text="密碼:", font=('Microsoft JhengHei', 10)).pack(pady=5)
        self.password_entry = ttk.Entry(self.root, show="*")
        self.password_entry.pack()
        
        ttk.Button(self.root, text="登入", command=self.check_credentials).pack(pady=10)

    def check_credentials(self):
        if self.username_entry.get() == "WSL" and self.password_entry.get() == "50968758":
            self.root.destroy()
            main_window = MainWindow()
            main_window.run()
        else:
            messagebox.showerror("錯誤", "使用者名稱或密碼錯誤")

# 主視窗
class MainWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("光譜分析工具")
        self.root.geometry("1200x800")
        
        self.spectra_data = []
        self.figures = []
        self.canvases = []
        self.current_n = 0
        
        self.create_widgets()
        
    def create_widgets(self):
        # 控制面板
        control_frame = ttk.Frame(self.root)
        control_frame.pack(fill=tk.X)
        
        ttk.Label(control_frame, text="光譜數量 (1-10):", font=('Microsoft JhengHei', 10)).pack(side=tk.LEFT)
        self.n_entry = ttk.Entry(control_frame, width=5)
        self.n_entry.pack(side=tk.LEFT)
        ttk.Button(control_frame, text="確認", command=self.generate_plots).pack(side=tk.LEFT)
        ttk.Button(control_frame, text="退出", command=self.root.destroy).pack(side=tk.RIGHT)
        
        # 主要顯示區域
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 左側光譜圖
        self.left_canvas = tk.Canvas(main_frame)
        self.left_scroll = ttk.Scrollbar(main_frame, orient="vertical", command=self.left_canvas.yview)
        self.left_frame = ttk.Frame(self.left_canvas)
        
        self.left_canvas.configure(yscrollcommand=self.left_scroll.set)
        self.left_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.left_scroll.pack(side=tk.LEFT, fill=tk.Y)
        self.left_canvas.create_window((0,0), window=self.left_frame, anchor="nw")
        
        # 右側總和圖
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self.sum_fig = plt.figure(figsize=(6,4))
        self.sum_ax = self.sum_fig.add_subplot(111)
        self.sum_canvas = FigureCanvasTkAgg(self.sum_fig, master=right_frame)
        self.sum_canvas.get_tk_widget().pack()
        
        self.norm_fig = plt.figure(figsize=(6,4))
        self.norm_ax = self.norm_fig.add_subplot(111)
        self.norm_canvas = FigureCanvasTkAgg(self.norm_fig, master=right_frame)
        self.norm_canvas.get_tk_widget().pack()
        
    def generate_plots(self):
        try:
            n = int(self.n_entry.get())
            if n < 1 or n > 10:
                raise ValueError
        except ValueError:
            messagebox.showerror("錯誤", "請輸入1-10之間的數字")
            return
        
        # 清除舊資料
        for widget in self.left_frame.winfo_children():
            widget.destroy()
        self.figures = []
        self.canvases = []
        self.spectra_data = []
        self.current_n = n
        
        # 生成新圖表
        for i in range(n):
            frame = ttk.Frame(self.left_frame)
            frame.pack(fill=tk.X, pady=5)
            
            fig = plt.figure(figsize=(8,3))
            ax = fig.add_subplot(111)
            ax.set_title(f"光譜圖 {i+1}", fontname='Microsoft JhengHei')
            ax.set_xlabel("nm", fontname='Microsoft JhengHei')
            ax.set_ylabel("mw", fontname='Microsoft JhengHei')
            
            canvas = FigureCanvasTkAgg(fig, master=frame)
            canvas.get_tk_widget().pack(side=tk.RIGHT)
            
            btn = ttk.Button(frame, text=f"載入檔案 {i+1}", 
                           command=lambda idx=i: self.load_file(idx))
            btn.pack(side=tk.LEFT)
            
            self.figures.append(fig)
            self.canvases.append(canvas)
            self.spectra_data.append(None)
            
        self.left_frame.update_idletasks()
        self.left_canvas.configure(scrollregion=self.left_canvas.bbox("all"))
        
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
                    data['nm'].append(float(values[0]))
                    data['mw'].append(float(values[1]))
                    
                self.spectra_data[index] = data
                
                # 更新圖表
                ax = self.figures[index].get_axes()[0]
                ax.clear()
                ax.plot(data['nm'], data['mw'])
                ax.set_title(f"光譜圖 {index+1}", fontname='Microsoft JhengHei')
                ax.set_xlabel("nm", fontname='Microsoft JhengHei')
                ax.set_ylabel("mw", fontname='Microsoft JhengHei')
                self.canvases[index].draw()
                
                # 更新總和圖
                self.update_sum_plots()
                
        except Exception as e:
            messagebox.showerror("錯誤", f"讀取檔案失敗: {str(e)}")
            
    def update_sum_plots(self):
        if not all(self.spectra_data):
            return
            
        # 計算總和
        sum_mw = [0] * 301
        for data in self.spectra_data:
            if data:
                for i, val in enumerate(data['mw']):
                    sum_mw[i] += val
                    
        # 正規化
        max_val = max(sum_mw)
        norm_mw = [val/max_val for val in sum_mw] if max_val != 0 else [0]*301
        
        # 更新總和圖
        self.sum_ax.clear()
        self.sum_ax.plot(range(400,701), sum_mw)
        self.sum_ax.set_title("總和光譜圖", fontname='Microsoft JhengHei')
        self.sum_ax.set_xlabel("nm", fontname='Microsoft JhengHei')
        self.sum_ax.set_ylabel("mw", fontname='Microsoft JhengHei')
        self.sum_canvas.draw()
        
        # 更新正規化圖
        self.norm_ax.clear()
        self.norm_ax.plot(range(400,701), norm_mw)
        self.norm_ax.set_title("正規化光譜圖", fontname='Microsoft JhengHei')
        self.norm_ax.set_xlabel("nm", fontname='Microsoft JhengHei')
        self.norm_ax.set_ylabel("強度", fontname='Microsoft JhengHei')
        self.norm_canvas.draw()
        
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    if check_expiration():
        login = LoginWindow()
        login.root.mainloop()