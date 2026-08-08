# =================================================================
# WEBSITE INTEGRATION PATCH
# -----------------------------------------------------------------
# This is your freq_using_led.py with serial "DATA" lines added so
# the website (index.html) can read notes/volume/effects live over
# USB. Every line marked  # >>> WEBSITE  is new — merge these into
# your real file rather than replacing it wholesale, since your
# actual button/effect logic may have moved on since this copy.
#
# PROTOCOL (one line per event, printed over the same USB serial
# the REPL already uses — no extra wiring needed):
#
#   DATA,NOTE,<NAME>,ON,<VOL 0-100>     e.g. DATA,NOTE,C4,ON,73
#   DATA,NOTE,<NAME>,OFF                e.g. DATA,NOTE,C4,OFF
#   DATA,VOL,<VOL 0-100>                periodic volume-only update
#   DATA,FX,<NAME>,ON | OFF             e.g. DATA,FX,THUNDERCLAP,ON
#
# FX names must match the website exactly: THUNDERCLAP, RAINFALL,
# STATIC. You don't have effects implemented yet (this file only
# plays 8 plain tones) — the doc requires 3 distinct effects beyond
# pitch/volume, so that's still open. Wherever you add an effect
# trigger, print DATA,FX,<NAME>,ON when it engages and
# DATA,FX,<NAME>,OFF when it releases; the website already listens
# for those and will react instantly, no other changes needed.
# =================================================================

import os
import math
import struct
from machine import I2S, Pin, ADC
from utime import sleep_ms, ticks_ms, ticks_diff  # >>> WEBSITE: added ticks_ms/ticks_diff

# --- Configuration Constants ---
BUTTONC4_PIN = 3
BUTTOND4_PIN = 4
BUTTONE4_PIN = 5
BUTTONF4_PIN = 6
BUTTONG4_PIN = 7
BUTTONA4_PIN = 8
BUTTONB4_PIN = 9
BUTTONC5_PIN = 10

adc = ADC(Pin(27))

SCK_PIN = 0
WS_PIN = 1
SD_PIN = 2
volume = 8000
SAMPLE_RATE = 22050
BUFFER_SIZE = 2048

# --- Hardware Initialization ---
buttonC4 = Pin(BUTTONC4_PIN, Pin.IN, Pin.PULL_UP)
buttonD4 = Pin(BUTTOND4_PIN, Pin.IN, Pin.PULL_UP)
buttonE4 = Pin(BUTTONE4_PIN, Pin.IN, Pin.PULL_UP)
buttonF4 = Pin(BUTTONF4_PIN, Pin.IN, Pin.PULL_UP)
buttonG4 = Pin(BUTTONG4_PIN, Pin.IN, Pin.PULL_UP)
buttonA4 = Pin(BUTTONA4_PIN, Pin.IN, Pin.PULL_UP)
buttonB4 = Pin(BUTTONB4_PIN, Pin.IN, Pin.PULL_UP)
buttonC5 = Pin(BUTTONC5_PIN, Pin.IN, Pin.PULL_UP)

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

def read_adc_percentage():
    value = adc.read_u16()
    percentage = (value / 65535) * 100
    return percentage

notes = {"C4": 261.63, "D4": 293.66, "E4": 329.63, "F4": 349.23,
         "G4": 392.00, "A4": 440.00, "B4": 493.88, "C5": 523.25}

def play_i2s_tone(frequency, duration_ms, volume):
    if frequency == 0:
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

def play_note_with_data(name, freq, pct):
    """>>> WEBSITE: wraps play_i2s_tone with DATA,NOTE lines for the site."""
    print("DATA,NOTE,{},ON,{}".format(name, pct))          # >>> WEBSITE
    print("Playing note: {} Hz".format(freq))
    vol_scaled = int((pct / 100) * 15000)
    play_i2s_tone(freq, 1000, vol_scaled)
    play_i2s_tone(0, 100, 0)
    print("DATA,NOTE,{},OFF".format(name))                 # >>> WEBSITE

# --- Primary Application Loop ---
print("System ready. Press the button to play the 8 digital notes...")
last_vol_print = ticks_ms()                                 # >>> WEBSITE

while True:
    try:
        pct = int(read_adc_percentage())                    # >>> WEBSITE
        volume = int((pct / 100) * 15000)

        # >>> WEBSITE: periodic volume broadcast (throttled to ~6-7/sec)
        now = ticks_ms()
        if ticks_diff(now, last_vol_print) > 150:
            print("DATA,VOL,{}".format(pct))
            last_vol_print = now

        if not buttonC4.value():
            play_note_with_data("C4", notes["C4"], pct)
            sleep_ms(500)
        if not buttonD4.value():
            play_note_with_data("D4", notes["D4"], pct)
            sleep_ms(500)
        if not buttonE4.value():
            play_note_with_data("E4", notes["E4"], pct)
            sleep_ms(500)
        if not buttonF4.value():
            play_note_with_data("F4", notes["F4"], pct)
            sleep_ms(500)
        if not buttonG4.value():
            play_note_with_data("G4", notes["G4"], pct)
            sleep_ms(500)
        if not buttonA4.value():
            play_note_with_data("A4", notes["A4"], pct)
            sleep_ms(500)
        if not buttonB4.value():
            play_note_with_data("B4", notes["B4"], pct)
            sleep_ms(500)
        if not buttonC5.value():
            play_note_with_data("C5", notes["C5"], pct)
            sleep_ms(500)

        sleep_ms(10)

    except KeyboardInterrupt:
        print("\nExiting script...")
        break

audio_out.deinit()
print("Finished.")
