from typing import Any, Dict
from urllib.parse import urljoin

import requests


class Api:
    def __init__(self, endpoint: str, token: str):
        self.endpoint: str = endpoint
        self.token: str = token

    def get_history(self) -> Dict[str, Any]:
        r = requests.get(
            urljoin(self.endpoint, "/v1/sport/run/history.json"),
            headers={"apptoken": self.token},
        )
        r.raise_for_status()

        return r.json()

    def get_detail(self, track_id: str, source: str) -> Dict[str, Any]:
        r = requests.get(
            urljoin(self.endpoint, "/v1/sport/run/detail.json"),
            headers={"apptoken": self.token},
            params={
                "trackid": track_id,
                "source": source,
            },
        )
        r.raise_for_status()

        return r.json()
