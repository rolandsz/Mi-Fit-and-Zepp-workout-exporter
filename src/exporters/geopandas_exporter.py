# type: ignore
import logging
from pathlib import Path
from datetime import datetime
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
                "latitude": point.latitude,
                "longitude": point.longitude,
                "altitude": point.altitude,
                "timestamp": point.time.isoformat(),
            }
            for point in points
        ]

        # list -> GeoDataFrame
        gdf = gpd.GeoDataFrame(data)

        # Shape points for Geometry
        gdf["geometry"] = [
            Point(gdf.latitude[point], gdf.longitude[point])
            for point in range(len(gdf))
        ]

        # Sorting columns
        gdf = gdf[
            ["track_date", "timestamp", "latitude", "longitude", "altitude", "geometry"]
        ]

        # Set crs for Geometry
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
            gdf.to_json(output_file_path)
        elif ext == ".xslx":
            gdf.to_excel(output_file_path)
        elif ext == ".sql":
            gdf.to_sql(output_file_path)
        elif ext == ".xml":
            gdf.to_xml(output_file_path)
        elif ext == ".html":
            gdf.to_html(output_file_path)
        else:
            LOGGER.error(f"File format is not implemented: {ext}")
