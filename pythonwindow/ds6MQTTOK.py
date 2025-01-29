import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import paho.mqtt.client as mqtt
import random
import json

class MQTTApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MQTT Client - Kenny1119")
        self.root.geometry("800x600")
        self.setup_ui()
        self.setup_mqtt()

    def setup_ui(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TFrame', background='#f0f0f0')
        style.configure('TLabel', background='#f0f0f0', font=('Arial', 10))
        style.configure('TButton', font=('Arial', 10), padding=5)
        style.configure('Header.TLabel', font=('Arial', 12, 'bold'))

        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 發送區
        send_frame = ttk.LabelFrame(main_frame, text="發送數據", padding=10)
        send_frame.pack(fill=tk.X, pady=5)

        self.inputs = {}
        topics = [
            ("整數", "kenny1119/dataint1119", int),
            ("浮點數", "kenny1119/datafloat1119", float),
            ("字串", "kenny1119/datastring1119", str)
        ]

        for i, (label_text, topic, dtype) in enumerate(topics):
            frame = ttk.Frame(send_frame)
            frame.pack(fill=tk.X, pady=2)
            
            lbl = ttk.Label(frame, text=label_text, width=8)
            lbl.pack(side=tk.LEFT)
            
            entry = ttk.Entry(frame)
            entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
            
            btn = ttk.Button(frame, text="發送", 
                           command=lambda t=topic, e=entry, d=dtype: self.send_data(t, e, d))
            btn.pack(side=tk.RIGHT)
            
            self.inputs[topic] = (entry, btn)

        # 接收區
        recv_frame = ttk.LabelFrame(main_frame, text="接收數據", padding=10)
        recv_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.text_boxes = {}
        sub_topics = [
            ("updatekenny1119/dataint1119", "整數更新"),
            ("updatekenny1119/datafloat1119", "浮點數更新"),
            ("updatekenny1119/datastring1119", "字串更新")
        ]

        for topic, title in sub_topics:
            frame = ttk.Frame(recv_frame)
            frame.pack(fill=tk.BOTH, expand=True, pady=2)
            
            lbl = ttk.Label(frame, text=title, style='Header.TLabel')
            lbl.pack(anchor=tk.W)
            
            text_box = scrolledtext.ScrolledText(frame, height=4, wrap=tk.WORD)
            text_box.pack(fill=tk.BOTH, expand=True)
            self.text_boxes[topic] = text_box

    def setup_mqtt(self):
        client_id = f"mqttgokenny50968758-{random.randint(1000,9999)}"
        self.client = mqtt.Client(client_id=client_id)
        self.client.username_pw_set("Steve", "1234567")
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        
        try:
            self.client.connect("broker.MQTTGO.io", 1883, 60)
            self.client.loop_start()
        except Exception as e:
            messagebox.showerror("連接錯誤", f"無法連接MQTT Broker: {str(e)}")

    def on_connect(self, client, userdata, flags, rc):
        topics = [("updatekenny1119/dataint1119", 0),
                 ("updatekenny1119/datafloat1119", 0),
                 ("updatekenny1119/datastring1119", 0)]
        client.subscribe(topics)

    def on_message(self, client, userdata, msg):
        payload = msg.payload.decode()
        text_box = self.text_boxes.get(msg.topic)
        if text_box:
            text_box.config(state=tk.NORMAL)
            text_box.insert(tk.END, f"{payload}\n")
            text_box.see(tk.END)
            text_box.config(state=tk.DISABLED)

    def send_data(self, topic, entry, dtype):
        try:
            data = dtype(entry.get())
            payload = json.dumps({"value": data})
            self.client.publish(topic, payload)
            entry.delete(0, tk.END)
        except ValueError:
            messagebox.showerror("輸入錯誤", f"請輸入有效的{dtype.__name__}類型數據")
        except Exception as e:
            messagebox.showerror("發送錯誤", f"數據發送失敗: {str(e)}")

    def on_closing(self):
        self.client.disconnect()
        self.client.loop_stop()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = MQTTApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()