"""
    Sample {JSON} Placeholder user API (https://jsonplaceholder.typicode.com/user) exerciser
"""
import argparse
import os
from functools import partial

import people as people_manager
from geo import reverse_geocode

USER_API_URL: str = 'https://jsonplaceholder.typicode.com/users'
GEOAPIFY_KEY: str = '4c0d2f6d926a4989b11ec3f03d98f641'
DEFAULT_FILTERS = ('name', 'username', 'location', 'timezone',
                'address.geo.lat', 'address.geo.lng', 'company.email')

def main() -> None:
    """
        Main entrypoint
    """
    parser = argparse.ArgumentParser(description='Sample {JSON} Placeholder user API exerciser')
    parser.add_argument('--geoapify-api-key', help='Geoapify API key')
    parser.add_argument('--json', help='Output JSON file name', default='test.json')
    parser.add_argument('--xls', help='Output XLS file name', default='test.xls')
    parser.add_argument('--data-filter', help='Data filters (comma-separated)')
    parser.add_argument('-s', '--silent', help='No verbose output', action='store_true', default=False)
    args = parser.parse_args()

    geoapify_key = args.geoapify_api_key or os.getenv('GEOAPIFY_API_KEY') or GEOAPIFY_KEY
    keys = tuple(args.data_filter.split(',')) if args.data_filter else DEFAULT_FILTERS

    # Get data from user API URL
    people = people_manager.from_url(USER_API_URL)

    # Get location name and timezone using provided reverse geocode function
    people.update_location(partial(reverse_geocode, api_key=geoapify_key))
    if not args.silent:
        people.print(*keys)
    if args.json:
        people.store_json(args.json)
    if args.xls:
        people.store_xls(args.xls, *keys)


if __name__ == '__main__':
    main()
