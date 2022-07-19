import logging
from datetime import datetime
from pathlib import Path

from src.api import Api
from src.exporters.base_exporter import BaseExporter, parse_points

LOGGER = logging.getLogger(__name__)


class Scraper:
    def __init__(
        self, api: Api, exporter: BaseExporter, output_dir: Path, file_format: str
    ):
        self.api: Api = api
        self.exporter: BaseExporter = exporter
        self.output_dir: Path = output_dir
        self.file_format: str = file_format

    def get_output_file_path(self, file_name: str) -> Path:
        return (self.output_dir / file_name).with_suffix(f".{self.file_format}")

    def run(self) -> None:
        workout_history = self.api.get_workout_history()
        logging.info(f"There are {len(workout_history.data.summary)} workouts")

        for summary in workout_history.data.summary:
            detail = self.api.get_workout_detail(summary)

            track_id = int(summary.trackid)
            file_name = datetime.fromtimestamp(track_id).strftime(
                "Workout--%Y-%m-%d--%H-%M-%S"
            )

            output_file_path = self.get_output_file_path(file_name)
            output_file_path.parent.mkdir(exist_ok=True)

            points = parse_points(summary, detail.data)

            self.exporter.export(output_file_path, summary, points)
            LOGGER.info(f"Downloaded {output_file_path}")
