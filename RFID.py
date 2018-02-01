
import time
import RPi.GPIO as GPIO
import MFRC522
import signal
from neopixel import *
import argparse
import signal
import sys

GPIO.setmode(GPIO.BOARD)



# LED strip configuration:
LED_COUNT      = 30      # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (18 uses PWM!).
#LED_PIN        = 10      # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 5       # DMA channel to use for generating signal (try 5)
LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53
LED_STRIP      = ws.WS2811_STRIP_GRB   # Strip type and colour ordering
continue_reading = True

key = [0xFC,0xFE,0xEC,0x3D,0xD3]

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

def theaterChase(strip, color, wait_ms=50, iterations=10):
    """Movie theater light style chaser animation."""
    for j in range(iterations):
        for q in range(3):
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i+q, color)
                strip.show()
                time.sleep(wait_ms/1000.0)
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i+q, 0)

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

def soundtest():
    soundvalue = raw_input("key in 1 2 3: ")

    if soundvalue == "1":
        Green_pwm.ChangeDutyCycle(100)
        Red_pwm.ChangeDutyCycle(100)
        Blue_pwm.ChangeDutyCycle(100)
        print ('Color wipe animations.')
        colorWipe(strip, Color(255, 0, 0))  # Red wipe
        colorWipe(strip, Color(0, 255, 0))  # Blue wipe
        colorWipe(strip, Color(0, 0, 255))  # Green wipe
        time.sleep(1)
    elif soundvalue== "2":
        Green_pwm.ChangeDutyCycle(60)
        Red_pwm.ChangeDutyCycle(60)
        Blue_pwm.ChangeDutyCycle(60)
        print ('Theater chase animations.')
        theaterChase(strip, Color(127, 127, 127))  # White theater chase
        theaterChase(strip, Color(127,   0,   0))  # Red theater chase
        theaterChase(strip, Color(  0,   0, 127))  # Blue theater chase
        time.sleep(1)
    elif soundvalue== "3":
        Green_pwm.ChangeDutyCycle(20)
        Red_pwm.ChangeDutyCycle(20)
        Blue_pwm.ChangeDutyCycle(20)
        print ('Rainbow animations.')
        rainbow(strip)
        rainbowCycle(strip)
        theaterChaseRainbow(strip)
        time.sleep(1)

# Capture SIGINT for cleanup when the script is aborted
def end_read(signal,frame):
    global continue_reading
    print "Ctrl+C captured, ending read."
    continue_reading = False
    GPIO.cleanup()

# Hook the SIGINT
signal.signal(signal.SIGINT, end_read)

# Create an object of the class MFRC522
MIFAREReader = MFRC522.MFRC522()

# Create NeoPixel object with appropriate configuration.
strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL, LED_STRIP)
# Intialize the library (must be called once before other functions).
strip.begin()


global_index = 0
try:

# This loop keeps checking for chips. If one is near it will get the UID and authenticate
    mode = ['wipe', 'theater', 'rainbow', 'rainbowCycle', 'theaterChaseRainbow'] 
    mode_index = 0
    wait_ms=50
    while continue_reading:
       
        # Scan for cards 
        status = 'jkasdklasd'
        if global_index % 15 == 0:
            (status,TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)
        
            print('checking', status)
            (status,uid) = MIFAREReader.MFRC522_Anticoll()

        if status == MIFAREReader.MI_OK and uid != key:
            mode_index += 1
            mode_index = mode_index % 4
        if mode_index == 0:
            i = global_index % strip.numPixels()
            color =Color(0, 0, 0)
            strip.setPixelColor(i, color)
            strip.show()
            time.sleep(wait_ms/1000)
        if mode_index == 1:
            i = global_index % strip.numPixels()
            color = Color(255, 0, 0)
            # color = Color(0, 255, 0)
            # color = Color(0, 0, 255)
            strip.setPixelColor(i, color)
            strip.show() 
            time.sleep(wait_ms/1000.0)
        elif mode_index == 2:
            i = global_index % strip.numPixels()
            # color = Color(255, 0, 0)
            color = Color(0, 255, 0)
            # color = Color(0, 0, 255)
            strip.setPixelColor(i, color)
            strip.show() 
            time.sleep(wait_ms/1000.0)
            # for q in range(3):
            #     for i in range(0, strip.numPixels(), 3):
            #         strip.setPixelColor(i+q, color)
            #             strip.show()
            #         time.sleep(wait_ms/1000.0)
            #     for i in range(0, strip.numPixels(), 3):
            #         strip.setPixelColor(i+q, 0)
        elif mode_index == 3:
            i = global_index % strip.numPixels()
            # color = Color(255, 0, 0)
            # color = Color(0, 255, 0)
            color = Color(0, 0, 255)
            strip.setPixelColor(i, color)
            strip.show() 
            time.sleep(wait_ms/1000.0)
        

        global_index += 1

        # # If a card is found
        # if status == MIFAREReader.MI_OK:
        #     print("Card detected",status)
        #     #print "Card read UID: "+str(uid[0])+","+str(uid[1])+","+str(uid[2])+","+str(uid[3])
            
        #     colorWipe(strip, Color(255, 0, 0))  # Red wipe
        #     colorWipe(strip, Color(0, 255, 0))  # Blue wipe
        #     colorWipe(strip, Color(0, 0, 255))  # Green wipe
        # if status == MIFAREReader.MI_OK:
        #         print("Card detected",status)
        #         print ('Theater chase animations.')
        #     theaterChase(strip, Color(127, 127, 127))  # White theater chase
        #     theaterChase(strip, Color(127,   0,   0))  # Red theater chase
        #     theaterChase(strip, Color(  0,   0, 127))  # Blue theater chase
        # if status == MIFAREReader.MI_OK:
        #     print("Card detected",status)
        #     print ('Rainbow animations.')
        #     rainbow(strip)
        #     rainbowCycle(strip)
        #     theaterChaseRainbow(strip)

        
except KeyboardInterrupt:
    pass
#finally:
#    end_read()
