import logging
from datetime import datetime
from pathlib import Path
from typing import List

from src.api import Api, WorkoutSummary
from src.exporters.base_exporter import BaseExporter, parse_points

LOGGER = logging.getLogger(__name__)


class Scraper:
    def __init__(
        self, api: Api, exporter: BaseExporter, output_dir: Path, file_format: str, start_ts: float, end_ts: float, include_no_gps: bool = False
    ):
        self.api: Api = api
        self.exporter: BaseExporter = exporter
        self.output_dir: Path = output_dir
        self.file_format: str = file_format
        self.start_ts: float = start_ts
        self.end_ts: float = end_ts
        self.include_no_gps: bool = include_no_gps

        if start_ts > end_ts:
            raise ValueError("Start date cannot be after end date")

    def get_output_file_path(self, file_name: str) -> Path:
        return (self.output_dir / file_name).with_suffix(f".{self.file_format}")

    def fetch_workout_summaries(self) -> List[WorkoutSummary]:
        summaries: List[WorkoutSummary] = []

        history = self.api.get_workout_history()
        summaries.extend(history.data.summary)

        while history.data.next != -1:
            logging.info(
                f"Fetching more summaries starting from workout {history.data.next}"
            )
            history = self.api.get_workout_history(
                from_track_id=history.data.next)
            summaries.extend(history.data.summary)

        logging.info(f"There are {len(summaries)} workouts in total")
        return summaries

    def run(self) -> None:
        summaries = self.fetch_workout_summaries()
        filtered_summaries = [
            s for s in summaries
            if self.start_ts <= int(s.trackid) <= self.end_ts
        ]

        for summary in filtered_summaries:
            detail = self.api.get_workout_detail(summary)

            points = parse_points(summary, detail.data)
            if not points:
                if not self.include_no_gps:
                    LOGGER.warning(
                        f"Skipping workout {summary.trackid} because it has no points"
                    )
                    continue
                else:
                    LOGGER.info(
                        f"Detail for workout {summary.trackid} (no GPS): activity={detail.activity}, summary={detail.summary}, heart_rate_zones={detail.heart_rate_zones}")

            track_id = int(summary.trackid)

            track_id = int(summary.trackid)
            file_name = datetime.fromtimestamp(track_id).strftime(
                "Workout--%Y-%m-%d--%H-%M-%S"
            )

            output_file_path = self.get_output_file_path(file_name)
            output_file_path.parent.mkdir(exist_ok=True)
            assert output_file_path.parent.exists(), "Couldn't create output folder"

            self.exporter.export(output_file_path, summary, points, detail)
            LOGGER.info(f"Downloaded {output_file_path}")
