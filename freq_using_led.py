import os
import math
import struct
from machine import I2S, Pin, ADC
from utime import sleep_ms

# --- Configuration Constants ---
BUTTONC4_PIN = 3  # Pin GP3 (Physical Pin 5)
BUTTOND4_PIN = 4  # Pin GP4 (Physical Pin 6)
BUTTONE4_PIN = 5  # Pin GP5 (Physical Pin 7)
BUTTONF4_PIN = 6  # Pin GP6 (Physical Pin 9)
BUTTONG4_PIN = 7  # Pin GP7 (Physical Pin 10)
BUTTONA4_PIN = 8  # Pin GP8 (Physical Pin 11)
BUTTONB4_PIN = 9  # Pin GP9 (Physical Pin 12)
BUTTONC5_PIN = 10 # Pin GP10 (Physical Pin 14)

#potentiometer for volume control
adc = ADC(Pin(26))  # GP26 (Physical Pin 31) for analog input

SCK_PIN = 0     # BCLK on GP0 (Physical Pin 1)
WS_PIN = 1      # LRC/WS on GP1 (Physical Pin 2)
SD_PIN = 2      # DIN on GP2 (Physical Pin 4)

volume = 8000 #sample volume for now
SAMPLE_RATE = 22050  # Matches your amplifier's sample rate setup
BUFFER_SIZE = 2048   # Smaller, responsive buffer for real-time tones

# --- Hardware Initialization ---
buttonC4 = Pin(BUTTONC4_PIN, Pin.IN, Pin.PULL_UP)
buttonD4 = Pin(BUTTOND4_PIN, Pin.IN, Pin.PULL_UP)
buttonE4 = Pin(BUTTONE4_PIN, Pin.IN, Pin.PULL_UP)
buttonF4 = Pin(BUTTONF4_PIN, Pin.IN, Pin.PULL_UP)
buttonG4 = Pin(BUTTONG4_PIN, Pin.IN, Pin.PULL_UP)
buttonA4 = Pin(BUTTONA4_PIN, Pin.IN, Pin.PULL_UP)
buttonB4 = Pin(BUTTONB4_PIN, Pin.IN, Pin.PULL_UP)
buttonC5 = Pin(BUTTONC5_PIN, Pin.IN, Pin.PULL_UP)

# Keep the I2S system constantly alive and steady.
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


#controlling volume with potentiometer
def read_adc_percentage():
    value = adc.read_u16()
    percentage = (value / 65535) * 100
    return percentage

volume = int((read_adc_percentage() / 100) * 15000)  # Scale to 16-bit range


# --- Tone Scale Frequencies ---
notes = {"C4": 261.63, "D4": 293.66, "E4": 329.63, "F4": 349.23, "G4": 392.00, "A4": 440.00, "B4": 493.88, "C5": 523.25}
# notes = [261.63, 293.66, 329.63, 349.23, 392.00, 440.00, 493.88, 523.25]  # C4 to C5

# --- Digital Audio Generator ---

def play_i2s_tone(frequency, duration_ms, volume):
    """Generates a perfect digital sine wave tone and writes it to the I2S amp."""
    if frequency == 0:
        # Playing a rest / silence
        silence = bytearray(BUFFER_SIZE)
        chunks = int((duration_ms / 1000) * SAMPLE_RATE * 2 / BUFFER_SIZE)
        for _ in range(max(1, chunks)):
            audio_out.write(silence)
        return

    # Calculate how many samples we need for a single wave cycle
    samples_per_cycle = SAMPLE_RATE / frequency
    
    # Create one complete wave cycle buffer in 16-bit Mono format
    cycle_buffer = bytearray()
    for i in range(int(samples_per_cycle)):
        # Generate sine wave math value between -32767 and 32767 (max 16-bit volume)
        # Using 8000 here to keep the volume at a comfortable medium level
        val = int(volume * math.sin(2 * math.pi * i / samples_per_cycle))
        cycle_buffer += struct.pack('<h', val)
    
    # Repeat the cycle buffer until the desired duration is met
    bytes_needed = int((duration_ms / 1000) * SAMPLE_RATE * 2)
    bytes_written = 0
    
    while bytes_written < bytes_needed:
        # Write chunks to the I2S amplifier pipeline
        audio_out.write(cycle_buffer)
        bytes_written += len(cycle_buffer)

