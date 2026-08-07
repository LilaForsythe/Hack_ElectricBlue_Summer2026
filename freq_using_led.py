from machine import Pin
from machine import PWM
import time

#output pin = 28
pin28 = Pin(28, Pin.OUT)

#sound = pwm for pin28
sound = PWM(pin28)

#volume corresponds to the duty cycle
volume = 50


#frequencies
notes = [262, 277, 294, 311, 330, 349, 370, 392]

#plays the given note
def play_note(freq):
    sound.duty_u16(int(volume * 65535 / 100))
    sound.freq(note)
    time.sleep(1)

#rests for 0.1 seconds
def rest():
    sound.duty_u16(0)
    time.sleep(0.1)

#cycles through the notes and plays them
for note in notes:
    print("Playing note: {} Hz".format(note))
    play_note(note)
    rest()
