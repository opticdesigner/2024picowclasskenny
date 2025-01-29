import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import matplotlib.pyplot as plt

class SpectrumApp:
    def __init__(self, master):
        self.master = master
        self.master.title("光譜分析程式")
        
        # 輸入數量的標籤和輸入框
        self.label = tk.Label(master, text="請輸入光譜檔案數量 (1-10):")
        self.label.pack()
        
        self.entry = tk.Entry(master)
        self.entry.pack()
        
        self.submit_button = tk.Button(master, text="提交", command=self.submit)
        self.submit_button.pack()
        
        # 顯示區域
        self.canvas_frame = tk.Frame(master)
        self.canvas_frame.pack()
        
        self.spectrum_canvases = []
        
        # 強度總和和正規化圖的畫布
        self.sum_canvas = None
        self.norm_canvas = None
        
        # 儲存強度數據
        self.intensity_data = []

    def submit(self):
        try:
            N = int(self.entry.get())
            if N < 1 or N > 10:
                raise ValueError("數量必須在1到10之間")
            
            # 清空之前的畫布和數據
            for canvas in self.spectrum_canvases:
                canvas.destroy()
            self.spectrum_canvases.clear()
            self.intensity_data.clear()
            
            # 創建N個畫布
            for i in range(N):
                canvas = tk.Canvas(self.canvas_frame, width=400, height=300)
                canvas.pack(side=tk.LEFT)
                self.spectrum_canvases.append(canvas)
                
                load_button = tk.Button(self.canvas_frame, text=f"讀取檔案 {i+1}", command=lambda i=i: self.load_file(i))
                load_button.pack(side=tk.LEFT)

            # 總和圖和正規化圖的畫布
            self.sum_canvas = tk.Canvas(self.canvas_frame, width=400, height=300)
            self.sum_canvas.pack(side=tk.LEFT)
            
            self.norm_canvas = tk.Canvas(self.canvas_frame, width=400, height=300)
            self.norm_canvas.pack(side=tk.LEFT)

        except ValueError as e:
            messagebox.showerror("錯誤", str(e))

    def load_file(self, index):
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if file_path:
            try:
                data = pd.read_csv(file_path, delim_whitespace=True)
                
                if 'nm' not in data.columns or 'mw' not in data.columns:
                    raise ValueError("檔案中必須包含 'nm' 和 'mw' 兩個欄位")
                
                # 繪製光譜圖
                plt.figure(figsize=(5, 3))
                plt.plot(data['nm'], data['mw'])
                plt.title(f"光譜圖 {index + 1}")
                plt.xlabel("nm")
                plt.ylabel("mw")
                plt.grid()
                
                # 儲存圖表並顯示在Tkinter畫布上
                spectrum_img_path = f'spectrum_{index}.png'
                plt.savefig(spectrum_img_path)
                plt.close()

                img = tk.PhotoImage(file=spectrum_img_path)
                canvas = self.spectrum_canvases[index]
                canvas.create_image(0, 0, anchor=tk.NW, image=img)
                canvas.image = img
                
                # 儲存強度數據以便後續計算總和和正規化
                self.intensity_data.append(data['mw'])
                
                # 更新總和和正規化圖
                self.update_sum_and_normalization()

            except Exception as e:
                messagebox.showerror("錯誤", str(e))

    def update_sum_and_normalization(self):
        if not self.intensity_data:
            return
        
        total_intensity = sum(self.intensity_data)

        # 繪製總和光譜圖
        plt.figure(figsize=(5, 3))
        nm_values = pd.Series(range(400, 701))  # nm 值從400到700
        plt.plot(nm_values, total_intensity)
        plt.title("總和光譜圖")
        plt.xlabel("nm")
        plt.ylabel("總強度")
        plt.grid()
        
        sum_img_path = 'sum_spectrum.png'
        plt.savefig(sum_img_path)
        plt.close()

        img_sum = tk.PhotoImage(file=sum_img_path)
        self.sum_canvas.create_image(0, 0, anchor=tk.NW, image=img_sum)
        self.sum_canvas.image = img_sum
        
        # 繪製正規化光譜圖
        normalized_intensity = total_intensity / max(total_intensity) if max(total_intensity) > 0 else total_intensity
        
        plt.figure(figsize=(5, 3))
        plt.plot(nm_values, normalized_intensity)
        plt.title("正規化光譜圖")
        plt.xlabel("nm")
        plt.ylabel("正規化強度")
        plt.grid()
        
        norm_img_path = 'norm_spectrum.png'
        plt.savefig(norm_img_path)
        plt.close()

        img_norm = tk.PhotoImage(file=norm_img_path)
        self.norm_canvas.create_image(0, 0, anchor=tk.NW, image=img_norm)
        self.norm_canvas.image = img_norm

if __name__ == "__main__":
    root = tk.Tk()
    app = SpectrumApp(root)
    root.mainloop()
