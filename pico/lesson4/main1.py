# from machine import Pin
# led = Pin("LED", Pin.OUT)
# led.value(0)

# import machine
# led = machine.Pin("LED", machine.Pin.OUT)
# led.value(1)

from machine import Pin
import time
led = Pin("LED", mode=Pin.OUT)
status = False
while True:
    led.on()
    if status == False:
        led.on()
        status = True
    else:
        led.off()
        status = False
    time.sleep(1)

    