"""Get data from the NOAA Aviation Weather Center ADDS system

See https://aviationweather.gov/adds/dataserver
"""

import urllib2
import xml.etree.cElementTree as ET
from metar_taf import Metar

SINGLE_ID_URL = "https://aviationweather.gov/adds/dataserver_current/httpparam?dataSource=metars&requestType=retrieve&format=xml&hoursBeforeNow=3&mostRecent=true&stationString=%s"
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


    return metar


def get_metar(identifier):
    """ Go to the internet and get a single airport metar

    :param identifier: the airport identifier
    :return: the metar for the airport

    """
    response = urllib2.urlopen(SINGLE_ID_URL % identifier)
    xml_tree = ET.parse(response)
    root = xml_tree.getroot()
    metars = root.find("data").findall("METAR")
    return parse_metar(metars[0])


def get_metar_country(country_code):
    response = urllib2.urlopen(MULTI_ID_URL % country_code)
    xml_tree = ET.parse(response)
    root = xml_tree.getroot()
    metars = root.find("data").findall("METAR")
    return map(parse_metar, metars)


if __name__ == '__main__':
    metars = get_metar_country('gb')
    print len(metars)
    for metar in metars:
            print metar.identifier, ' : ', metar.noaa_flight_category, '\t: ', metar.snow_depth
