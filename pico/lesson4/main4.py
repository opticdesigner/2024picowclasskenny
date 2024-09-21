from machine import Pin
import time
red_led = Pin(15,Pin.OUT)
button = Pin(14,Pin.IN,Pin.PULL_DOWN)

while True:
    if button.value(): #0:False ,有值:True
        red_led.toggle()
        time.sleep(0.5)