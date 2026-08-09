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
WAV_SWITCH_PIN = 17 # Pin GP17 (Physical Pin 22) - Switch for WAV file playback
VIBRATO_PIN = 18    # Pin GP18 (Physical Pin 24)
BITCRUSH_PIN = 19   # Pin GP19 (Physical Pin 25)

LED_PIN = 16      # GPIO 16 (Physical Pin 21)
POT_PIN = 27      # GPIO 27 / ADC1 (Physical Pin 32)

SCK_PIN = 0     # BCLK on GP0 (Physical Pin 1)
WS_PIN = 1      # LRC/WS on GP1 (Physical Pin 2)
SD_PIN = 2      # DIN on GP2 (Physical Pin 4)

WAV_FILE = "sound.wav"
SAMPLE_RATE = 22050  
BUFFER_SIZE = 10240   
MAX_AMPLITUDE = 28000 

print("[SYSTEM] Initializing Hardware...")

# --- Hardware Initialization ---
buttonC4 = Pin(BUTTONC4_PIN, Pin.IN, Pin.PULL_UP)
buttonD4 = Pin(BUTTOND4_PIN, Pin.IN, Pin.PULL_UP)
buttonE4 = Pin(BUTTONE4_PIN, Pin.IN, Pin.PULL_UP)
buttonF4 = Pin(BUTTONF4_PIN, Pin.IN, Pin.PULL_UP)
buttonG4 = Pin(BUTTONG4_PIN, Pin.IN, Pin.PULL_UP)
buttonA4 = Pin(BUTTONA4_PIN, Pin.IN, Pin.PULL_UP)
buttonB4 = Pin(BUTTONB4_PIN, Pin.IN, Pin.PULL_UP)
buttonC5 = Pin(BUTTONC5_PIN, Pin.IN, Pin.PULL_UP)

# Switch Initialization (Read 0 when flipped/connected to GND)
switch_wav = Pin(WAV_SWITCH_PIN, Pin.IN, Pin.PULL_UP)
switch_vibrato = Pin(VIBRATO_PIN, Pin.IN, Pin.PULL_UP)
switch_bitcrush = Pin(BITCRUSH_PIN, Pin.IN, Pin.PULL_UP)

led = Pin(LED_PIN, Pin.OUT)
led.off()  

pot = ADC(Pin(POT_PIN)) 

print("[SYSTEM] Starting I2S Audio Interface...")
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

def play_wav_file(filename):
    """Streams WAV data across the permanent I2S channel."""
    if filename not in os.listdir():
        print(f"[ERROR] '{filename}' not found on storage!")
        return
        
    try:
        with open(filename, "rb") as wav:
            wav.seek(44)
            print(f"[WAV] Playing file: {filename}")
            audio_data = bytearray(BUFFER_SIZE)
            while True:
                bytes_read = wav.readinto(audio_data)
                if bytes_read == 0:
                    break
                audio_out.write(audio_data[:bytes_read])
        print("[WAV] Playback finished.")
    except Exception as e:
        print(f"[ERROR] Playback error: {e}")

def play_i2s_tone(frequency, duration_ms, volume, vibrato=False, bitcrush=False):
    if frequency == 0 or volume == 0:
        silence = bytearray(BUFFER_SIZE)
        chunks = int((duration_ms / 1000) * SAMPLE_RATE * 2 / BUFFER_SIZE)
        for _ in range(max(1, chunks)):
            audio_out.write(silence)
        return

    # --- FAST PATH: Used when vibrato is off to guarantee zero CPU lag/stutter ---
    if not vibrato:
        samples_per_cycle = int(SAMPLE_RATE / frequency)
        cycle_buffer = bytearray()
        for i in range(samples_per_cycle):
            val = float(volume * math.sin(2 * math.pi * i / samples_per_cycle))
            
            # Apply Bitcrusher
            if bitcrush:
                steps = 8.0
                val = round(val / (MAX_AMPLITUDE / steps)) * (MAX_AMPLITUDE / steps)
                
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
                    
                val = float(volume * math.sin(phase))
                
                # Apply Bitcrusher
                if bitcrush:
                    steps = 8.0
                    val = round(val / (MAX_AMPLITUDE / steps)) * (MAX_AMPLITUDE / steps)
                    
                chunk += struct.pack('<h', int(val))
                sample_index += 1
                
            audio_out.write(chunk)
            bytes_written += len(chunk)


