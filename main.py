import urllib.request
import json

USER_API_URL: str = 'https://jsonplaceholder.typicode.com/users'


def main() -> None:
    with urllib.request.urlopen(USER_API_URL) as url:
        data = json.load(url)
        print(json.dumps(data, indent=4))


if __name__ == '__main__':
    main()
