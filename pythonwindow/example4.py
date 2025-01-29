import tkinter as tk
from tkinter import ttk, messagebox
import paho.mqtt.client as mqtt
from threading import Thread

class MQTTPairApp:
    def __init__(self, master):
        self.master = master
        master.title("Python-Windows MQTT 雙向通訊工具 - Steve's Controller")
        master.geometry("720x520")
        self.setup_styles()

        # MQTT 配置
        self.broker = "broker.MQTTGO.io"
        self.port = 1883
        self.client_id = "mqttgokenny50968758"
        self.username = "Steve"
        self.password = "1234567"
        self.client = None
        self.running = True

        # 通訊配對配置
        self.pairs = [
            {
                "send_topic": "kenny1119/dataint1119",
                "receive_topic": "updatekenny1119/dataint1119",
                "data_type": int,
                "label": "整數數據"
            },
            {
                "send_topic": "kenny1119/datafloat1119",
                "receive_topic": "updatekenny1119/datafloat1119",
                "data_type": float,
                "label": "浮點數數據"
            },
            {
                "send_topic": "kenny1119/datastring1119",
                "receive_topic": "updatekenny1119/datastring1119",
                "data_type": str,
                "label": "字串數據"
            }
        ]

        self.create_widgets()
        self.connect_mqtt()
        self.subscribe_all()

    def setup_styles(self):
        """自定義界面樣式"""
        style = ttk.Style()
        #style.theme_use('clam')
        style.theme_use('alt')
        #style.theme_use('default')
        #style.theme_use('classic')
        
        self.colors = {
            'primary': '#2c3e50',
            'secondary': '#3498db',
            'success': '#27ae60',
            'danger': '#e74c3c',
            'light': '#ecf0f1',
            'dark': '#2c3e50'
        }

        style.configure('TFrame', background=self.colors['light'])
        style.configure('Header.TLabel', 
                       font=('Helvetica', 14, 'bold'),
                       foreground=self.colors['primary'],
                       padding=5)
        style.configure('Primary.TButton',
                       font=('Helvetica', 10, 'bold'),
                       foreground='white',
                       background=self.colors['secondary'],
                       borderwidth=0,
                       padding=8)
        style.map('Primary.TButton',
                 background=[('active', self.colors['primary']), 
                            ('disabled', '#95a5a6')])
        style.configure('Status.TEntry',
                       foreground=self.colors['dark'],
                       font=('Consolas', 10),
                       padding=5)

    def connect_mqtt(self):
        """建立MQTT連線"""
        self.client = mqtt.Client(client_id=self.client_id)
        self.client.username_pw_set(self.username, self.password)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        
        try:
            self.client.connect(self.broker, self.port)
            Thread(target=self.mqtt_loop, daemon=True).start()
        except Exception as e:
            messagebox.showerror("連線錯誤", 
                f"無法連接 MQTT Broker:\n{str(e)}\n"
                f"請檢查以下參數：\n"
                f"Broker: {self.broker}:{self.port}\n"
                f"Client ID: {self.client_id}\n"
                f"Username: {self.username}")

    def mqtt_loop(self):
        """MQTT網路循環"""
        while self.running:
            self.client.loop(timeout=1.0)

    def on_connect(self, client, userdata, flags, rc):
        """連線回調函數"""
        if rc == 0:
            print("連線成功")
        else:
            print(f"連線失敗，代碼：{rc}")

    def on_message(self, client, userdata, msg):
        """訊息接收處理"""
        for idx, pair in enumerate(self.pairs):
            if msg.topic == pair["receive_topic"]:
                self.master.after(0, self.update_receive_display, idx, msg.payload.decode())
                self.update_status(f"收到來自 {msg.topic} 的更新", 'info')
                break

    def subscribe_all(self):
        """訂閱所有主題"""
        for pair in self.pairs:
            self.client.subscribe(pair["receive_topic"], qos=1)
            print(f"已訂閱: {pair['receive_topic']}")

    def create_widgets(self):
        """創建界面組件"""
        main_frame = ttk.Frame(self.master)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # 標題
        header = ttk.Label(main_frame, 
                          text="MQTT 雙向通訊控制面板",
                          style='Header.TLabel')
        header.pack(pady=(0, 15))

        # 數據通道面板
        self.entries = []
        self.receive_displays = []
        for idx, pair in enumerate(self.pairs):
            group = ttk.LabelFrame(main_frame,
                                  text=f" {pair['label']} ",
                                  style='TFrame')
            group.pack(fill=tk.X, pady=8, ipadx=10, ipady=5)

            # 輸入發送區域
            input_frame = ttk.Frame(group)
            input_frame.pack(fill=tk.X, pady=3)
            
            entry = ttk.Entry(input_frame, 
                             font=('Helvetica', 11),
                             style='Status.TEntry')
            entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
            self.entries.append(entry)
            
            btn = ttk.Button(input_frame,
                            text="發送 →",
                            style='Primary.TButton',
                            command=lambda i=idx: self.send_data(i))
            btn.pack(side=tk.RIGHT)

            # 接收顯示區域
            receive_frame = ttk.Frame(group)
            receive_frame.pack(fill=tk.X, pady=3)
            
            ttk.Label(receive_frame, 
                     text="接收狀態：",
                     font=('Helvetica', 9)).pack(side=tk.LEFT)
            
            receive_display = ttk.Entry(receive_frame,
                                       state='readonly',
                                       style='Status.TEntry')
            receive_display.pack(side=tk.RIGHT, fill=tk.X, expand=True)
            self.receive_displays.append(receive_display)

        # 狀態欄
        self.status_bar = ttk.Frame(main_frame, height=30)
        self.status_bar.pack(fill=tk.X, pady=(15, 0))
        self.status_label = ttk.Label(self.status_bar,
                                     text="READY",
                                     foreground=self.colors['success'],
                                     font=('Helvetica', 9))
        self.status_label.pack(side=tk.RIGHT)

    def update_status(self, message, status_type='info'):
        """更新狀態欄"""
        colors = {
            'info': self.colors['primary'],
            'success': self.colors['success'],
            'error': self.colors['danger']
        }
        self.status_label.config(
            text=message,
            foreground=colors.get(status_type, self.colors['primary'])
        )

    def send_data(self, index):
        """發送數據方法"""
        data = self.entries[index].get()
        pair = self.pairs[index]
        
        try:
            # 數據類型驗證
            if pair["data_type"] != str:
                converted_data = pair["data_type"](data)
            elif not data:
                raise ValueError("字串不能為空")
            else:
                converted_data = data
                
            self.client.publish(pair["send_topic"], str(converted_data), qos=1)
            self.update_status(f"成功發送到 {pair['send_topic']}", 'success')
            print(f"已發送至 {pair['send_topic']}: {converted_data}")
        except ValueError as e:
            messagebox.showerror("格式錯誤", f"無效的 {pair['label']} 格式\n錯誤訊息: {e}")
            self.update_status(f"輸入格式錯誤: {str(e)}", 'error')
        except Exception as e:
            messagebox.showerror("發送錯誤", f"訊息發送失敗: {e}")
            self.update_status(f"發送失敗: {str(e)}", 'error')

    def update_receive_display(self, index, message):
        """更新接收顯示框"""
        display = self.receive_displays[index]
        display.config(state='normal')
        display.delete(0, tk.END)
        display.insert(0, message)
        display.config(state='readonly')

    def on_closing(self):
        """關閉視窗處理"""
        self.running = False
        if self.client:
            self.client.disconnect()
        self.master.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = MQTTPairApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()