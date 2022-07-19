# type: ignore
# Based on https://github.com/mireq/MiFitDataExport
import abc
import array
from bisect import bisect_left
from collections import namedtuple
from datetime import datetime
from itertools import accumulate
from pathlib import Path
from typing import List, Optional

from pydantic import BaseModel

from src.api import WorkoutSummary, WorkoutDetailData

NO_VALUE = -2000000
FIX_BIP_GAPS = False

RawTrackData = namedtuple(
    "RawTrackData",
    [
        "start_time",
        "end_time",
        "cost_time",
        "distance",
        "times",
        "lat",
        "lon",
        "alt",
        "hrtimes",
        "hr",
        "steptimes",
        "stride",
        "cadence",
    ],
)
Position = namedtuple("Position", ["lat", "lon", "alt"])
TrackPoint = namedtuple("TrackPoint", ["time", "position", "hr", "stride", "cadence"])


class Interpolate(object):
    def __init__(self, x_list, y_list):
        intervals = zip(x_list, x_list[1:], y_list, y_list[1:])
        self.x_list = x_list
        self.y_list = y_list
        self.slopes = [(y2 - y1) // ((x2 - x1) or 1) for x1, x2, y1, y2 in intervals]

    def __getitem__(self, x):
        i = bisect_left(self.x_list, x) - 1
        if i >= len(self.slopes):
            return self.y_list[-1]
        if i < 0:
            return self.y_list[0]
        return self.y_list[i] + self.slopes[i] * (x - self.x_list[i])


class ExportablePoint(BaseModel):
    time: datetime
    latitude: float
    longitude: float
    altitude: Optional[float]
    heart_rate: Optional[float]
    cadence: Optional[float]


def parse_track_data(summary: WorkoutSummary, detail: WorkoutDetailData):
    return RawTrackData(
        start_time=int(summary.trackid),
        end_time=int(summary.end_time),
        cost_time=-1,
        distance=float(summary.dis),
        times=array.array(
            "q",
            [int(val) for val in list(filter(None, detail.time.split(";")))]
            if detail.time
            else [],
        ),
        lat=array.array(
            "q",
            [
                int(val.split(",")[0])
                for val in list(filter(None, detail.longitude_latitude.split(";")))
            ]
            if detail.longitude_latitude
            else [],
        ),
        lon=array.array(
            "q",
            [
                int(val.split(",")[1])
                for val in list(filter(None, detail.longitude_latitude.split(";")))
            ]
            if detail.longitude_latitude
            else [],
        ),
        alt=array.array(
            "q",
            [int(val) for val in list(filter(None, detail.altitude.split(";")))]
            if detail.altitude
            else [],
        ),
        hrtimes=array.array(
            "q",
            [
                int(val.split(",")[0] or 1)
                for val in list(filter(None, detail.heart_rate.split(";")))
            ]
            if detail.heart_rate
            else [],
        ),
        hr=array.array(
            "q",
            [
                int(val.split(",")[1])
                for val in list(filter(None, detail.heart_rate.split(";")))
            ]
            if detail.heart_rate
            else [],
        ),
        steptimes=array.array(
            "q",
            [
                int(val.split(",")[0])
                for val in list(filter(None, detail.gait.split(";")))
            ]
            if detail.gait
            else [],
        ),
        stride=array.array(
            "q",
            [
                int(val.split(",")[2])
                for val in list(filter(None, detail.gait.split(";")))
            ]
            if detail.gait
            else [],
        ),
        cadence=array.array(
            "q",
            [
                int(val.split(",")[3])
                for val in list(filter(None, detail.gait.split(";")))
            ]
            if detail.gait
            else [],
        ),
    )


def interpolate_column(data, original_points, new_points):
    data = array.array("q", data)
    old_value = NO_VALUE
    for old_value in data:
        if old_value != NO_VALUE:
            break
    for i, value in enumerate(data):
        if value == NO_VALUE:
            data[i] = old_value
        else:
            old_value = value

    if len(new_points) == 0:
        return array.array("q", [])
    if len(original_points) == 0:
        return array.array("q", [0] * len(new_points))
    if len(original_points) == 1:
        return array.array("q", [original_points[0]] * len(new_points))
    interpolate = Interpolate(original_points, data)
    return array.array("q", (interpolate[point] for point in new_points))


def track_points(track_data):
    for time, lat, lon, alt, hr, stride, cadence in zip(
        track_data.times,
        track_data.lat,
        track_data.lon,
        track_data.alt,
        track_data.hr,
        track_data.stride,
        track_data.cadence,
    ):
        yield TrackPoint(
            time=time,
            position=Position(lat=lat / 100000000, lon=lon / 100000000, alt=alt / 100),
            hr=hr,
            stride=stride,
            cadence=cadence,
        )


def interpolate_data(track_data):
    track_times = array.array("q", accumulate(track_data.times))
    hr_times = array.array("q", accumulate(track_data.hrtimes))
    step_times = array.array("q", accumulate(track_data.steptimes))

    def change_times(times, change, time_from):
        return array.array(
            "q", (time + change if time >= time_from else time for time in times)
        )

    times = list(sorted(set(track_times).union(hr_times).union(step_times)))

    if FIX_BIP_GAPS:
        time_to_trim = (times[-1] - track_data.cost_time) if track_times else 0
        while time_to_trim > 0:
            max_time = 0
            max_interval = 0
            last_time = 0
            for time in times:
                current_interval = time - last_time
                last_time = time
                if current_interval > max_interval:
                    max_interval = current_interval
                    max_time = time
            time_change = max(max_interval - time_to_trim, 1) - max_interval
            track_times = change_times(track_times, time_change, max_time)
            hr_times = change_times(hr_times, time_change, max_time)
            step_times = change_times(step_times, time_change, max_time)
            time_to_trim += time_change
            times = list(sorted(set(track_times).union(hr_times).union(step_times)))

    return track_data._replace(
        times=times,
        lat=interpolate_column(accumulate(track_data.lat), track_times, times),
        lon=interpolate_column(accumulate(track_data.lon), track_times, times),
        alt=interpolate_column(track_data.alt, track_times, times),
        hrtimes=times,
        hr=interpolate_column(accumulate(track_data.hr), hr_times, times),
        steptimes=times,
        stride=interpolate_column(track_data.stride, step_times, times),
        cadence=interpolate_column(track_data.cadence, step_times, times),
    )


def parse_points(
    summary: WorkoutSummary, detail: WorkoutDetailData
) -> List[ExportablePoint]:
    track_data = parse_track_data(summary, detail)

    if not track_data.lat:
        return []

    points = [
        ExportablePoint(
            time=datetime.utcfromtimestamp(point.time + track_data.start_time),
            latitude=point.position.lat,
            longitude=point.position.lon,
            altitude=point.position.alt,
            heart_rate=point.hr,
            cadence=point.cadence,
        )
        for point in track_points(interpolate_data(track_data))
    ]

    return points


class BaseExporter(abc.ABC):
    @abc.abstractmethod
    def get_supported_file_formats(self) -> List[str]:
        raise NotImplementedError()

    @abc.abstractmethod
    def export(
        self,
        output_file_path: Path,
        summary: WorkoutSummary,
        points: List[ExportablePoint],
    ):
        raise NotImplementedError()
