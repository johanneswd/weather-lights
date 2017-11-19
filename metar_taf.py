"""Structures to describe Metars and TAFs
"""


class WeatherField(object):
    """Container for individual weather fields

    >>> f = WeatherField()
    >>> f.valid
    False
    >>> f.error
    False
    >>> f.data = 10
    >>> f.data
    10
    >>> f.valid
    True
    >>> f.error
    False
    >>> f.error = True
    >>> f.error
    True
    >>> f.valid
    False
    >>> f.data
    >>> f.error = False
    >>> f.data
    10
    """

    def __init__(self, init_error=False):
        self._data = None
        if type(init_error) == bool:
            self._error = init_error
        else:
            raise ValueError("init_error must be a boolean")

    @property
    def error(self):
        return self._error

    @error.setter
    def error(self, value):
        self._error = value

    @property
    def valid(self):
        return self._data is not None and not self._error

    @valid.setter
    def valid(self, value):
        if not value:
            # Clear the error flag and go back to the last known real data
            self.error = False
            self.data = None
            return
        else:
            raise ValueError("Cannot force back to valid without real data - use .data")

    @property
    def data(self):
        if self.valid:
            return self._data
        else:
            return None

    @data.setter
    def data(self, value):
        self.error = False
        self._data = value

    def map(self, fn):
        """Apply fn to the data and return a new weather field, maintaining error state

        fn should handle the case when data is None
        """
        if not self.error:
            return WeatherField(fn(self.data))
        else:
            return self

    def __str__(self):
        return str(self.data)



class DerivedWeatherField(object):
    def __init__(self, source, get_fn=None, set_fn=None):
        self._source = source
        self._get_fn = get_fn
        self._set_fn = set_fn

    @property
    def valid(self):
        return self._source.valid

    @valid.setter
    def valid(self, value):
        self._source.valid = value

    @property
    def error(self):
        return self._source.error

    @error.setter
    def error(self, value):
        self._source.error = value

    @property
    def data(self):
        if self._get_fn is None:
            raise AttributeError("Cannot read converted field")
        data = self._source.data
        if data is not None:
            return self._get_fn(data)
        else:
            return data

    @data.setter
    def data(self, value):
        if self._set_fn is None:
            raise AttributeError("Cannot write converted field")
        self._source.data = self._set_fn(value)


class ConversionWeatherField(DerivedWeatherField):
    # noinspection PyMissingConstructor
    def __init__(self, source, conversion_factor):
        def get_fn(x):
            return x * conversion_factor

        def set_fn(x):
            return x / conversion_factor

        super(ConversionWeatherField, self).__init__(source, get_fn, set_fn)


class WeatherState(object):
    """Describes a snapshot of weather state.

    Each of the fields can be in one of three states: "present with data", "no data" or "error".
    By default they are set to "no data"
    """

    def __init__(self):
        self.ceiling = WeatherField()
        self.visibility = WeatherField()
        self.visibility_sm = ConversionWeatherField(self.visibility, 0.000621371)  # vis in statute miles
        self.pressure = WeatherField()
        self.pressure_hg = ConversionWeatherField(self.pressure, 0.02953)
        self.wind_speed = WeatherField()
        self.wind_direction = WeatherField()
        self.gust_speed = WeatherField()
        self.gust_direction = WeatherField()
        self.temperature = WeatherField()
        self.dewpoint = WeatherField()
        self.snow_depth = WeatherField()

    def __str__(self):
        str = ""
        for k, v in self.__dict__.items():
            if isinstance(v, WeatherField):
                if v.error:
                    str += '%s:ERR ' % k
                elif v.valid:
                    str += "%s:%s " % (k, v.data)
        return str


class Metar(WeatherState):
    def __init__(self):
        super(Metar, self).__init__()
        self.identifier = WeatherField(True)
        self.report_time = WeatherField(True)
        self.noaa_flight_category = WeatherField()
        self.raw = WeatherField(True)


class Taf(object):
    pass
