import time
import machine

trig_pin = machine.Pin(15, machine.Pin.OUT)
echo_pin = machine.Pin(14, machine.Pin.IN)

SOUND_SPEED = 340
TRIG_PULSE_DURATION_US = 10

def measure_distance():
    trig_pin.value(0)
    time.sleep_us(2)
    trig_pin.value(1)
    time.sleep_us(TRIG_PULSE_DURATION_US)
    trig_pin.value(0)

    ultrason_duration = pulse_in(echo_pin, 1)
    distance_cm = ultrason_duration * SOUND_SPEED / 2 * 0.0001

    return distance_cm

def pulse_in(pin, level, timeout=1000000):
    t0 = time.ticks_us()
    while pin.value() != level:
        if time.ticks_diff(time.ticks_us(), t0) > timeout:
            return 0
    pulse_start = time.ticks_us()
    while pin.value() == level:
        if time.ticks_diff(time.ticks_us(), t0) > timeout:
            return 0
    pulse_end = time.ticks_us()
    return time.ticks_diff(pulse_end, pulse_start)

# Setup
trig_pin.init(machine.Pin.OUT)
echo_pin.init(machine.Pin.IN)

# Main loop
try:
    while True:
        distance_cm = measure_distance()
        print("Distance (cm): {:.2f}".format(distance_cm))

        # Check if the distance is 5cm or less
        if distance_cm <= 5:
            print("Object detected at 5cm or less! Stopping the script.")
            break  # Exit the loop

        time.sleep(0.25)

except KeyboardInterrupt:
    pass