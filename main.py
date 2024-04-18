import urllib.request
import json
from typing import Any, Self
import attridict

USER_API_URL: str = 'https://jsonplaceholder.typicode.com/users'

GEO_API_URL: str = 'https://api.geoapify.com/v1/geocode/reverse?lat={lat}&lon={lon}&apiKey={api_key}'
GEO_API_KEY: str = '4c0d2f6d926a4989b11ec3f03d98f641'


class Person:
    def __init__(self, data: dict[str, Any]):
        self.data = attridict(data)

    def __getitem__(self, key):
        return self.get(key)

    def update(self, data: dict[str, Any]) -> Self:
        self.data.update(data)
        return self

    def _getitem(self, key_list: list[str], data):
        if len(key_list) == 1:
            return data[key_list[0]]
        return self._getitem(key_list[1:], data[key_list[0]])

    def get(self, key: str):
        if '.' not in key:
            return self.data[key]
        return self._getitem(key.split('.'), self.data)


def reverse_geocode(lat: str, lon: str) -> dict[str, str]:

    api_url = GEO_API_URL.format(lat=lat, lon=lon, api_key=GEO_API_KEY)
    result = {'location': '', 'timezone': ''}
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


def print_data(data, *args) -> None:
    filtered = [{key: person[key] for key in args} for person in data]
    print(json.dumps(filtered, indent=4))


def geo_lat_lon(person) -> tuple[str, str]:
    return person.get('address.geo.lat'), person.get('address.geo.lng')
    # return person['address']['geo']['lat'], person['address']['geo']['lng']


def main() -> None:
    with urllib.request.urlopen(USER_API_URL) as url:
        data = json.load(url, object_hook=attridict)
        # data = [Person(data[6])]
        new_data = [person.update(reverse_geocode(*geo_lat_lon(person))) for person in [Person(item) for item in data]]
        print_data(new_data, 'name', 'username', 'location', 'timezone', 'address.geo.lat', 'address.geo.lng')


if __name__ == '__main__':
    main()
