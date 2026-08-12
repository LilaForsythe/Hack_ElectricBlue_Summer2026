import os
import math
import struct
from machine import I2S, Pin, ADC
from utime import sleep_ms
#mix of original code and ai (it started off original but modified multiple times with ai)

BUTTONC4_PIN = 3  # Pin GP3 (Physical Pin 5)
BUTTOND4_PIN = 4  # Pin GP4 (Physical Pin 6)
BUTTONE4_PIN = 5  # Pin GP5 (Physical Pin 7)
BUTTONF4_PIN = 6  # Pin GP6 (Physical Pin 9)
BUTTONG4_PIN = 7  # Pin GP7 (Physical Pin 10)
BUTTONA4_PIN = 8  # Pin GP8 (Physical Pin 11)
BUTTONB4_PIN = 9  # Pin GP9 (Physical Pin 12)
BUTTONC5_PIN = 10 # Pin GP10 (Physical Pin 14)
LED_PIN = 16      # GPIO 16 (Physical Pin 21)
POT_PIN = 27      # GPIO 27 / ADC1 (Physical Pin 32)

SCK_PIN = 0     # BCLK on GP0 (Physical Pin 1)
WS_PIN = 1      # LRC/WS on GP1 (Physical Pin 2)
SD_PIN = 2      # DIN on GP2 (Physical Pin 4)

SAMPLE_RATE = 22050  
BUFFER_SIZE = 2048   
MAX_AMPLITUDE = 28000 


buttonC4 = Pin(BUTTONC4_PIN, Pin.IN, Pin.PULL_UP)
buttonD4 = Pin(BUTTOND4_PIN, Pin.IN, Pin.PULL_UP)
buttonE4 = Pin(BUTTONE4_PIN, Pin.IN, Pin.PULL_UP)
buttonF4 = Pin(BUTTONF4_PIN, Pin.IN, Pin.PULL_UP)
buttonG4 = Pin(BUTTONG4_PIN, Pin.IN, Pin.PULL_UP)
buttonA4 = Pin(BUTTONA4_PIN, Pin.IN, Pin.PULL_UP)
buttonB4 = Pin(BUTTONB4_PIN, Pin.IN, Pin.PULL_UP)
buttonC5 = Pin(BUTTONC5_PIN, Pin.IN, Pin.PULL_UP)

led = Pin(LED_PIN, Pin.OUT)
led.off()  

pot = ADC(Pin(POT_PIN)) 

audio_out = I2S(
    0, 
    sck=Pin(SCK_PIN), 
    ws=Pin(WS_PIN), 
    sd=Pin(SD_PIN), 
    mode=I2S.TX, 
    bits=16, 
    format=I2S.MONO, 
    rate=SAMPLE_RATE, 
    ibuf=10240
)

notes = {
    "C4": 261.63, "D4": 293.66, "E4": 329.63, "F4": 349.23, 
    "G4": 392.00, "A4": 440.00, "B4": 493.88, "C5": 523.25
}

def get_volume():
    """Averaged read to smooth out ADC/contact noise, tuned for 1k pot curve."""
    num_samples = 12
    readings = []
    for _ in range(num_samples):
        readings.append(pot.read_u16())
        sleep_ms(1)
        
    readings.sort()
    trimmed = readings[2:-2]  # Drop 2 lowest + 2 highest as likely spikes
    raw_adc = sum(trimmed) / len(trimmed)

    min_floor = 25000 
    max_ceiling = 64000 
    
    if raw_adc <= min_floor:
        return 0 
    elif raw_adc >= max_ceiling:
        return MAX_AMPLITUDE
        
    scaled = (raw_adc - min_floor) / (max_ceiling - min_floor)
    return int(scaled * MAX_AMPLITUDE)

def play_i2s_tone(frequency, duration_ms, volume):
    if frequency == 0 or volume == 0:
        silence = bytearray(BUFFER_SIZE)
        chunks = int((duration_ms / 1000) * SAMPLE_RATE * 2 / BUFFER_SIZE)
        for _ in range(max(1, chunks)):
            audio_out.write(silence)
        return

    samples_per_cycle = SAMPLE_RATE / frequency
    cycle_buffer = bytearray()
    for i in range(int(samples_per_cycle)):
        val = int(volume * math.sin(2 * math.pi * i / samples_per_cycle))
        cycle_buffer += struct.pack('<h', val)
    
    bytes_needed = int((duration_ms / 1000) * SAMPLE_RATE * 2)
    bytes_written = 0
    
    while bytes_written < bytes_needed:
        audio_out.write(cycle_buffer)
        bytes_written += len(cycle_buffer)

print("System ready with averaged volume smoothing...")

while True:
    try:
        if not buttonC4.value():
            vol = get_volume()
            print("Playing note C4 at Volume: {}".format(vol))
            led.on()
            play_i2s_tone(notes["C4"], 1000, vol)  
            play_i2s_tone(0, 100, 0)     
            led.off()
            sleep_ms(300)

        elif not buttonD4.value():
            vol = get_volume()
            print("Playing note D4 at Volume: {}".format(vol))
            play_i2s_tone(notes["D4"], 1000, vol)  
            play_i2s_tone(0, 100, 0)     
            sleep_ms(300)

        elif not buttonE4.value():
            vol = get_volume()
            print("Playing note E4 at Volume: {}".format(vol))
            play_i2s_tone(notes["E4"], 1000, vol)  
            play_i2s_tone(0, 100, 0)     
            sleep_ms(300)

        elif not buttonF4.value():
            vol = get_volume()
            print("Playing note F4 at Volume: {}".format(vol))
            play_i2s_tone(notes["F4"], 1000, vol)  
            play_i2s_tone(0, 100, 0)     
            sleep_ms(300)
            
        elif not buttonG4.value():
            vol = get_volume()
            print("Playing note G4 at Volume: {}".format(vol))
            play_i2s_tone(notes["G4"], 1000, vol)  
            play_i2s_tone(0, 100, 0)     
            sleep_ms(300)

        elif not buttonA4.value():
            vol = get_volume()
            print("Playing note A4 at Volume: {}".format(vol))
            play_i2s_tone(notes["A4"], 1000, vol)  
            play_i2s_tone(0, 100, 0)     
            sleep_ms(300)

        elif not buttonB4.value():
            vol = get_volume()
            print("Playing note B4 at Volume: {}".format(vol))
            play_i2s_tone(notes["B4"], 1000, vol)  
            play_i2s_tone(0, 100, 0)     
            sleep_ms(300)

        elif not buttonC5.value():
            vol = get_volume()
            print("Playing note C5 at Volume: {}".format(vol))
            play_i2s_tone(notes["C5"], 1000, vol)  
            play_i2s_tone(0, 100, 0)     
            sleep_ms(300)
            
        sleep_ms(10)  
        
    except KeyboardInterrupt:
        print("\nExiting script...")
        break

audio_out.deinit()
led.off()
print("Finished.")