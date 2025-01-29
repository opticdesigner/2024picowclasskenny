import tkinter as tk
from tkinter import ttk
import paho.mqtt.client as mqtt

class MQTTButtonApp:
    def __init__(self, master):
        self.master = master
        master.title("MQTT 按鈕發送器")

        # MQTT 客戶端初始化
        self.client = mqtt.Client()
        self.broker = "test.mosquitto.org"  # 使用公共測試伺服器
        self.port = 1883
        self.topic = "your/topic/here"  # 請修改為自己的主題

        # 連接 MQTT Broker
        self.connect_mqtt()

        # 創建界面元件
        self.create_widgets()

    def connect_mqtt(self):
        try:
            self.client.connect(self.broker, self.port)
            self.client.loop_start()
        except Exception as e:
            print(f"連接 MQTT Broker 失敗: {e}")

    def create_widgets(self):
        # 創建三個輸入框和按鈕組合
        for i in range(1, 4):
            frame = ttk.Frame(self.master)
            frame.pack(padx=10, pady=5, fill=tk.X)

            entry = ttk.Entry(frame)
            entry.pack(side=tk.LEFT, expand=True, fill=tk.X)

            btn = ttk.Button(
                frame,
                text=f"按鈕 {i} 發送",
                command=lambda e=entry: self.send_message(e.get())
            )
            btn.pack(side=tk.RIGHT, padx=(5, 0))

    def send_message(self, payload):
        if payload.strip():
            try:
                self.client.publish(self.topic, payload)
                print(f"已發送: {payload}")
            except Exception as e:
                print(f"發送失敗: {e}")
        else:
            print("輸入內容不能為空")

    def on_closing(self):
        self.client.disconnect()
        self.master.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = MQTTButtonApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()