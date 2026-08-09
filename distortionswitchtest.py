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

# Effect Switches
DISTORTION_PIN = 17 # Pin GP17 (Physical Pin 22) 
VIBRATO_PIN = 18    # Pin GP18 (Physical Pin 24)

LED_PIN = 16      # GPIO 16 (Physical Pin 21)
POT_PIN = 27      # GPIO 27 / ADC1 (Physical Pin 32)

SCK_PIN = 0     # BCLK on GP0 (Physical Pin 1)
WS_PIN = 1      # LRC/WS on GP1 (Physical Pin 2)
SD_PIN = 2      # DIN on GP2 (Physical Pin 4)

SAMPLE_RATE = 22050  
BUFFER_SIZE = 2048   
MAX_AMPLITUDE = 28000 

# --- Hardware Initialization ---
buttonC4 = Pin(BUTTONC4_PIN, Pin.IN, Pin.PULL_UP)
buttonD4 = Pin(BUTTOND4_PIN, Pin.IN, Pin.PULL_UP)
buttonE4 = Pin(BUTTONE4_PIN, Pin.IN, Pin.PULL_UP)
buttonF4 = Pin(BUTTONF4_PIN, Pin.IN, Pin.PULL_UP)
buttonG4 = Pin(BUTTONG4_PIN, Pin.IN, Pin.PULL_UP)
buttonA4 = Pin(BUTTONA4_PIN, Pin.IN, Pin.PULL_UP)
buttonB4 = Pin(BUTTONB4_PIN, Pin.IN, Pin.PULL_UP)
buttonC5 = Pin(BUTTONC5_PIN, Pin.IN, Pin.PULL_UP)

switch_distortion = Pin(DISTORTION_PIN, Pin.IN, Pin.PULL_UP)
switch_vibrato = Pin(VIBRATO_PIN, Pin.IN, Pin.PULL_UP)

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
    trimmed = readings[2:-2]  
    raw_adc = sum(trimmed) / len(trimmed)

    min_floor = 25000 
    max_ceiling = 64000 
    
    if raw_adc <= min_floor:
        return 0 
    elif raw_adc >= max_ceiling:
        return MAX_AMPLITUDE
        
    scaled = (raw_adc - min_floor) / (max_ceiling - min_floor)
    return int(scaled * MAX_AMPLITUDE)

def play_i2s_tone(frequency, duration_ms, volume, distort=False, vibrato=False):
    if frequency == 0 or volume == 0:
        silence = bytearray(BUFFER_SIZE)
        chunks = int((duration_ms / 1000) * SAMPLE_RATE * 2 / BUFFER_SIZE)
        for _ in range(max(1, chunks)):
            audio_out.write(silence)
        return

    clip_limit = MAX_AMPLITUDE * 0.8

    # --- FAST PATH: Used when vibrato is off to guarantee zero CPU lag/stutter ---
    if not vibrato:
        samples_per_cycle = int(SAMPLE_RATE / frequency)
        cycle_buffer = bytearray()
        
        for i in range(samples_per_cycle):
            val = volume * math.sin(2 * math.pi * i / samples_per_cycle)
            if distort:
                val *= 3.5
                if val > clip_limit: val = clip_limit
                elif val < -clip_limit: val = -clip_limit
            cycle_buffer += struct.pack('<h', int(val))
        
        bytes_needed = int((duration_ms / 1000) * SAMPLE_RATE * 2)
        bytes_written = 0
        while bytes_written < bytes_needed:
            audio_out.write(cycle_buffer)
            bytes_written += len(cycle_buffer)
            
    # --- VIBRATO PATH: Active pitch warbling ---
    else:
        total_samples = int((duration_ms / 1000) * SAMPLE_RATE)
        total_bytes = total_samples * 2
        bytes_written = 0
        
        phase = 0.0
        sample_index = 0 
        two_pi = 2 * math.pi
        phase_inc_base = two_pi / SAMPLE_RATE
        
        vibrato_rate = 5.0 
        vibrato_depth = frequency * 0.015 
        chunk_size = 512 

        while bytes_written < total_bytes:
            chunk = bytearray()
            samples_to_gen = min(chunk_size, total_samples - (bytes_written // 2))
            
            for _ in range(samples_to_gen):
                lfo = math.sin(two_pi * vibrato_rate * (sample_index / SAMPLE_RATE))
                current_freq = frequency + (vibrato_depth * lfo)
                    
                phase += current_freq * phase_inc_base
                if phase > two_pi:
                    phase -= two_pi
                    
                val = volume * math.sin(phase)
                
                if distort:
                    val *= 3.5
                    if val > clip_limit: val = clip_limit
                    elif val < -clip_limit: val = -clip_limit
                    
                chunk += struct.pack('<h', int(val))
                sample_index += 1
                
            audio_out.write(chunk)
            bytes_written += len(chunk)

print("System ready. \nDistortion Switch: Physical Pin 22\nVibrato Switch: Physical Pin 24")

while True:
    try:
        is_distorted = not switch_distortion.value()
        is_vibrato = not switch_vibrato.value()

        active_note = None
        if not buttonC4.value(): active_note = "C4"
        elif not buttonD4.value(): active_note = "D4"
        elif not buttonE4.value(): active_note = "E4"
        elif not buttonF4.value(): active_note = "F4"
        elif not buttonG4.value(): active_note = "G4"
        elif not buttonA4.value(): active_note = "A4"
        elif not buttonB4.value(): active_note = "B4"
        elif not buttonC5.value(): active_note = "C5"

        if active_note:
            vol = get_volume()
            d_text = "ON" if is_distorted else "OFF"
            v_text = "ON" if is_vibrato else "OFF"
            print(f"Playing {active_note} | Vol: {vol} | Dist: {d_text} | Vib: {v_text}")
            
            led.on()
            play_i2s_tone(notes[active_note], 1000, vol, distort=is_distorted, vibrato=is_vibrato)  
            
            play_i2s_tone(0, 100, 0)     
            led.off()
            sleep_ms(300)
            
        sleep_ms(10)  
        
    except KeyboardInterrupt:
        print("\nExiting script...")
        break

audio_out.deinit()
led.off()
print("Finished.")