import argparse
import logging
from pathlib import Path
from typing import List

from src.api import Api
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
    ap.add_argument("-t", "--token", required=True, help="A valid application token")
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

    args = vars(ap.parse_args())

    api = Api(args["endpoint"], args["token"])

    exporter = next(
        exporter
        for exporter in exporters
        if args["file_format"] in exporter.get_supported_file_formats()
    )
    scraper = Scraper(api, exporter, args["output_directory"], args["file_format"])
    scraper.run()
