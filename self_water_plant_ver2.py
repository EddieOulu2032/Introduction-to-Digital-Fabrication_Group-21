import machine as mc
import utime

# Constant values for container height 16 cm
DRY_LIMIT = 30          
OK_LIMIT = 80           
SOUND_SPEED = 0.0343    
CONTAINER_HEIGHT = 16   
REFILL_LIMIT = 15.0     

# Pin setup
sensor = mc.ADC(26)
led_pump_red = mc.Pin(2, mc.Pin.OUT)
led_pump_green = mc.Pin(3, mc.Pin.OUT)
led_container_red = mc.Pin(4, mc.Pin.OUT)
led_container_green = mc.Pin(5, mc.Pin.OUT)
trig = mc.Pin(11, mc.Pin.OUT)
echo = mc.Pin(12, mc.Pin.OUT)
pump = mc.Pin(10, mc.Pin.OUT)
pump.value(0)

def binary_conversion(percentage_value):
    """Convert the moisture percentage to ADC 16-bit values"""
    return int(65535 * (1 - percentage_value / 100))

def calculate_water_in_container():
    """Calculate the height of the water in the container, use the average of 5 times the measurements to reduce errors"""
    total_dist = 0
    samples = 5
    valid_samples = 0
    
    for _ in range(samples):
        trig.low()
        utime.sleep_us(2)
        trig.high()
        utime.sleep_us(10)
        trig.low()
        
        count = 0
        while echo.value() == 0 and count < 2000:
            count += 1
            utime.sleep_us(1)
            
        if count < 2000:
            t1 = utime.ticks_us()
            while echo.value() == 1: pass
            t2 = utime.ticks_us()
            
            dist = (utime.ticks_diff(t2, t1) * SOUND_SPEED) / 2
            total_dist += dist
            valid_samples += 1
        utime.sleep_ms(10) 

    if valid_samples > 0:
        avg_dist = total_dist / valid_samples
        print(f"Distance: {avg_dist:.2f} cm") 
        
        if avg_dist <= REFILL_LIMIT:
            led_container_green.value(1)
            led_container_red.value(0)
            return True
        else:
            led_container_green.value(0)
            led_container_red.value(1)
            return False
    return False

def pumping_control():
    """Control the pump using the moisture sensors and water inside the water tank"""
    current_soil = sensor.read_u16()
    dry_limit = binary_conversion(DRY_LIMIT)
    ok_limit = binary_conversion(OK_LIMIT)
    ok_water = calculate_water_in_container()

    if current_soil >= dry_limit and ok_water:
        pump.value(1)
        led_pump_green.value(1)
        led_pump_red.value(0)
        print(">>> STATUS: watering the plant")
    else:
        pump.value(0)
        led_pump_green.value(0)
        led_pump_red.value(1)
        if not ok_water:
            print("!!! WARNING: Container needs refilling!")
        else:
            print("--- STATUS: Plant conditions are ok!")


print("Self watering plant initializing")
utime.sleep(1)
while True:
    try:
        pumping_control()
        utime.sleep(0.5)
    except Exception as e:
        print("Errors, start initialize again!")
        utime.sleep(1)
