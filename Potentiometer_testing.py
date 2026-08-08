from machine import Pin, ADC, PWM
import time

adc = ADC(Pin(27))  # GP27 (Physical Pin 31) for analog input

led = PWM(Pin(28))  # Onboard LED on GP28 (Physical Pin 34)

led.freq(1000)  # Set the LED frequency to 1 kHz

while True:
        value = adc.read_u16()
        print(value)
        duty_cycle = int((value / 65535) * 10000)  # Scale to 16-bit range
        led.duty_u16(duty_cycle)  # Set the LED brightness based on potentiometer
        time.sleep(0.5)  # Small delay to avoid rapid flickering