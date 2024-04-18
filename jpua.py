"""
    Sample {JSON} Placeholder user API (https://jsonplaceholder.typicode.com/user) exerciser
"""
import argparse
import json
import re
import urllib.request
from typing import Callable

import attridict
import xlsxwriter

USER_API_URL: str = 'https://jsonplaceholder.typicode.com/users'

GEOAPIFY_URL: str = 'https://api.geoapify.com/v1/geocode/reverse?lat={lat}&lon={lon}&apiKey={api_key}'
GEOAPIFY_KEY: str = '4c0d2f6d926a4989b11ec3f03d98f641'


def _getitem(key_list: list[str], data):
    """
    Gets item recursively
    :param key_list: List of keys in subsequent recursive dictionaries
    :param data: Dictionary to search
    :return: Value of the key in the innermost dictionary
    """
    if len(key_list) == 1:
        return data[key_list[0]]
    return _getitem(key_list[1:], data[key_list[0]])


class Person:
    """
        Stores data of a single person acquired from {JSON} Placeholder user API
    """

    LATITUDE = 'address.geo.lat'
    LONGITUDE = 'address.geo.lng'

    def __init__(self, data: dict[str, ...]):
        self.data = attridict(data)  # pylint: disable=not-callable
        self.data.company.email = (f'{'.'.join([item.lower() for item in self.data.name.split()
                                                if not re.search(r'^mr.*\.$', item, re.IGNORECASE)])}@'
                                   f'{'-'.join([item.lower() for item in self.data.company.name.split()
                                                if item.lower() not in ['llc', 'and']])}.com')

    def __getitem__(self, key: str):
        return self.get(key)

    def keys(self) -> list[str]:
        """
        :return: Person object data keys
        """
        return self.data.keys()

    def get(self, key: str):
        """
        Get item value.

        :param key: Key
        :return: Value of a key
        """
        if '.' not in key:
            return self.data[key]
        return _getitem(key.split('.'), self.data)

    def acquire_location_name(self, location_func: Callable[[str, str], dict[str, str]]) -> None:
        """
        Sets location name using reverse geocode location function provided

        :param location_func: Reverse geocode location function
        """
        self.data.update(location_func(self._lat, self._lon))

    @property
    def _lat(self) -> str:
        """
        :return: Person's location latitude
        """
        return self.get(Person.LATITUDE)

    @property
    def _lon(self) -> str:
        """
        :return: Person's location longitude
        """
        return self.get(Person.LONGITUDE)

    def as_dict(self) -> dict[str, ...]:
        """
        :return: Dictionary representation of person's data
        """
        return self.data


class People:
    """
        Stores data of all people acquired from {JSON} Placeholder user API
    """
    def __init__(self):
        self.data = None

    def load_json(self, json_data: list[dict[str, ...]]) -> None:
        """
        Loads data from JSON

        :param json_data: Source JSON
        """
        self.data = [Person(item) for item in json_data]

    def update_location(self, reverse_geocode_func: Callable[[str, str], dict[str, str]]) -> None:
        """
        Sets location of each person using provided reverse geocode function

        :param reverse_geocode_func: Function converting geo coords to location name
        """
        _ = [person.acquire_location_name(reverse_geocode_func) for person in self.data]

    def _filter(self, *args: str) -> list[dict[str, ...]]:
        """
        Filters people data and returns them as a dictionary

        :param args: Filter columns names
        :return: Filtered people dictionaries list
        """
        if args:
            return [{key: person[key] for key in args} for person in self.data]
        return [item.as_dict() for item in self.data]

    def print(self, *filter_args: str) -> None:
        """
        Prints filtered people list

        :param filter_args: Filter columns names
        """
        print(json.dumps(self._filter(*filter_args), indent=4))

    def store_json(self, filename: str, *filter_args: str) -> None:
        """
        Stores filtered people list as JSON

        :param filename: JSON file name
        :param filter_args: Filter columns names
        """
        with open(filename, 'w', encoding='utf-8') as fp:
            json.dump(self._filter(*filter_args), fp, indent=4)

    def store_xls(self, filename: str, *filter_args: str) -> None:
        """
        Stores filtered people list as XLS

        :param filename: XLS file name
        :param filter_args: Filter columns names
        """
        with xlsxwriter.Workbook(filename) as wb:
            data = self._filter(*filter_args)
            ws = wb.add_worksheet()
            ws.write_row(0, 0, data[0].keys())
            for row, item in enumerate(data, start=1):
                for col, key in enumerate(item.keys()):
                    ws.write(row, col, item[key])


def reverse_geocode(lat: str, lon: str) -> dict[str, str]:
    """
    Translates geo coords to location name and time zone
    :param lat: Latitude
    :param lon: Longitude
    :return: Location and timezone name dictionary
    """

    api_url = GEOAPIFY_URL.format(lat=lat, lon=lon, api_key=GEOAPIFY_KEY)
    result = {'location': '', 'timezone': ''}
    return result
    try:
        with urllib.request.urlopen(api_url) as url:
            data = json.load(url)
            location = data['features'][0]['properties']
            try:
                result['location'] = location['formatted']
            except KeyError:
                result['location'] = location['name']
            result['timezone'] = location['timezone']['name']
    except KeyError:
        pass
    return result


def get_from_url(url) -> list[dict[str, ...]]:
    """
    Gets JSON data from URL

    :param url: URL to get data from
    :return: JSON data
    """
    with urllib.request.urlopen(url) as json_data:
        return json.load(json_data, object_hook=attridict)


def main() -> None:
    """
        Main entrypoint
    """
    parser = argparse.ArgumentParser(description='Sample {JSON} Placeholder user API exerciser')
    parser.add_argument('--geoapify-api-key', help='Geoapify API key', default=GEOAPIFY_KEY)
    parser.add_argument('--json', help='Output JSON file name')
    parser.add_argument('--xls', help='Output XLS file name')
    parser.add_argument('--data-filter', help='Data filters (comma-separated)')
    parser.add_argument('-s', '--silent', help='No verbose output', action='store_true', default=False)
    args = parser.parse_args()

    people = People()
    people.load_json(get_from_url(USER_API_URL))
    people.update_location(reverse_geocode)
    if args.data_filter:
        keys = tuple(args.data_filter.split(','))
    else:
        keys = ('name', 'username', 'location', 'timezone',
                'address.geo.lat', 'address.geo.lng', 'company.email')
    if not args.silent:
        people.print(*keys)
    if args.json:
        people.store_json(args.json)
    if args.xls:
        people.store_xls(args.xls, *keys)


if __name__ == '__main__':
    main()
