"""
    People management
"""
import json
import urllib.request
from typing import Callable

import attridict
import xlsxwriter

from person import Person


def _get_from_url(url) -> list[dict[str, ...]]:
    """
    Gets JSON data from URL

    :param url: URL to get data from
    :return: JSON data
    """
    with urllib.request.urlopen(url) as json_data:
        return json.load(json_data, object_hook=attridict)


def from_url(url):
    """
    Convenient method to create and populate people object with data from URL in one step
    :param url: URL to get people data from
    :return: Populated people object
    """
    people = People()
    people.load_json(_get_from_url(url))
    return people


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
        with xlsxwriter.Workbook(filename) as workbook:
            data = self._filter(*filter_args)
            worksheet = workbook.add_worksheet()
            # Set initial column width
            column_width = {key: len(key) for key in data[0].keys()}
            # Write headers
            worksheet.write_row(0, 0, data[0].keys())
            # Write data
            for row, item in enumerate(data, start=1):
                for col, key in enumerate(item.keys()):
                    worksheet.write(row, col, item[key])
                    # Update column width if necessary
                    if (current_len := len(item[key])) > column_width[key]:
                        column_width[key] = current_len
            # Apply column width to worksheet
            for col, key in enumerate(column_width.keys()):
                worksheet.set_column(col, col, column_width[key])
