"""
    Person management
"""
import re
from typing import Callable

import attridict


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
