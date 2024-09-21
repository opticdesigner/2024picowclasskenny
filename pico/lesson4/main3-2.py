from machine import Timer,Pin

#tim = Timer(period=5000, mode=Timer.ONE_SHOT, callback=lambda t:print(1))
#tim.init(period=1000, mode=Timer.PERIODIC, callback=lambda t:print(2))
green_led = Pin("LED",Pin.OUT)

green_count = 0
def green_led_mycallback(t:Timer):
    global green_count #引用全域變數count
    green_count = green_count + 1 
#     print(f"目前mycallback被執行:{count}次")
    green_led.toggle()
    print(f"green led run:{green_count}次")
    if green_count >= 10:
        t.deinit()

green_led_timer = Timer(period=1000,mode=Timer.PERIODIC,callback=green_led_mycallback)

red_count = 0
def red_led_mycallback(t:Timer):
    global red_count #引用全域變數count
    red_count = red_count + 1 
#     print(f"目前mycallback被執行:{count}次")
#     green_led.toggle()
    print(f"red led run:{red_count}次")
    if red_count >= 10:
        t.deinit()
red_led_timer = Timer(period=2000,mode=Timer.PERIODIC,callback=red_led_mycallback)