"""Stub for the neopixel Adafruit library"""


class StripSim(object):
    def begin(self):
        pass

    def setPixelColor(self, n, colour):
        pass

    def show(self):
        pass

    WS2811_STRIP_RGB = None


ws = StripSim()

def Color(r, g, b):
    pass


def Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL,
                      LED_STRIP):
    return StripSim()
