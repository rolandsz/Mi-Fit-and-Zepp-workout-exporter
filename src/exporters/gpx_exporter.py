# Based on https://github.com/mireq/MiFitDataExport
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from src.api import WorkoutSummary
from src.exporters.base_exporter import BaseExporter, ExportablePoint

LOGGER = logging.getLogger(__name__)

WORKOUT_TYPE_MAP = {
    1: "running",
    6: "walking",
    8: "treadmill_running",
    9: "cycling",
    10: "indoor_cycling",
    16: "other",
    23: "indoor_rowing",
    92: "badminton",
}


def _map_workout_type(summary: WorkoutSummary) -> Optional[str]:
    if not (workout_type := WORKOUT_TYPE_MAP.get(summary.type)):
        LOGGER.warning(f"Unhandled type for workout {summary.trackid}: {summary.type}")

    return workout_type


class GpxExporter(BaseExporter):
    def get_supported_file_formats(self) -> List[str]:
        return ["gpx"]

    def export(
        self,
        output_file_path: Path,
        summary: WorkoutSummary,
        points: List[ExportablePoint],
    ):
        ind = "\t"
        with output_file_path.open(mode="w") as fp:
            time = datetime.utcfromtimestamp(int(summary.trackid)).isoformat()
            fp.write('<?xml version="1.0" encoding="UTF-8" standalone="no" ?>\n')
            fp.write(
                '<gpx xmlns="http://www.topografix.com/GPX/1/1" '
                'xmlns:gpxdata="http://www.cluetrust.com/XML/GPXDATA/1/0" '
                'xmlns:gpxtpx="http://www.garmin.com/xmlschemas/TrackPointExtension/v1">\n'
            )
            fp.write(f"{ind}<metadata><time>{time}</time></metadata>\n")
            fp.write(f"{ind}<trk>\n")
            fp.write(f"{ind}{ind}<name>{time}</name>\n")

            if workout_type := _map_workout_type(summary):
                fp.write(f"{ind}{ind}<type>{workout_type}</type>\n")

            fp.write(f"{ind}{ind}<trkseg>\n")
            for point in points:
                ext_hr = ""
                ext_cadence = ""
                if point.heart_rate:
                    ext_hr = (
                        f"<gpxtpx:TrackPointExtension>"
                        f"<gpxtpx:hr>{int(point.heart_rate)}</gpxtpx:hr>"
                        f"</gpxtpx:TrackPointExtension>"
                        f"<gpxdata:hr>{int(point.heart_rate)}</gpxdata:hr>"
                    )
                if point.cadence:
                    ext_cadence = f"<gpxdata:cadence>{point.cadence}</gpxdata:cadence>"
                fp.write(
                    f'{ind}{ind}{ind}<trkpt lat="{point.latitude}" lon="{point.longitude}">'
                    f"<ele>{point.altitude}</ele>"
                    f"<time>{point.time.isoformat()}</time>"
                    f"<extensions>"
                    f"{ext_hr}{ext_cadence}"
                    f"</extensions>"
                    f"</trkpt>\n"
                )
            fp.write(f"{ind}{ind}</trkseg>\n")
            fp.write(f"{ind}</trk>\n")
            fp.write("</gpx>")
