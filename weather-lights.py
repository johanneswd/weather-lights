
from neopixel import *
from adds_data import get_metar

airports = ['EGKB', 'EGHI', 'EGGP', 'EGGD']

# LED strip configuration:
LED_COUNT      = len(airports)      # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (18 uses PWM!).
#LED_PIN        = 10      # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 5       # DMA channel to use for generating signal (try 5)
LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53
LED_STRIP      = ws.WS2811_STRIP_GRB   # Strip type and colour ordering


colours = {
    'LIFR'  : Color(191, 44, 214),      # purple
    'IFR'   : Color(226, 67, 27),       # red
    'MVFR'  : Color(46, 56, 209),       # blue
    'VFR'   : Color(41, 178, 45)        # green
}

BLANK = Color(0,0,0)

def get_colour(airport_id):
    metar = get_metar(airport_id)
    if not metar.noaa_flight_category.valid:
        return BLANK
    condition = metar.noaa_flight_category.data
    if condition not in colours:
        return BLANK
    return colours[condition]

def set_colours(strip, airport_list):
    for airport, n in zip(airport_list, range(0, len(airport_list))):
        colour = get_colour(airport)
        strip.setPixelColor(n, colour)
    strip.show()


if __name__=='__main__':
    strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL,
                              LED_STRIP)
    strip.begin()
    set_colours(strip, airports)