def play_digital_scale():
    """Cycles through the 8 notes digitally over I2S."""
    print("Playing digital tone scale via amplifier...")
    for note in notes:
        print("Playing note: {} Hz".format(note))
        play_i2s_tone(note, 1000, 8000)  # Play each note for 1000ms (1 second)
        play_i2s_tone(0, 100, 0)     # Rest for 100ms
    print("Scale finished.")

# --- Primary Application Loop ---
print("System ready. Press the button to play the 8 digital notes...")

while True:
    try:
        # Check if the button is physically pressed (LOW / 0 / False)
        if not buttonC4.value():
            print("Playing note: {} Hz".format(notes["C4"]))
            play_i2s_tone(notes["C4"], 1000, volume)  # Play each note for 1000ms (1 second)
            play_i2s_tone(0, 100, 0)     # Rest for 100ms
            #play_digital_scale()
            
            # Debounce delay: limits you to triggering once every 500ms
            sleep_ms(500)
            print("\nWaiting for next press...")

        if not buttonD4.value():
            print("Playing note: {} Hz".format(notes["D4"]))
            play_i2s_tone(notes["D4"], 1000, volume)  # Play each note for 1000ms (1 second)
            play_i2s_tone(0, 100, 0)     # Rest for 100ms
            
            # Debounce delay: limits you to triggering once every 500ms
            sleep_ms(500)
            print("\nWaiting for next press...")

        if not buttonE4.value():
            print("Playing note: {} Hz".format(notes["E4"]))
            play_i2s_tone(notes["E4"], 1000, volume)  # Play each note for 1000ms (1 second)
            play_i2s_tone(0, 100, 0)     # Rest for 100ms
            
            # Debounce delay: limits you to triggering once every 500ms
            sleep_ms(500)
            print("\nWaiting for next press...")

        if not buttonF4.value():
            print("Playing note: {} Hz".format(notes["F4"]))
            play_i2s_tone(notes["F4"], 1000, volume)  # Play each note for 1000ms (1 second)
            play_i2s_tone(0, 100, 0)     # Rest for 100ms
            
            # Debounce delay: limits you to triggering once every 500ms
            sleep_ms(500)
            print("\nWaiting for next press...")
            
        if not buttonG4.value():
            print("Playing note: {} Hz".format(notes["G4"]))
            play_i2s_tone(notes["G4"], 1000, volume)  # Play each note for 1000ms (1 second)
            play_i2s_tone(0, 100, 0)     # Rest for 100ms

            # Debounce delay: limits you to triggering once every 500ms
            sleep_ms(500)
            print("\nWaiting for next press...")

        if not buttonA4.value():
            print("Playing note: {} Hz".format(notes["A4"]))
            play_i2s_tone(notes["A4"], 1000, volume)  # Play each note for 1000ms (1 second)
            play_i2s_tone(0, 100, 0)     # Rest for 100ms

            # Debounce delay: limits you to triggering once every 500ms
            sleep_ms(500)
            print("\nWaiting for next press...")

        if not buttonB4.value():
            print("Playing note: {} Hz".format(notes["B4"]))
            play_i2s_tone(notes["B4"], 1000, volume)  # Play each note for 1000ms (1 second)
            play_i2s_tone(0, 100, 0)     # Rest for 100ms

            # Debounce delay: limits you to triggering once every 500ms
            sleep_ms(500)
            print("\nWaiting for next press...")

        if not buttonC5.value():
            print("Playing note: {} Hz".format(notes["C5"]))
            play_i2s_tone(notes["C5"], 1000, volume)  # Play each note for 1000ms (1 second)
            play_i2s_tone(0, 100, 0)     # Rest for 100ms

            # Debounce delay: limits you to triggering once every 500ms
            sleep_ms(500)
            print("\nWaiting for next press...")
            
        sleep_ms(10)  # Micro-sleep to keep processing loops cool
        
    except KeyboardInterrupt:
        print("\nExiting script...")
        break

# Only shut down when you completely terminate the program with Ctrl+C
audio_out.deinit()
print("Finished.")