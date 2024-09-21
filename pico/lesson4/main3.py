from machine import Timer,Pin

#tim = Timer(period=5000, mode=Timer.ONE_SHOT, callback=lambda t:print(1))
#tim.init(period=1000, mode=Timer.PERIODIC, callback=lambda t:print(2))
green_led = Pin("LED",Pin.OUT)

count = 0
def green_led_mycallback(t:Timer):
    global count #引用全域變數count
    count = count + 1 
    print(f"目前mycallback被執行:{count}次")
    green_led.toggle()
    if count >= 10:
        t.deinit()

green_led_timer = Timer(period=1000,mode=Timer.PERIODIC,callback=green_led_mycallback)
