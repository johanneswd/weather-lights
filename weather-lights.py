from time import sleep

try:
    import neopixel
except ImportError:
    print "Could not import neopixel, running in simulation mode"
    import neopixel_sim as neopixel



from adds_data import MetarCache

airports = ['EGKB', 'EGHI', 'EGGP', 'EGGD', 'BIEG', 'EDDS']

# LED strip configuration:
LED_COUNT      = len(airports)      # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (18 uses PWM!).
#LED_PIN        = 10      # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 5       # DMA channel to use for generating signal (try 5)
LED_BRIGHTNESS = 32     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53
LED_STRIP      = neopixel.ws.WS2811_STRIP_RGB   # Strip type and colour ordering


colours = {
    'LIFR'  : neopixel.Color(191, 44, 214),      # purple
    'IFR'   : neopixel.Color(226, 67, 27),       # red
    'MVFR'  : neopixel.Color(46, 56, 209),       # blue
    'VFR'   : neopixel.Color(41, 178, 45)        # green
}

BLANK = neopixel.Color(0,0,0)

def get_colour(airport_id, metars):
    metar = metars[airport_id]
    if metar is None:
        return BLANK
    if not metar.noaa_flight_category.valid:
        return BLANK
    condition = metar.noaa_flight_category.data
    print "%s is %s" % (airport_id, condition)
    if condition not in colours:
        return BLANK
    return colours[condition]

def set_colours(strip, cache, airport_list):
    metars = cache.get_metars(airport_list)
    for airport, n in zip(airport_list, range(0, len(airport_list))):
        colour = get_colour(airport, metars)
        strip.setPixelColor(n, colour)
    strip.show()


def main(poll_interval):
    strip = neopixel.Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL,
                              LED_STRIP)
    strip.begin()
    cache = MetarCache()
    while True:
        set_colours(strip, cache, airports)
        sleep(poll_interval)

if __name__=='__main__':
    main(5)
