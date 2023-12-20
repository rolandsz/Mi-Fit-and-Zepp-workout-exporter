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
    max_pace: Optional[float] = None
    min_pace: Optional[float] = None
    version: int
    altitude_ascend: Optional[int] = None
    altitude_descend: Optional[int] = None
    total_step: Optional[int] = None
    avg_stride_length: Optional[int] = None
    max_frequency: Optional[int] = None
    max_altitude: Optional[int] = None
    min_altitude: Optional[int] = None
    lap_distance: Optional[int] = None
    sync_to: Optional[str] = None
    distance_ascend: Optional[int] = None
    max_cadence: Optional[int] = None
    avg_cadence: Optional[int] = None
    landing_time: Optional[int] = None
    flight_ratio: Optional[int] = None
    climb_dis_descend: Optional[int] = None
    climb_dis_ascend_time: Optional[int] = None
    climb_dis_descend_time: Optional[int] = None
    child_list: Optional[str] = None
    parent_trackid: Optional[int] = None
    max_heart_rate: Optional[int] = None
    min_heart_rate: Optional[int] = None
    swolf: Optional[int] = None
    total_strokes: Optional[int] = None
    total_trips: Optional[int] = None
    avg_stroke_speed: Optional[float] = None
    max_stroke_speed: Optional[float] = None
    avg_distance_per_stroke: Optional[float] = None
    swim_pool_length: Optional[int] = None
    te: Optional[int] = None
    swim_style: Optional[int] = None
    unit: Optional[int] = None
    add_info: Optional[str] = None
    sport_mode: Optional[int] = None
    downhill_num: Optional[int] = None
    downhill_max_altitude_desend: Optional[int] = None
    strokes: Optional[int] = None
    fore_hand: Optional[int] = None
    back_hand: Optional[int] = None
    serve: Optional[int] = None
    second_half_start_time: Optional[int] = None
    pb: Optional[str] = None
    rope_skipping_count: Optional[int] = None
    rope_skipping_avg_frequency: Optional[int] = None
    rope_skipping_max_frequency: Optional[int] = None
    rope_skipping_rest_time: Optional[int] = None
    left_landing_time: Optional[int] = None
    left_flight_ratio: Optional[int] = None
    right_landing_time: Optional[int] = None
    right_flight_ratio: Optional[int] = None
    marathon: Optional[str] = None
    situps: Optional[int] = None
    anaerobic_te: Optional[int] = None
    target_type: Optional[int] = None
    target_value: Optional[str] = None
    total_group: Optional[int] = None
    spo2_max: Optional[int] = None
    spo2_min: Optional[int] = None
    avg_altitude: Optional[float] = None
    max_slope: Optional[int] = None
    avg_slope: Optional[int] = None
    avg_pulloar_time: Optional[float] = None
    avg_return_time: Optional[float] = None
    floor_number: Optional[int] = None
    upstairs_height: Optional[float] = None
    min_upstairs_floors: Optional[float] = None
    accumulated_gap: Optional[int] = None
    auto_recognition: Optional[int] = None
    app_name: str
    pause_time: Optional[str] = None
    heartrate_setting_type: Optional[int] = None


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
