from urllib.parse import urljoin

import requests


class Api:

    def __init__(self, endpoint, token):
        self.endpoint = endpoint
        self.token = token

    def get_history(self):
        r = requests.get(urljoin(self.endpoint, '/v1/sport/run/history.json'), headers={
            'apptoken': self.token
        })
        r.raise_for_status()

        return r.json()

    def get_detail(self, track_id, source):
        r = requests.get(urljoin(self.endpoint, '/v1/sport/run/detail.json'), headers={
            'apptoken': self.token
        }, params={
            'trackid': track_id,
            'source': source,
        })
        r.raise_for_status()

        return r.json()
