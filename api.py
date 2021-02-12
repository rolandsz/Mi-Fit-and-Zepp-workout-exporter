import requests


class Api:

    def __init__(self, token):
        self.token = token

    def get_history(self):
        r = requests.get('https://api-mifit-de2.huami.com/v1/sport/run/history.json', headers={
            'apptoken': self.token
        }, params={
            'source': 'run.mifit.huami.com',
        })
        r.raise_for_status()

        return r.json()

    def get_detail(self, track_id, source):
        r = requests.get('https://api-mifit-de2.huami.com/v1/sport/run/detail.json', headers={
            'apptoken': self.token
        }, params={
            'trackid': track_id,
            'source': source,
        })
        r.raise_for_status()

        return r.json()
