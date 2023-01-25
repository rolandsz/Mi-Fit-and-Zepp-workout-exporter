from typing import Any, Dict, List, Optional
from urllib.parse import urljoin

import requests
from pydantic import BaseModel

from src import constants


class WorkoutSummary(BaseModel):
    trackid: str
    source: str
    dis: str
    calorie: str
    end_time: str
    run_time: str
    avg_pace: str
    avg_frequency: str
    avg_heart_rate: str
    type: int
    location: str
    city: str
    forefoot_ratio: str
    bind_device: str
    max_pace: Optional[float]
    min_pace: Optional[float]
    version: int
    altitude_ascend: Optional[int]
    altitude_descend: Optional[int]
    total_step: Optional[int]
    avg_stride_length: Optional[int]
    max_frequency: Optional[int]
    max_altitude: Optional[int]
    min_altitude: Optional[int]
    lap_distance: Optional[int]
    sync_to: Optional[str]
    distance_ascend: Optional[int]
    max_cadence: Optional[int]
    avg_cadence: Optional[int]
    landing_time: Optional[int]
    flight_ratio: Optional[int]
    climb_dis_descend: Optional[int]
    climb_dis_ascend_time: Optional[int]
    climb_dis_descend_time: Optional[int]
    child_list: Optional[str]
    parent_trackid: Optional[int]
    max_heart_rate: Optional[int]
    min_heart_rate: Optional[int]
    swolf: Optional[int]
    total_strokes: Optional[int]
    total_trips: Optional[int]
    avg_stroke_speed: Optional[float]
    max_stroke_speed: Optional[float]
    avg_distance_per_stroke: Optional[float]
    swim_pool_length: Optional[int]
    te: Optional[int]
    swim_style: Optional[int]
    unit: Optional[int]
    add_info: Optional[str]
    sport_mode: Optional[int]
    downhill_num: Optional[int]
    downhill_max_altitude_desend: Optional[int]
    strokes: Optional[int]
    fore_hand: Optional[int]
    back_hand: Optional[int]
    serve: Optional[int]
    second_half_start_time: Optional[int]
    pb: Optional[str]
    rope_skipping_count: Optional[int]
    rope_skipping_avg_frequency: Optional[int]
    rope_skipping_max_frequency: Optional[int]
    rope_skipping_rest_time: Optional[int]
    left_landing_time: Optional[int]
    left_flight_ratio: Optional[int]
    right_landing_time: Optional[int]
    right_flight_ratio: Optional[int]
    marathon: Optional[str]
    situps: Optional[int]
    anaerobic_te: Optional[int]
    target_type: Optional[int]
    target_value: Optional[str]
    total_group: Optional[int]
    spo2_max: Optional[int]
    spo2_min: Optional[int]
    avg_altitude: Optional[float]
    max_slope: Optional[int]
    avg_slope: Optional[int]
    avg_pulloar_time: Optional[float]
    avg_return_time: Optional[float]
    floor_number: Optional[int]
    upstairs_height: Optional[float]
    min_upstairs_floors: Optional[float]
    accumulated_gap: Optional[int]
    auto_recognition: Optional[int]
    app_name: str
    pause_time: Optional[str]
    heartrate_setting_type: Optional[int]


class WorkoutHistoryData(BaseModel):
    next: int
    summary: List[WorkoutSummary]


class WorkoutHistory(BaseModel):
    code: int
    message: str
    data: WorkoutHistoryData


class WorkoutDetailData(BaseModel):
    trackid: int
    source: str
    longitude_latitude: str
    altitude: str
    accuracy: str
    time: str
    gait: str
    pace: str
    pause: str
    spo2: str
    flag: str
    kilo_pace: str
    mile_pace: str
    heart_rate: str
    version: int
    provider: str
    speed: str
    bearing: str
    distance: str
    lap: str
    air_pressure_altitude: str
    course: str
    correct_altitude: str
    stroke_speed: str
    cadence: str
    daily_performance_info: str
    rope_skipping_frequency: str
    weather_info: str
    coaching_segment: str
    golf_swing_rt_data: str
    power_meter: str


class WorkoutDetail(BaseModel):
    code: int
    message: str
    data: WorkoutDetailData


class Api:
    def __init__(self, endpoint: str, token: str):
        self.base_url: str = endpoint
        self.token: str = token

    def get_workout_history(
        self, from_track_id: Optional[int] = None
    ) -> WorkoutHistory:
        response = self._do_request(
            endpoint="/v1/sport/run/history.json",
            params={"trackid": from_track_id} if from_track_id is not None else {},
        )
        model = WorkoutHistory(**response)
        return model

    def get_workout_detail(self, workout: WorkoutSummary) -> WorkoutDetail:
        response = self._do_request(
            endpoint="/v1/sport/run/detail.json",
            params={
                "trackid": workout.trackid,
                "source": workout.source,
            },
        )
        model = WorkoutDetail(**response)
        return model

    def _do_request(self, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        response = requests.get(
            urljoin(self.base_url, endpoint),
            headers={
                "apptoken": self.token,
                "appPlatform": constants.APP_PLATFORM,
                "appname": constants.APP_NAME,
            },
            params=params,
        )
        response.raise_for_status()
        return response.json()
