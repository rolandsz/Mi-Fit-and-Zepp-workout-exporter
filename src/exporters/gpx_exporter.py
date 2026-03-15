# Based on https://github.com/mireq/MiFitDataExport
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from src.api import WorkoutDetail, WorkoutSummary
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
        LOGGER.warning(
            f"Unhandled type for workout {summary.trackid}: {summary.type}")

    return workout_type


class GpxExporter(BaseExporter):
    def get_supported_file_formats(self) -> List[str]:
        return ["gpx"]

    def export(
        self,
        output_file_path: Path,
        summary: WorkoutSummary,
        points: List[ExportablePoint],
        detail: WorkoutDetail,
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
            # Add description with workout metadata
            desc_parts = []
            if summary.dis:
                desc_parts.append(f"Distance: {summary.dis} km")
            if summary.calorie:
                desc_parts.append(f"Calories: {summary.calorie}")
            if summary.run_time:
                desc_parts.append(f"Duration: {summary.run_time} s")
            if summary.avg_pace:
                desc_parts.append(f"Avg Pace: {summary.avg_pace}")
            if summary.avg_heart_rate:
                desc_parts.append(f"Avg HR: {summary.avg_heart_rate}")
            # Add more metadata
            if summary.total_step:
                desc_parts.append(f"Steps: {summary.total_step}")
            if summary.altitude_ascend:
                desc_parts.append(f"Ascend: {summary.altitude_ascend} m")
            if summary.altitude_descend:
                desc_parts.append(f"Descend: {summary.altitude_descend} m")
            if summary.max_pace:
                desc_parts.append(f"Max Pace: {summary.max_pace}")
            if summary.min_pace:
                desc_parts.append(f"Min Pace: {summary.min_pace}")
            # Add additional data from detail
            if detail.activity:
                if detail.activity.get("user"):
                    desc_parts.append(f"User: {detail.activity['user']}")
                if detail.activity.get("device"):
                    desc_parts.append(f"Device: {detail.activity['device']}")
                if detail.activity.get("date"):
                    desc_parts.append(f"Date: {detail.activity['date']}")
                if detail.activity.get("start_time"):
                    desc_parts.append(
                        f"Start Time: {detail.activity['start_time']}")
            if detail.summary:
                if detail.summary.get("duration"):
                    desc_parts.append(
                        f"Duration: {detail.summary['duration']}")
                if detail.summary.get("calories_kcal"):
                    desc_parts.append(
                        f"Calories: {detail.summary['calories_kcal']} kcal")
                if detail.summary.get("heart_rate") and detail.summary["heart_rate"].get("avg_bpm"):
                    desc_parts.append(
                        f"Avg BPM: {detail.summary['heart_rate']['avg_bpm']}")
                if detail.summary.get("heart_rate") and detail.summary["heart_rate"].get("max_bpm"):
                    desc_parts.append(
                        f"Max BPM: {detail.summary['heart_rate']['max_bpm']}")
            if detail.heart_rate_zones:
                zones = []
                for zone_name, zone_data in detail.heart_rate_zones.items():
                    if zone_data.get("time") and zone_data["time"] != "00:00":
                        zones.append(f"{zone_name}: {zone_data['time']}")
                if zones:
                    desc_parts.append(f"HR Zones: {', '.join(zones)}")
            if desc_parts:
                desc = "; ".join(desc_parts)
                fp.write(f"{ind}{ind}<desc>{desc}</desc>\n")

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
