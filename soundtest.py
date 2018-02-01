import time
import RPi.GPIO as GPIO
import MFRC522
import signal
from neopixel import *
import argparse
import signal
import sys
import alsaaudio, time, audioop, datetime

GPIO.setmode(GPIO.BOARD)

# LED strip configuration:
LED_COUNT      = 30      # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (18 uses PWM!).
#LED_PIN        = 10      # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 5       # DMA channel to use for generating signal (try 5)
LED_BRIGHTNESS= 100     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53
LED_STRIP      = ws.WS2811_STRIP_GRB   # Strip type and colour ordering
continue_reading = True



#Glowstick 
def signal_handler(signal, frame):
        colorWipe(strip, Color(0,0,0))
        sys.exit(0)

def opt_parse():
        parser = argparse.ArgumentParser()
        parser.add_argument('-c', action='store_true', help='clear the display on exit')
        args = parser.parse_args()
        if args.c:
                signal.signal(signal.SIGINT, signal_handler)

# Define functions which animate LEDs in various ways.
def colorWipe(strip, color, wait_ms=50):
    """Wipe color across display a pixel at a time."""
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
        strip.show()
        time.sleep(wait_ms/1000.0)

def theaterChase(strip, color, wait_ms=50, iterations=1):
    """Movie theater light style chaser animation."""
    for j in range(iterations):
        for q in range(3):
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i+q, color)
                strip.show()
                time.sleep(wait_ms/1000.0)
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i+q, 0)
        break
    
def wheel(pos):
    """Generate rainbow colors across 0-255 positions."""
    if pos < 85:
        return Color(pos * 3, 255 - pos * 3, 0)
    elif pos < 170:
        pos -= 85
        return Color(255 - pos * 3, 0, pos * 3)
    else:
        pos -= 170
        return Color(0, pos * 3, 255 - pos * 3)

def rainbow(strip, wait_ms=20, iterations=1):
    """Draw rainbow that fades across all pixels at once."""
    for j in range(256*iterations):
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, wheel((i+j) & 255))
            strip.show()
            time.sleep(wait_ms/1000.0)

def rainbowCycle(strip, wait_ms=20, iterations=5):
    """Draw rainbow that uniformly distributes itself across all pixels."""
    for j in range(256*iterations):
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, wheel((int(i * 256 / strip.numPixels()) + j) & 255))
            strip.show()
            time.sleep(wait_ms/1000.0)

def theaterChaseRainbow(strip, wait_ms=50):
    """Rainbow movie theater light style chaser animation."""
    for j in range(256):
        for q in range(3):
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i+q, wheel((i+j) % 255))
                strip.show()
                time.sleep(wait_ms/1000.0)
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i+q, 0)


#SoundMoniter

class SoundMonitor:

    # Light red LED when measured sound value exceeds the preset limit

    WARNING_THRESHOLD = 8001

    # Tolerance as a percentage (0.5 is 50%)

    # LCD output is changed when the measured value exceeds this tolerance

    TOLERANCE = 0.15

    # Minimum time in seconds between each LCD value change

    MAX_CHANGE_FREQ = 0.5   


# Alsaaudio instance

    inp = alsaaudio.PCM(alsaaudio.PCM_CAPTURE,alsaaudio.PCM_NORMAL, 'sysdefault:CARD=1')

# Get the current sound level

    def get_sound_level(self):

        # Read data from device

        l,data = self.inp.read()

        if not l:

            return 1

        if l:

            try:
                value =audioop.max(data,2)
           
                if  value < 1:

                    value = 1.0
                return value
        except audioop.error, e:
            if e.message !="not a whole number of frames":
                raise e

        # Return the maximum of the absolute value of all samples in a fragment.

        

     


    def run(self):

        print "Running the program - press Ctrl + C to exit."

        time.sleep(2)

        saved_value = 1

        last_changed = time.time()

        while True:

            value = self.get_sound_level()
            print "Level: %s;" % (value)
            
            
            LED_BRIGHTNESS= 100+int(value/20)

        

            if value >= 2000:
		        strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL, LED_STRIP)
		        strip.begin()
                        theaterChase(strip, Color(127, 127, 127))  # White theater chase
                        
                   # GPIO.output(self.RED_LED, red_state) # Light red LED?


                        saved_value = value

                        last_changed = time.time()

                        time.sleep(1)




# Capture SIGINT for cleanup when the script is aborted
def end_read(signal,frame):
    global continue_reading
    print "Ctrl+C captured, ending read."
    continue_reading = False
    GPIO.cleanup()

# Hook the SIGINT
signal.signal(signal.SIGINT, end_read)

# Create NeoPixel object with appropriate configuration.
# Intialize the library (must be called once before other functions).



try:


    while continue_reading:
        

        monitor = SoundMonitor().run()
except KeyboardInterrupt:
    GPIO.cleanup()

