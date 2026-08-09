from machine import ADC, Pin
from utime import sleep_ms

pot = ADC(Pin(27)) # GP27 / Physical Pin 32

print("Testing Potentiometer on GP27. Press Ctrl+C to stop.")

while True:
    try:
        raw_adc = pot.read_u16() # Raw value from 0 to 65535
        scaled_vol = int((raw_adc / 65535) * 28000)
        
        # Create a visual bar to easily see the changes
        bar_length = int((scaled_vol / 28000) * 40)
        bar = "#" * bar_length
        
        print("Raw: {:>5} | Vol: {:>5} | {}".format(raw_adc, scaled_vol, bar))
        sleep_ms(150)
        
    except KeyboardInterrupt:
        break