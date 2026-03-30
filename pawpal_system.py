from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, time
from typing import Any


@dataclass
class Owner:
    owner_id: str
    name: str
    daily_time_budget_minutes: int
    preferred_time_blocks: list[str] = field(default_factory=list)

    def set_time_budget(self, minutes: int) -> None:
        pass

    def set_preferences(self, preferences: list[str]) -> None:
        pass

    def get_available_time_for_day(self) -> int:
        pass


@dataclass
class Pet:
    pet_id: str
    name: str
    species: str
    age: int
    health_notes: str = ""

    def update_pet_info(self, **updates: Any) -> None:
        pass

    def get_care_profile(self) -> dict[str, Any]:
        pass


@dataclass
class CareTask:
    task_id: str
    title: str
    category: str
    duration_minutes: int
    priority: str
    due_window_start: time | None = None
    due_window_end: time | None = None
    is_mandatory: bool = False
    is_completed: bool = False

    def validate(self) -> bool:
        pass

    def is_due_on(self, target_date: date) -> bool:
        pass

    def mark_completed(self) -> None:
        pass

    def update_task(self, **details: Any) -> None:
        pass


@dataclass
class DailyPlan:
    date: date
    scheduled_items: list[tuple[CareTask, time, time]] = field(default_factory=list)
    unscheduled_tasks: list[CareTask] = field(default_factory=list)
    total_scheduled_minutes: int = 0
    reasoning_notes: list[str] = field(default_factory=list)

    def add_scheduled_item(self, task: CareTask, start_time: time, end_time: time) -> None:
        pass

    def calculate_total_minutes(self) -> int:
        pass

    def summarize(self) -> str:
        pass


class Scheduler:
    def __init__(self, ranking_strategy: str = "priority_first") -> None:
        self.ranking_strategy = ranking_strategy

    def generate_plan(self, tasks: list[CareTask], available_minutes: int) -> DailyPlan:
        pass

    def rank_tasks(self, tasks: list[CareTask]) -> list[CareTask]:
        pass

    def schedule_tasks(
        self,
        ranked_tasks: list[CareTask],
        available_minutes: int,
    ) -> tuple[list[tuple[CareTask, time, time]], list[CareTask]]:
        pass

    def produce_unscheduled_list(self, tasks: list[CareTask], scheduled: list[CareTask]) -> list[CareTask]:
        pass
