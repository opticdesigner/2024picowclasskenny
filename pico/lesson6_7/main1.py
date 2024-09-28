import machine
import time

adc = machine.ADC(4)
conversion_factor = 3.3 / (65535)

while True:
    #temperature_value = adc.read_u16()
    reading = adc.read_u16() * conversion_factor
    temperature = 27 - (reading - 0.706)/0.001721
    #print(temperature_value)
    print(temperature)
    print(reading)
    time.sleep(1)
