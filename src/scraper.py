import json
import logging
import os
from datetime import datetime

from src.api import Api
from third_party.gpx_file_exporter import GpxFileExporter


class Scraper:
    def __init__(self, api: Api, output: str):
        self.api: Api = api
        self.output: str = output

    def get_output_dir_path(self, track_id: str) -> str:
        return os.path.join(self.output, track_id)

    def get_history_file_path(self, track_id: str) -> str:
        return os.path.join(self.get_output_dir_path(track_id), "history.json")

    def get_detail_file_path(self, track_id: str) -> str:
        return os.path.join(self.get_output_dir_path(track_id), "detail.json")

    def get_gpx_file_path(self, track_id: str) -> str:
        return os.path.join(self.get_output_dir_path(track_id), f"{track_id}.gpx")

    def run(self) -> None:
        history = self.api.get_history()
        logging.info(f'There are {len(history["data"]["summary"])} workouts')

        for history in history["data"]["summary"]:
            track_id = history["trackid"]

            # timestamp -> str
            track_date = int(track_id)
            track_date = datetime.fromtimestamp(track_date).strftime('%Y-%m-%d')

            logging.info(f"Downloading workout {track_date}")

            os.makedirs(self.get_output_dir_path(track_date), exist_ok=True)

            # history.json
            history_file_path = self.get_history_file_path(track_date)

            with open(history_file_path, encoding="utf8", mode="w") as f:
                json.dump(history, f)

            # detail.json
            detail = self.api.get_detail(track_id, history["source"])
            detail_file_path = self.get_detail_file_path(track_date)

            with open(detail_file_path, encoding="utf8", mode="w") as f:
                json.dump(detail, f)

            # track_id.gpx
            exporter = GpxFileExporter(
                self.get_gpx_file_path(track_date), history, detail["data"]
            )
            exporter.export()
