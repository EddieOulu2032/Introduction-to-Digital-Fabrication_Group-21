# Import the libraries for the watering plant
import machine as mc
import time
import utime

# Limits for pumper and LED
DRY_LIMIT = 30
OK_LIMIT = 80
SOUND_SPEED = 0.0343
CONTAINER_HEIGHT = 20
REFILL_LIMIT = 0.75 * CONTAINER_HEIGHT

# Set up pins for sensors, LED and pump
sensor = mc.ADC(26)
led_pump_red = mc.Pin(2, mc.Pin.OUT)
led_pump_green = mc.Pin(3, mc.Pin.OUT)
led_container_red = mc.Pin(4, mc.Pin.OUT)
led_container_green = mc.Pin(5, mc.Pin.OUT)
trig = mc.Pin(11, mc.Pin.OUT)
echo = mc.Pin(12, mc.Pin.OUT)
pump = mc.Pin(10, mc.Pin.OUT)

# Functions
def calculate_water_in_container ():
    trig.low()
    utime.sleep_us(2)
    
    trig.high()
    utime.sleep_us(10)
    trig.low()
    
    while echo.value() == 0:
        pass
    t1 = utime.ticks_us()
    
    while echo.value() == 1:
        pass
    t2 = utime.ticks_us()
    
    echo_time = utime.ticks_diff(t2, t1)
    distant_to_water = echo_time * SOUND_SPEED / 2
    if distant_to_water <= REFILL_LIMIT:
        led_container_green.value(1)
        led_container_red.value(0)
        return True
    else:
        led_container_green.value(0)
        led_container_red.value(1)
        return False

def binary_conversion (percentage_value):
    binary_limit = 65535 * (1 - percentage_value / 100)
    return int(binary_limit)

def pumping_control ():
    current_soil = sensor.read_u16()
    dry_binary_limit = binary_conversion(DRY_LIMIT)
    ok_binary_limit = binary_conversion(OK_LIMIT)
    ok_water = calculate_water_in_container()
    if current_soil <= ok_binary_limit:
        pump.value(0)
        led_pump_green.value(0)
        led_pump_red.value(1)
    elif current_soil >= dry_binary_limit:
        if ok_water == True:
            pump_timing()
        else:
            pump.value(0)
            led_pump_red.value(1)
            led_pump_green.value(0)
            led_container_red.value(1)
            led_container_green.value(0)
            
    else:
        pump.value(0)
        led_pump_green.value(0)
        led_pump_red.value(1)

def pump_timing():
    led_pump_green.value(1)
    led_pump_red.value(0)
    pump.value(1)
    utime.sleep(20)
    pump.value(0)
    led_pump_red.value(1)
    led_pump_green.value(0)

while True:
    pumping_control()
    utime.sleep(2)
        


    
