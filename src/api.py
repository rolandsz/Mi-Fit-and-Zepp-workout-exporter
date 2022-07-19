from typing import Any, Dict, List, Optional
from urllib.parse import urljoin

import requests
from pydantic import BaseModel


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
    max_pace: float
    min_pace: float
    version: int
    altitude_ascend: int
    altitude_descend: int
    total_step: int
    avg_stride_length: int
    max_frequency: int
    max_altitude: int
    min_altitude: int
    lap_distance: int
    sync_to: str
    distance_ascend: int
    max_cadence: int
    avg_cadence: int
    landing_time: int
    flight_ratio: int
    climb_dis_descend: int
    climb_dis_ascend_time: int
    climb_dis_descend_time: int
    child_list: str
    parent_trackid: int
    max_heart_rate: int
    min_heart_rate: int
    swolf: int
    total_strokes: int
    total_trips: int
    avg_stroke_speed: float
    max_stroke_speed: float
    avg_distance_per_stroke: float
    swim_pool_length: int
    te: int
    swim_style: int
    unit: int
    add_info: str
    sport_mode: int
    downhill_num: int
    downhill_max_altitude_desend: int
    strokes: int
    fore_hand: int
    back_hand: int
    serve: int
    second_half_start_time: int
    pb: Optional[str]
    rope_skipping_count: int
    rope_skipping_avg_frequency: int
    rope_skipping_max_frequency: int
    rope_skipping_rest_time: int
    left_landing_time: int
    left_flight_ratio: int
    right_landing_time: int
    right_flight_ratio: int
    marathon: Optional[str]
    situps: int
    anaerobic_te: int
    target_type: int
    target_value: str
    total_group: int
    spo2_max: int
    spo2_min: int
    avg_altitude: float
    max_slope: int
    avg_slope: int
    avg_pulloar_time: float
    avg_return_time: float
    floor_number: int
    upstairs_height: float
    min_upstairs_floors: float
    accumulated_gap: int
    auto_recognition: int
    app_name: str
    pause_time: Optional[str]
    heartrate_setting_type: int


class WorkoutHistoryData(BaseModel):
    next: Optional[int] = None
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
    APP_NAME = "com.xiaomi.hm.health"
    APP_PLATFORM = "web"

    def __init__(self, endpoint: str, token: str):
        self.base_url: str = endpoint
        self.token: str = token

    def get_workout_history(self) -> WorkoutHistory:
        response = self._do_request(endpoint="/v1/sport/run/history.json", params={})
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
                "appPlatform": Api.APP_PLATFORM,
                "appname": Api.APP_NAME,
            },
            params=params,
        )
        response.raise_for_status()
        return response.json()