note_buttons = [
    (buttonC4, "C4", notes["C4"]),
    (buttonD4, "D4", notes["D4"]),
    (buttonE4, "E4", notes["E4"]),
    (buttonF4, "F4", notes["F4"]),
    (buttonG4, "G4", notes["G4"]),
    (buttonA4, "A4", notes["A4"]),
    (buttonB4, "B4", notes["B4"]),
    (buttonC5, "C5", notes["C5"]),
]

print("[SYSTEM] Ready! GP16 LED will only light up for C4.")

# Variables to track previous state so we only print when switches change
prev_wav_mode = None
prev_vibrato = None
prev_bitcrushed = None
wav_played_once = False

while True:
    try:
        # Read current switch states
        is_wav_mode = not switch_wav.value()
        is_vibrato = not switch_vibrato.value()
        is_bitcrushed = not switch_bitcrush.value()

        # Print if a switch state changed
        if is_wav_mode != prev_wav_mode:
            print(f"[SWITCH] WAV Mode changed to: {'ON' if is_wav_mode else 'OFF'}")
            prev_wav_mode = is_wav_mode
            
        if is_vibrato != prev_vibrato:
            print(f"[SWITCH] Vibrato changed to: {'ON' if is_vibrato else 'OFF'}")
            prev_vibrato = is_vibrato
            
        if is_bitcrushed != prev_bitcrushed:
            print(f"[SWITCH] Bitcrush Distortion changed to: {'ON' if is_bitcrushed else 'OFF'}")
            prev_bitcrushed = is_bitcrushed

        # Check for active button press
        active_btn = None
        for btn, name, freq in note_buttons:
            if not btn.value():
                active_btn = (btn, name, freq)
                break

        if active_btn:
            btn, name, freq = active_btn
            vol = get_volume()
            
            print(f"[ACTION] Note Played: {name} ({freq} Hz) | Volume level: {vol}")

            # LED Logic
            if name == "C4":
                print("   -> [LED] C4 is played, turning GP16 LED ON")
                led.on()
            else:
                led.off()

            # Playback Logic
            if is_wav_mode:
                if not wav_played_once:
                    print("   -> [WAV] Playing audio file...")
                    play_wav_file(WAV_FILE)
                    wav_played_once = True
            else:
                wav_played_once = False
                
                # Initial note attack
                print("   -> [SYNTH] Playing initial note attack (300ms)")
                play_i2s_tone(freq, 300, vol, vibrato=is_vibrato, bitcrush=is_bitcrushed)

                # Sustain loop
                if not btn.value():
                    print("   -> [SYNTH] Button held down - sustaining note...")
                while not btn.value():
                    vol = get_volume()
                    play_i2s_tone(freq, 100, vol, vibrato=is_vibrato, bitcrush=is_bitcrushed)

                # Note release
                print(f"[ACTION] Note {name} released.")
                play_i2s_tone(0, 10, 0, vibrato=is_vibrato, bitcrush=is_bitcrushed)

            # Cleanup after release
            if name == "C4":
                print("   -> [LED] Note released, turning GP16 LED OFF")
            led.off()
            
        else:
            wav_played_once = False
            sleep_ms(5)

    except KeyboardInterrupt:
        print("\n[SYSTEM] KeyboardInterrupt detected. Exiting script...")
        break

audio_out.deinit()
led.off()
print("[SYSTEM] Finished. Clean shutdown complete.")