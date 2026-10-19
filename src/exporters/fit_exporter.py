# Based on https://github.com/mireq/MiFitDataExport
import logging
from pathlib import Path
from typing import List, Tuple

from fit_tool.fit_file_builder import FitFileBuilder
from fit_tool.profile.messages.file_id_message import FileIdMessage
from fit_tool.profile.messages.record_message import RecordMessage
from fit_tool.profile.messages.lap_message import LapMessage
from fit_tool.profile.messages.session_message import SessionMessage
from fit_tool.profile.messages.activity_message import ActivityMessage
from fit_tool.profile.profile_type import FileType, Manufacturer, Sport, SubSport

from src.api import WorkoutSummary
from src.exporters.base_exporter import BaseExporter, ExportablePoint

LOGGER = logging.getLogger(__name__)

# Mapping von Huami-Sporttypen auf Garmin Sport- & SubSport-Enums
WORKOUT_TYPE_MAP = {
    1: (Sport.RUNNING, SubSport.GENERIC),
    6: (Sport.WALKING, SubSport.GENERIC),
    8: (Sport.RUNNING, SubSport.TREADMILL),
    9: (Sport.CYCLING, SubSport.GENERIC),
    10: (Sport.CYCLING, SubSport.INDOOR_CYCLING),
    16: (Sport.GENERIC, SubSport.GENERIC),
    23: (Sport.ROWING, SubSport.INDOOR_ROWING),
}


def _map_workout_type(summary: WorkoutSummary) -> Tuple[Sport, SubSport]:
    if summary.type in WORKOUT_TYPE_MAP:
        return WORKOUT_TYPE_MAP[summary.type]
    
    LOGGER.warning(f"Unhandled type for workout {summary.trackid}: {summary.type}. Defaulting to GENERIC.")
    return Sport.GENERIC, SubSport.GENERIC


class FitExporter(BaseExporter):
    def get_supported_file_formats(self) -> List[str]:
        return ["fit"]

    def export(
        self,
        output_file_path: Path,
        summary: WorkoutSummary,
        points: List[ExportablePoint],
    ):
        builder = FitFileBuilder(auto_define=True)

        # 1. Zeitstempel vorbereiten (fit-tool benötigt Millisekunden)
        end_timestamp_ms = int(summary.end_time) * 1000
        duration_ms = int(summary.run_time) * 1000
        start_timestamp_ms = end_timestamp_ms - duration_ms

        # 2. File ID Message hinzufügen
        file_id = FileIdMessage()
        file_id.type = FileType.ACTIVITY
        file_id.manufacturer = Manufacturer.DEVELOPMENT
        file_id.product = 0
        file_id.serial_number = int(summary.trackid)
        file_id.time_created = start_timestamp_ms
        builder.add(file_id)

        # 3. Trackpunkte (Record Messages) konvertieren und hinzufügen
        # Falls keine Punkte via API kamen, nutzen wir den Start/Endzeitpunkt der Summary
        last_timestamp_ms = start_timestamp_ms
        
        for point in points:
            record = RecordMessage()
            
            # Konvertiert das Python datetime-Objekt des Punktes in Millisekunden
            p_timestamp_ms = int(point.time.timestamp() * 1000)
            record.timestamp = p_timestamp_ms
            last_timestamp_ms = p_timestamp_ms

            # GPS-Daten vorhanden? (Wandlung von Grad in Semicircles für FIT)
            if point.latitude is not None and point.longitude is not None:
                record.position_lat = point.latitude
                record.position_long = point.longitude

            if point.altitude is not None:
                if float(point.altitude) > 0:
                    record.altitude = float(point.altitude)

            if point.heart_rate:
                record.heart_rate = int(point.heart_rate)

            if point.cadence:
                record.cadence = int(point.cadence)

            builder.add(record)

        # Falls die Punktliste leer war, sichern wir ab, dass der Endzeitpunkt stimmt
        if not points:
            last_timestamp_ms = end_timestamp_ms

        # 4. Lap Message (Runden-Zusammenfassung)
        lap = LapMessage()
        lap.start_time = start_timestamp_ms
        lap.timestamp = last_timestamp_ms
        lap.total_elapsed_time = float(summary.run_time)
        lap.total_timer_time = float(summary.run_time)
        lap.total_distance = float(summary.dis)
        if summary.avg_heart_rate:
            if float(summary.avg_heart_rate) >= 0:
                lap.avg_heart_rate = float(summary.avg_heart_rate)
        if summary.max_heart_rate:
            if float(summary.max_heart_rate) >= 0:
                lap.max_heart_rate = float(summary.max_heart_rate)
        if summary.avg_cadence:
            if float(summary.avg_cadence) >= 0:
                lap.avg_cadence = float(summary.avg_cadence)
        if summary.max_cadence:
            if float(summary.max_cadence) >= 0:
                lap.max_cadence = float(summary.max_cadence)
        builder.add(lap)

        # 5. Session Message (Workout-Zusammenfassung)
        session = SessionMessage()
        session.start_time = start_timestamp_ms
        session.timestamp = last_timestamp_ms
        session.total_elapsed_time = float(summary.run_time)
        session.total_timer_time = float(summary.run_time)
        session.total_distance = float(summary.dis)
        session.total_calories = int(float(summary.calorie))
        
        if summary.avg_heart_rate:
            session.avg_heart_rate = int(float(summary.avg_heart_rate))
        if summary.max_heart_rate:
            session.max_heart_rate = int(summary.max_heart_rate)
        if summary.avg_cadence:
            if float(summary.avg_cadence) >= 0:
                session.avg_cadence = int(summary.avg_cadence)
        if summary.max_cadence:
            if float(summary.max_cadence) >= 0:
                session.max_cadence = int(summary.max_cadence)

        # Sportprofile zuweisen
        sport, sub_sport = _map_workout_type(summary)
        session.sport = sport
        session.sub_sport = sub_sport
        builder.add(session)

        # 6. Activity Message (Abschluss)
        activity = ActivityMessage()
        activity.timestamp = last_timestamp_ms
        activity.num_sessions = 1
        activity.total_timer_time = float(summary.run_time)
        activity.local_timestamp = last_timestamp_ms//1000
        builder.add(activity)

        # 7. Datei als Binärdatei kompilieren und wegschreiben
        fit_file = builder.build()
        
        # Sicherstellen, dass das Verzeichnis existiert
        output_file_path.parent.mkdir(parents=True, exist_ok=True)
        fit_file.to_file(str(output_file_path))
