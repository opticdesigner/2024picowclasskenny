import tkinter as tk
from tkinter import ttk, messagebox
import paho.mqtt.client as mqtt
from threading import Thread

class MQTTPairApp:
    def __init__(self, master):
        self.master = master
        master.title("MQTT 雙向通訊工具")
        master.geometry("600x400")

        # MQTT 配置
        self.broker = "broker.MQTTGO.io"
        self.port = 1883
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

        # 初始化連線
        self.connect_mqtt()
        self.create_widgets()
        self.subscribe_all()

    def connect_mqtt(self):
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        
        try:
            self.client.connect(self.broker, self.port)
            Thread(target=self.mqtt_loop, daemon=True).start()
        except Exception as e:
            messagebox.showerror("連線錯誤", f"無法連接 MQTT Broker: {e}")

    def mqtt_loop(self):
        while self.running:
            self.client.loop(timeout=1.0)

    def on_connect(self, client, userdata, flags, rc):
        print("連線成功" if rc == 0 else f"連線失敗，代碼：{rc}")

    def on_message(self, client, userdata, msg):
        for idx, pair in enumerate(self.pairs):
            if msg.topic == pair["receive_topic"]:
                self.master.after(0, self.update_receive_display, idx, msg.payload.decode())
                break

    def subscribe_all(self):
        for pair in self.pairs:
            self.client.subscribe(pair["receive_topic"], qos=1)
            print(f"已訂閱: {pair['receive_topic']}")

    def create_widgets(self):
        main_frame = ttk.Frame(self.master)
        main_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.entries = []
        self.receive_displays = []

        for idx, pair in enumerate(self.pairs):
            group = ttk.LabelFrame(main_frame, text=pair["label"])
            group.pack(fill=tk.X, pady=5)

            # 發送區域
            send_frame = ttk.Frame(group)
            send_frame.pack(fill=tk.X, pady=2)
            
            entry = ttk.Entry(send_frame)
            entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
            self.entries.append(entry)
            
            btn = ttk.Button(
                send_frame,
                text="發送",
                command=lambda i=idx: self.send_data(i)
            )
            btn.pack(side=tk.RIGHT)

            # 接收區域
            receive_display = ttk.Entry(group, state='readonly')
            receive_display.pack(fill=tk.X, pady=2)
            self.receive_displays.append(receive_display)

    def send_data(self, index):
        data = self.entries[index].get()
        pair = self.pairs[index]
        
        try:
            # 數據類型驗證
            if pair["data_type"] != str:
                data = pair["data_type"](data)
            elif not data:
                raise ValueError("字串不能為空")
                
            self.client.publish(pair["send_topic"], str(data), qos=1)
            print(f"已發送至 {pair['send_topic']}: {data}")
        except ValueError as e:
            messagebox.showerror("格式錯誤", f"無效的 {pair['label']} 格式\n錯誤訊息: {e}")
        except Exception as e:
            messagebox.showerror("發送錯誤", f"訊息發送失敗: {e}")

    def update_receive_display(self, index, message):
        display = self.receive_displays[index]
        display.config(state='normal')
        display.delete(0, tk.END)
        display.insert(0, message)
        display.config(state='readonly')

    def on_closing(self):
        self.running = False
        if self.client:
            self.client.disconnect()
        self.master.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = MQTTPairApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()