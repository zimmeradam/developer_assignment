import time
from dataclasses import dataclass
from functools import lru_cache
from random import random
from typing import TypeAlias

AssetId: TypeAlias = str
PowerTarget: TypeAlias = int


class Clock:
    """
    Implements a clock that maps the time elapsed since start to an integer between 0 and the number_of_time_blocks.
    This loops around and is used to retrieve the scheduled power targets for the current time block.
    You can use the get_current_time_block() method for logging if needed.
    By default, each time block lasts 5 seconds.
    """

    @classmethod
    @lru_cache
    def get_instance(cls):
        # Feel free to adjust the number of time blocks for your liking
        return Clock(number_of_time_blocks=5)

    @classmethod
    def get_current_time_block(cls) -> int:
        return cls.get_instance()._get_current_time_block()

    def __init__(self, number_of_time_blocks: int, time_block_duration_seconds: int = 5):
        self._time_block_number = number_of_time_blocks
        self._time_block_duration_seconds = time_block_duration_seconds
        self._start_time = time.monotonic()

    def _get_current_time_block(self) -> int:
        elapsed = time.monotonic() - self._start_time
        time_blocks_since_start = int(elapsed / self._time_block_duration_seconds)
        return time_blocks_since_start % self._time_block_number


class ScheduleProvider:
    """
    Use this class to create a schedule provider with your schedule sample to test your application.
    A schedule consists of dictionaries with power targets for each asset. The assets are identified by an asset_id.
    Make sure the number of items provided matches the number of time blocks.

    Example usage:
    schedule_provider = ScheduleProvider([
        {'asset_1': 100, 'asset_2': 200, 'asset_3': 300},
        {'asset_1': 50, 'asset_2': 200, 'asset_3': 400},
        {'asset_1': 100, 'asset_2': 100, 'asset_3': 100},
        {'asset_1': 100, 'asset_2': 50, 'asset_3': 50},
        {'asset_1': 500, 'asset_2': 500, 'asset_3': 500},
    ])
    power_targets = schedule_provider.get_current_power_targets()
    """

    def __init__(
            self,
            schedule: list[dict[AssetId, PowerTarget]],
            # Feel free to adjust these parameters to test certain scenarios
            sleep_chance: float = 0.1,
            sleep_multiplier: float = 1.0,
            exception_chance: float = 0.0,
    ):
        self._sleep_chance = sleep_chance
        self._sleep_multiplier = sleep_multiplier
        self._exception_chance = exception_chance
        self._schedule = schedule

    def get_current_power_targets(self) -> dict[AssetId, PowerTarget]:
        if random() < self._sleep_chance:
            time.sleep(random() * self._sleep_multiplier)
        if random() < self._exception_chance:
            raise Exception('Could not get schedule')
        return self._schedule[Clock.get_current_time_block()]


@dataclass(frozen=True)
class DeviceStatus:
    current_power_output: int
    potential_power_output: int


class DeviceController:
    """
    An instance of this class represents the controller interface for a single asset.
    Create a controller for each asset so that the Energy Manager can use them.

    In part 2, the potential_power_outputs is used to tell the controller what the maximum available power production is
    """

    def __init__(
            self,
            asset_id: AssetId,
            potential_power_outputs: list[int] | None = None,
            # Feel free to adjust these parameters to test certain scenarios
            sleep_chance: float = 0.1,
            sleep_multiplier: float = 1.0,
            exception_chance: float = 0.0,
    ):
        self._asset_id = asset_id
        self._power_target = 0
        self._potential_power_outputs = potential_power_outputs
        self._sleep_chance = sleep_chance
        self._sleep_multiplier = sleep_multiplier
        self._exception_chance = exception_chance

    def set_power_target(self, power_target: PowerTarget):
        if random() < self._sleep_chance:
            time.sleep(random() * self._sleep_multiplier)
        if random() < self._exception_chance:
            raise Exception('Could not set power target')
        print(f'[{self._asset_id}] Power set: {power_target}')
        self._power_target = power_target

    def get_device_status(self) -> DeviceStatus:
        if random() < self._sleep_chance:
            time.sleep(random() * self._sleep_multiplier)
        if random() < self._exception_chance:
            raise Exception('Could not read device status')
        if self._potential_power_outputs:
            current_potential = self._potential_power_outputs[Clock.get_current_time_block()]
            return DeviceStatus(min(self._power_target, current_potential), current_potential)
        return DeviceStatus(self._power_target, 0)
