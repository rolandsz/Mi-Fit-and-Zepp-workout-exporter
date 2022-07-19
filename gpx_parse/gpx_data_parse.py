from datetime import timedelta, datetime

import gpxpy

import geopandas as gpd
from shapely.geometry import Point


class GPXParse:
    """
    The main class in which the gpx file is processed and converted to a GeoDataFrame.

    Input attributes:
        - `path_to_gpx` - path in `str` format that points to a file in `.gpx` format
    """

    def __init__(self, path_to_gpx: str):
        self.path = path_to_gpx

    def parse_gpx_to_raw(self) -> list[dict]:
        """
        A method that takes a file path as input and generates a list with training track values
        """
        with open(self.path, "r") as gpx_file:
            gpx = gpxpy.parse(gpx_file)

        workouts = []
        for track in gpx.tracks:
            for segment in track.segments:
                for point in segment.points:
                    point_dict = {
                        "track_date": datetime.strptime(
                            track.name, "%Y-%m-%dT%H:%M:%S"
                        ),
                        "latitude": point.latitude,
                        "longitude": point.longitude,
                        "altitude": point.elevation,
                        "timestamp": point.time,
                    }
                    workouts.append(point_dict)

        return workouts

    def execute_transform_track(self, diff_gmt: int = 0) -> gpd.GeoDataFrame:
        """
        Method that takes as input the result of the
        `parse_gpx_to_raw` method and converts it to a readable `gpd.GeoDataFrame`

        Input attributes:
            - `diff_gmt` - attribute in `int` format. If necessary, specify the difference from GMT
        """

        # list -> GeoDataFrame
        gdf = gpd.GeoDataFrame(self.parse_gpx_to_raw())

        # GMT -> Local Time
        gdf.timestamp += timedelta(hours=diff_gmt)
        gdf.track_date += timedelta(hours=diff_gmt)

        # Timestamp -> datetime.date
        gdf.track_date = gdf.track_date.apply(lambda x: datetime.date(x))

        # Shape points for Geometry
        gdf["geometry"] = [
            Point(gdf.latitude[point], gdf.longitude[point])
            for point in range(len(gdf))
        ]

        # Sorting columns
        gdf = gdf[
            ["track_date", "timestamp", "latitude", "longitude", "altitude", "geometry"]
        ]

        # Time Zone Exclusion, default = "Z"
        gdf.timestamp = gdf.timestamp.apply(lambda x: x.replace(tzinfo=None))

        # Set crs for Geometry
        gdf.geometry = gdf.geometry.set_crs(epsg=4326)
        gdf.geometry = gdf.geometry.to_crs(epsg=4326)

        return gdf
