import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List

import geopandas as gpd
from shapely.geometry import Point

from src.api import WorkoutDetail, WorkoutSummary
from src.exporters.base_exporter import BaseExporter, ExportablePoint

LOGGER = logging.getLogger(__name__)


class GeoPandasExporter(BaseExporter):
    def get_supported_file_formats(self) -> List[str]:
        return [
            "geojson",
            "gpkg",
            "parquet",
            "shp",
            "csv",
            "json",
            "xlsx",
            "sql",
            "sqlite3",
            "xml",
            "html",
        ]

    def export(
        self,
        output_file_path: Path,
        summary: WorkoutSummary,
        points: List[ExportablePoint],
        detail: WorkoutDetail,
    ):
        track_date = datetime.utcfromtimestamp(
            int(summary.trackid)).isoformat()

        if points:
            data = [
                {
                    "track_date": track_date,
                    "timestamp": point.time.isoformat(),
                    "latitude": point.latitude,
                    "longitude": point.longitude,
                    "altitude": point.altitude,
                    "heart_rate": point.heart_rate,
                    "cadence": point.cadence,
                    # Note: Point(lon, lat)
                    "geometry": Point(point.longitude, point.latitude),
                    "user": detail.activity.get("user") if detail.activity else None,
                    "device": detail.activity.get("device") if detail.activity else None,
                    "activity_date": detail.activity.get("date") if detail.activity else None,
                    "start_time": detail.activity.get("start_time") if detail.activity else None,
                    "duration": detail.summary.get("duration") if detail.summary else None,
                    "calories_kcal": detail.summary.get("calories_kcal") if detail.summary else None,
                    "avg_bpm": detail.summary.get("heart_rate", {}).get("avg_bpm") if detail.summary and detail.summary.get("heart_rate") else None,
                    "max_bpm": detail.summary.get("heart_rate", {}).get("max_bpm") if detail.summary and detail.summary.get("heart_rate") else None,
                }
                for point in points
            ]
            gdf = gpd.GeoDataFrame(data, geometry="geometry")
            columns = [
                "track_date",
                "timestamp",
                "latitude",
                "longitude",
                "altitude",
                "heart_rate",
                "cadence",
                "geometry",
            ]
            gdf = gdf[columns]
            gdf.geometry = gdf.geometry.set_crs(epsg=4326)
            gdf.geometry = gdf.geometry.to_crs(epsg=4326)
        else:
            # For workouts without GPS, use regular DataFrame with metadata
            import pandas as pd
            data = [{
                "track_date": track_date,
                "timestamp": track_date,
                "latitude": None,
                "longitude": None,
                "altitude": None,
                "heart_rate": summary.avg_heart_rate if summary.avg_heart_rate else None,
                "cadence": None,
                "distance_km": summary.dis,
                "calories": summary.calorie,
                "duration_s": summary.run_time,
                "avg_pace": summary.avg_pace,
                "workout_type": summary.type,
                "total_steps": summary.total_step,
                "altitude_ascend": summary.altitude_ascend,
                "altitude_descend": summary.altitude_descend,
                "max_pace": summary.max_pace,
                "min_pace": summary.min_pace,
                "user": detail.activity.get("user") if detail.activity else None,
                "device": detail.activity.get("device") if detail.activity else None,
                "activity_date": detail.activity.get("date") if detail.activity else None,
                "start_time": detail.activity.get("start_time") if detail.activity else None,
                "duration": detail.summary.get("duration") if detail.summary else None,
                "calories_kcal": detail.summary.get("calories_kcal") if detail.summary else None,
                "avg_bpm": detail.summary.get("heart_rate", {}).get("avg_bpm") if detail.summary and detail.summary.get("heart_rate") else None,
                "max_bpm": detail.summary.get("heart_rate", {}).get("max_bpm") if detail.summary and detail.summary.get("heart_rate") else None,
            }]
            df = pd.DataFrame(data)
            columns = [
                "track_date",
                "timestamp",
                "latitude",
                "longitude",
                "altitude",
                "heart_rate",
                "cadence",
                "distance_km",
                "calories",
                "duration_s",
                "avg_pace",
                "workout_type",
                "total_steps",
                "altitude_ascend",
                "altitude_descend",
                "max_pace",
                "min_pace",
                "user",
                "device",
                "activity_date",
                "start_time",
                "duration",
                "calories_kcal",
                "avg_bpm",
                "max_bpm",
            ]
            df = df[columns]

        ext = output_file_path.suffix

        if points:
            if ext == ".geojson":
                gdf.to_file(output_file_path, driver="GeoJSON")
            elif ext == ".gpkg":
                gdf.to_file(output_file_path, driver="GPKG")
            elif ext == ".parquet":
                gdf.to_parquet(output_file_path)
            elif ext == ".shp":
                gdf.to_file(output_file_path, driver="ESRI Shapefile")
            elif ext == ".csv":
                gdf.to_csv(output_file_path)
            elif ext == ".json":
                gdf.to_json(str(output_file_path))
            elif ext == ".xlsx":
                gdf.to_excel(output_file_path)
            elif ext in [".sql", ".sqlite3"]:
                con = sqlite3.connect(
                    ":memory:" if ext == ".sql" else output_file_path)
                gdf.drop(columns=["geometry"]).to_sql(
                    name="points", con=con, if_exists="append"
                )

                if ext == ".sql":
                    with open(output_file_path, "w") as f:
                        for line in con.iterdump():
                            f.write(f"{line}\n")
            elif ext == ".xml":
                gdf.to_xml(output_file_path)
            elif ext == ".html":
                gdf.to_html(output_file_path)
            else:
                LOGGER.error(f"File format is not implemented: {ext}")
        else:
            # For no GPS data, export metadata
            if ext == ".csv":
                df.to_csv(output_file_path, index=False)
            elif ext == ".json":
                df.to_json(str(output_file_path), orient="records")
            elif ext == ".xlsx":
                df.to_excel(output_file_path, index=False)
            elif ext in [".sql", ".sqlite3"]:
                con = sqlite3.connect(
                    ":memory:" if ext == ".sql" else output_file_path)
                df.to_sql(name="workouts", con=con,
                          if_exists="append", index=False)

                if ext == ".sql":
                    with open(output_file_path, "w") as f:
                        for line in con.iterdump():
                            f.write(f"{line}\n")
            elif ext == ".xml":
                df.to_xml(output_file_path)
            elif ext == ".html":
                df.to_html(output_file_path, index=False)
            else:
                # For geo formats without GPS, export as CSV
                df.to_csv(output_file_path.with_suffix(".csv"), index=False)
