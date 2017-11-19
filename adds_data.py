"""Get data from the NOAA Aviation Weather Center ADDS system

See https://aviationweather.gov/adds/dataserver
"""

import urllib2
import xml.etree.cElementTree as et
from metar_taf import Metar
from datetime import datetime, timedelta

SINGLE_ID_URL = "https://aviationweather.gov/adds/dataserver_current/httpparam?dataSource=metars&requestType=retrieve&format=xml&hoursBeforeNow=3&mostRecentForEachStation=true&stationString=%s"
MULTI_ID_URL = "https://aviationweather.gov/adds/dataserver_current/httpparam?dataSource=metars&requestType=retrieve&format=xml&hoursBeforeNow=3&mostRecentForEachStation=true&stationString=~%s"


def get_float(weather_field, tree, tag):
    entity = tree.find(tag)
    if entity is None:
        weather_field.valid = False
        return
    if len(entity.text) == 0:
        weather_field.error = True
        return
    try:
        t = float(entity.text)
    except ValueError:
        weather_field.error = True
        return
    weather_field.data = t


def get_string(weather_field, tree, tag):
    entity = tree.find(tag)
    if entity is None:
        weather_field.valid = False
        return
    if len(entity.text) == 0:
        weather_field.error = True
        return
    weather_field.data = entity.text


def parse_metar(xml_data):
    metar = Metar()

    get_string(metar.identifier, xml_data, 'station_id')
    get_float(metar.temperature, xml_data, 'temp_c')
    get_float(metar.dewpoint, xml_data, 'dewpoint_c')
    get_string(metar.wind_direction, xml_data, 'wind_dir_degrees')
    get_float(metar.wind_speed, xml_data, 'wind_speed_kt')
    get_float(metar.gust_speed, xml_data, 'wind_gust_kt')
    get_float(metar.visibility_sm, xml_data, 'visibility_statute_mi')
    get_float(metar.pressure_hg, xml_data, 'altim_in_hg')
    get_string(metar.noaa_flight_category, xml_data, 'flight_category')
    get_string(metar.raw, xml_data, 'raw_text')
    get_float(metar.ceiling, xml_data, 'cloud_base_ft_agl')
    get_float(metar.snow_depth, xml_data, 'snow_in')
    # todo: parse extra wx (eg RA, DZ, FZFG)
    # todo parse metar time

    print "Parsed METAR for %s" % metar.identifier.data

    return metar


def get_metar(identifier):
    """ Go to the internet and get a single airport metar

    :param identifier: the airport identifier
    :return: the metar for the airport
    """
    response = urllib2.urlopen(SINGLE_ID_URL % identifier)
    xml_tree = et.parse(response)
    root = xml_tree.getroot()
    metars = root.find("data").findall("METAR")
    return parse_metar(metars[0])


def get_metar_country(country_code):
    response = urllib2.urlopen(MULTI_ID_URL % country_code)
    xml_tree = et.parse(response)
    root = xml_tree.getroot()
    metars = root.find("data").findall("METAR")
    return map(parse_metar, metars)


def get_metar_list(identifiers):
    """Get a list of metars.

    Note, ordering will not be maintained. May not return a metar for each requested ID
    """
    if len(identifiers) == 0:
        return []
    id_list = ','.join(identifiers)
    response = urllib2.urlopen(SINGLE_ID_URL % id_list)
    xml_tree = et.parse(response)
    root = xml_tree.getroot()
    metars = root.find("data").findall("METAR")
    return map(parse_metar, metars)


class MetarCache(object):
    """
    A simple cache which avoids the need to reload metars too frequently.

    Timeouts are all in minutes.

    Entries can be present or missing.

    Missing entries use the missing_timeout.

    Present entries use the min_replacement and refresh timeouts.
    min_replacement works from the publish time of the metar.
    We assume a new metar will not be published in less than the min_replacement time.
    Once the min_replacement time, the refresh timout is used
    """

    def __init__(self, missing_timeout=5, min_replacement=30, refresh=2):
        self._missing_timeout = timedelta(minutes=missing_timeout)
        self._min_replacement = timedelta(minutes=min_replacement)
        self._refresh = timedelta(minutes=refresh)
        self._missing_entries = {}  # a dictionary from airport IDs to last check times
        self._present_entries = {}  # a dictionary from airport IDs to pair of (last check time, Metar)

    def evict(self):
        """Evict everything which has exceeded its timeout"""
        now = datetime.now()

        del_list = []
        for airport_id, t in self._missing_entries.items():
            if t + self._missing_timeout < now:
                del_list.append(airport_id)
        for airport_id in del_list:
            del self._missing_entries[airport_id]

        del_list = []
        for airport_id, (t, metar) in self._present_entries.items():
            if not metar.report_time.valid:
                if t + self._refresh < now:
                    del_list.append(airport_id)
                continue
            if metar.report_time.data + self._min_replacement < now and t + self._refresh < now:
                del_list.append(airport_id)
        for airport_id in del_list:
            del self._present_entries[airport_id]

    def prepopulate_country(self, country):
        """Pre-populate the cache using a 2-letter country code, eg 'gb'"""
        metars = get_metar_country(country)
        for m in metars:
            self.add_metar(m)

    def add_metar(self, metar):
        """Add a metar to the cache"""
        airport_id = metar.identifier.data  # todo handle error
        if airport_id in self._missing_entries:
            del self._missing_entries[airport_id]
        self._present_entries[airport_id] = (datetime.now(), metar)

    def get_metars(self, metar_list):
        """
        Get the metars for a list of airports

        :param metar_list: list of ICAO codes
        :return: a dictionary of ICAO code to metar. If no metar available None will be used instead of a metar.
        """
        self.evict()

        request_list = []
        for m in metar_list:
            if m not in self._missing_entries and m not in self._present_entries:
                request_list.append(m)

        if len(request_list) > 0:
            metars = get_metar_list(request_list)
            for m in metars:
                self.add_metar(m)
                del request_list[request_list.index(m.identifier.data)]
            for m in request_list:
                self._missing_entries[m] = datetime.now()

        ret = {}
        for m in metar_list:
            if m in self._present_entries:
                ret[m] = self._present_entries[m][1]
            else:
                ret[m] = None
        return ret


if __name__ == '__main__':
    cache = MetarCache()
    cache.prepopulate_country('gb')

    metars = cache.get_metars(['EGKB', 'EGKA']).values()
    print len(metars)
    for metar in metars:
        if metar is None:
            continue
        print metar.identifier, ' : ', metar.noaa_flight_category, '\t: ', metar.snow_depth

    metars = cache.get_metars(['EGKB', 'EGKA']).values()
    print len(metars)
    for metar in metars:
        if metar is None:
            continue
        print metar.identifier, ' : ', metar.noaa_flight_category, '\t: ', metar.snow_depth

    metars = cache.get_metars(['EGKB', 'BIEG']).values()
    print len(metars)
    for metar in metars:
        if metar is None:
            continue
        print metar.identifier, ' : ', metar.noaa_flight_category, '\t: ', metar.snow_depth

    metars = cache.get_metars(['EDDS', 'ZZZA']).values()
    print len(metars)
    for metar in metars:
        if metar is None:
            print None
            continue
        print metar.identifier, ' : ', metar.noaa_flight_category, '\t: ', metar.snow_depth