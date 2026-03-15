import argparse
import logging
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import List

from src.api import Api
from src.auth import get_app_token
from src.exporters.base_exporter import BaseExporter
from src.exporters.geopandas_exporter import GeoPandasExporter
from src.exporters.gpx_exporter import GpxExporter
from src.scraper import Scraper


def get_exporters() -> List[BaseExporter]:
    exporters: List[BaseExporter] = [GpxExporter(), GeoPandasExporter()]
    return exporters


def get_supported_file_formats(exporters: List[BaseExporter]) -> List[str]:
    supported_file_formats = [
        file_format
        for exporter in exporters
        for file_format in exporter.get_supported_file_formats()
    ]
    assert len(supported_file_formats) > 0
    return supported_file_formats


def parse_date_to_timestamp(date_str, is_end=False):
    if date_str is None:
        return math.inf if is_end else -math.inf

    try:
        dt = datetime.strptime(
            date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)

        if is_end:
            dt = dt.replace(hour=23, minute=59, second=59, microsecond=999999)

        return dt.timestamp()

    except ValueError as e:
        raise ValueError(f"Invalid date format '{date_str}': {e}") from e


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    exporters = get_exporters()
    supported_file_formats = get_supported_file_formats(exporters)

    ap = argparse.ArgumentParser()
    ap.add_argument(
        "-e",
        "--endpoint",
        default="https://api-mifit.huami.com",
        help="The endpoint to be used",
    )
    ap.add_argument("-t", "--token", help="A valid application token")
    ap.add_argument(
        "-f",
        "--file-format",
        default=supported_file_formats[0],
        choices=supported_file_formats,
        help="File format of the exported workouts",
    )
    ap.add_argument(
        "-o",
        "--output-directory",
        default="./workouts",
        type=Path,
        help="A directory where the downloaded workouts will be stored",
    )
    ap.add_argument(
        "--start-date",
        default=None,
        type=str,
        help="Start date in YYYY-MM-DD format (optional)"
    )
    ap.add_argument(
        "--end-date",
        default=None,
        type=str,
        help="End date in YYYY-MM-DD format (optional)"
    )
    ap.add_argument(
        "--include-no-gps",
        action="store_true",
        help="Include workouts that have no GPS data"
    )

    args = vars(ap.parse_args())

    if not args["token"]:
        args["token"] = get_app_token()

    if args["token"]:
        api = Api(args["endpoint"], args["token"])

        exporter = next(
            exporter
            for exporter in exporters
            if args["file_format"] in exporter.get_supported_file_formats()
        )

        start_ts = parse_date_to_timestamp(args["start_date"], is_end=False)
        end_ts = parse_date_to_timestamp(args["end_date"], is_end=True)

        scraper = Scraper(api, exporter, args["output_directory"],
                          args["file_format"], start_ts, end_ts, args["include_no_gps"])
        scraper.run()
