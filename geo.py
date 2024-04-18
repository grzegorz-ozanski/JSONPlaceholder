"""
    Reverse geocode mapping module
"""
import json
import urllib.request

GEOAPIFY_URL: str = 'https://api.geoapify.com/v1/geocode/reverse?lat={lat}&lon={lon}&apiKey={api_key}'


def reverse_geocode(lat: str, lon: str, api_key: str) -> dict[str, str]:
    """
    Translates geo coords to location name and time zone
    :param lat: Latitude
    :param lon: Longitude
    :return: Location and timezone name dictionary
    """

    api_url = GEOAPIFY_URL.format(lat=lat, lon=lon, api_key=api_key)
    result = {'location': '', 'timezone': ''}
    try:
        with urllib.request.urlopen(api_url) as url:
            data = json.load(url)
            location = data['features'][0]['properties']
            # Not many of the people from the sample API are actually located in some meaningful place...
            try:
                result['location'] = location['formatted']
            except KeyError:
                # most are in the middle of the ocean or in Antarctic
                result['location'] = location['name']
            result['timezone'] = location['timezone']['name']
    except KeyError:
        pass
    return result
