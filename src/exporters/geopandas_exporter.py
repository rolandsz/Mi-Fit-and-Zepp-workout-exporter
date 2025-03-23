import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List

import geopandas as gpd
from shapely.geometry import Point

from src.api import WorkoutSummary
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
    ):
        track_date = datetime.utcfromtimestamp(int(summary.trackid)).isoformat()

        data = [
            {
                "track_date": track_date,
                "timestamp": point.time.isoformat(),
                "latitude": point.latitude,
                "longitude": point.longitude,
                "altitude": point.altitude,
                "heart_rate": point.heart_rate,
                "cadence": point.cadence,
                "geometry": Point(point.latitude, point.longitude),
            }
            for point in points
        ]

        gdf = gpd.GeoDataFrame(data, geometry="geometry")
        gdf = gdf[
            [
                "track_date",
                "timestamp",
                "latitude",
                "longitude",
                "altitude",
                "heart_rate",
                "cadence",
                "geometry",
            ]
        ]
        gdf.geometry = gdf.geometry.set_crs(epsg=4326)
        gdf.geometry = gdf.geometry.to_crs(epsg=4326)

        ext = output_file_path.suffix

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
        elif ext == ".xslx":
            gdf.to_excel(output_file_path)
        elif ext in [".sql", ".sqlite3"]:
            con = sqlite3.connect(":memory:" if ext == ".sql" else output_file_path)
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
