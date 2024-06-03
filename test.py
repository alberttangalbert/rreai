import requests
from requests_ip_rotator import ApiGateway
import os

keywords = ['test']


def parse(keyword, session):
    url = f"https://www.google.com/search?q={keyword}"
    response = session.get(url)
    print(response)


if __name__ == '__main__':
    AWS_ACCESS_KEY_ID = ''
    AWS_SECRET_ACCESS_KEY = ''

    gateway = ApiGateway("https://www.google.com", access_key_id=AWS_ACCESS_KEY_ID,
                         access_key_secret=AWS_SECRET_ACCESS_KEY)
    gateway.start()

    session = requests.Session()
    session.mount("https://www.google.com", gateway)

    for keyword in keywords:
        parse(keyword, session)
    gateway.shutdown()