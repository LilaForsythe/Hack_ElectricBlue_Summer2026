import os
from machine import I2S, Pin
from utime import sleep_ms

# --- Configuration Constants ---
BUTTON_PIN = 3  # Pin GP3 (Physical Pin 5)
LED_PIN = 16    # GPIO 16 (Physical Pin 21) - 100% Verified!

SCK_PIN = 0     # BCLK on GP0 (Physical Pin 1)
WS_PIN = 1      # LRC/WS on GP1 (Physical Pin 2)
SD_PIN = 2      # DIN on GP2 (Physical Pin 4)

WAV_FILE = "sound.wav"
BUFFER_SIZE = 10240  # 10KB static buffer allocation

# --- Hardware Initialization ---
button = Pin(BUTTON_PIN, Pin.IN, Pin.PULL_UP)
led = Pin(LED_PIN, Pin.OUT)  # Configure GPIO 16 as a digital output
led.off()                    # Ensure it starts turned off

# Keep the I2S system constantly alive and steady.
audio_out = I2S(
    0, 
    sck=Pin(SCK_PIN), 
    ws=Pin(WS_PIN), 
    sd=Pin(SD_PIN), 
    mode=I2S.TX, 
    bits=16, 
    format=I2S.MONO, 
    rate=22050, 
    ibuf=BUFFER_SIZE
)

def play_wav_file(filename):
    """Streams data across the static, permanent I2S channel."""
    if filename not in os.listdir():
        print(f"Error: '{filename}' not found on storage!")
        return
        
    try:
        with open(filename, "rb") as wav:
            # Safely skip the standard 44-byte WAV header metadata
            wav.seek(44)
            print(f"Playing: {filename}")
            
            # Read chunk by chunk into a static memory array
            audio_data = bytearray(BUFFER_SIZE)
            while True:
                bytes_read = wav.readinto(audio_data)
                
                # Exit cleanly if we reach the end of the sound file
                if bytes_read == 0:
                    break
                    
                # Write directly to our permanent open audio pipeline
                audio_out.write(audio_data[:bytes_read])
                
        print("Playback finished.")
        
    except Exception as e:
        print(f"Playback error: {e}")

# --- Primary Application Loop ---
print("System hard reset complete. Press the button...")

while True:
    try:
        # Check if the button is physically pressed (LOW / 0 / False)
        if not button.value():
            print("Button detected! Toggling LED on...")
            led.on()  # Turn the LED on
            
            play_wav_file(WAV_FILE)
            
            led.off()  # Turn the LED off when audio completes
            print("Playback done. LED off.")
            
            # Debounce delay: limits you to triggering once every 400ms
            sleep_ms(400)
            
        sleep_ms(10)  # Micro-sleep to keep processing loops cool
        
    except KeyboardInterrupt:
        print("\nExiting script...")
        break

# Only shut down when you completely terminate the program with Ctrl+C
audio_out.deinit()
led.off()  # Clean up and ensure LED is off on exit
print("Finished.")