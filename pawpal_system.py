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
    pets: list[Pet] = field(default_factory=list)

    def set_time_budget(self, minutes: int) -> None:
        """Update the owner's daily time budget."""
        if minutes < 0:
            raise ValueError("Time budget cannot be negative")
        self.daily_time_budget_minutes = minutes

    def set_preferences(self, preferences: list[str]) -> None:
        """Update the owner's preferred time blocks."""
        self.preferred_time_blocks = preferences

    def get_available_time_for_day(self) -> int:
        """Return the owner's available time in minutes."""
        return self.daily_time_budget_minutes
    
    def add_pet(self, pet: Pet) -> None:
        """Add a pet to the owner's list."""
        self.pets.append(pet)
    
    def get_all_tasks(self) -> list[CareTask]:
        """Retrieve all tasks across all pets."""
        all_tasks = []
        for pet in self.pets:
            all_tasks.extend(pet.tasks)
        return all_tasks
    
    def get_pet_by_id(self, pet_id: str) -> Pet | None:
        """Find a pet by ID."""
        for pet in self.pets:
            if pet.pet_id == pet_id:
                return pet
        return None


@dataclass
class Pet:
    pet_id: str
    name: str
    species: str
    age: int
    health_notes: str = ""
    tasks: list[CareTask] = field(default_factory=list)

    def update_pet_info(self, **updates: Any) -> None:
        """Update pet attributes dynamically."""
        for key, value in updates.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                raise AttributeError(f"Pet has no attribute '{key}'")

    def get_care_profile(self) -> dict[str, Any]:
        """Return a summary of the pet's profile and key tasks."""
        return {
            "pet_id": self.pet_id,
            "name": self.name,
            "species": self.species,
            "age": self.age,
            "health_notes": self.health_notes,
            "task_count": len(self.tasks),
            "mandatory_tasks": sum(1 for t in self.tasks if t.is_mandatory),
        }
    
    def add_task(self, task: CareTask) -> None:
        """Add a task to this pet's task list."""
        self.tasks.append(task)
    
    def get_task_by_id(self, task_id: str) -> CareTask | None:
        """Find a task by ID."""
        for task in self.tasks:
            if task.task_id == task_id:
                return task
        return None


@dataclass
class CareTask:
    task_id: str
    title: str
    category: str
    duration_minutes: int
    priority: str
    due_date: date | None = None
    due_window_start: time | None = None
    due_window_end: time | None = None
    is_mandatory: bool = False
    is_completed: bool = False

    def validate(self) -> bool:
        """Validate that the task has valid attributes."""
        if not self.title or len(self.title.strip()) == 0:
            raise ValueError("Task title cannot be empty")
        if self.duration_minutes <= 0:
            raise ValueError("Task duration must be positive")
        valid_priorities = {"low", "medium", "high"}
        if self.priority not in valid_priorities:
            raise ValueError(f"Priority must be one of {valid_priorities}")
        if self.due_window_start and self.due_window_end:
            if self.due_window_start >= self.due_window_end:
                raise ValueError("due_window_start must be before due_window_end")
        return True

    def is_due_on(self, target_date: date) -> bool:
        """Check if this task is due on a specific date."""
        if self.due_date is None:
            return False
        return self.due_date == target_date

    def mark_completed(self) -> None:
        """Mark this task as completed."""
        self.is_completed = True

    def update_task(self, **details: Any) -> None:
        """Update task attributes."""
        for key, value in details.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                raise AttributeError(f"CareTask has no attribute '{key}'")


@dataclass
class DailyPlan:
    date: date
    owner: Owner
    pet: Pet
    scheduled_items: list[tuple[CareTask, time, time]] = field(default_factory=list)
    unscheduled_tasks: list[CareTask] = field(default_factory=list)
    total_scheduled_minutes: int = 0
    reasoning_notes: list[str] = field(default_factory=list)

    def add_scheduled_item(self, task: CareTask, start_time: time, end_time: time) -> None:
        """Add a scheduled item, checking for time conflicts."""
        # Check for overlaps with existing scheduled items
        for scheduled_task, sched_start, sched_end in self.scheduled_items:
            if not (end_time <= sched_start or start_time >= sched_end):
                raise ValueError(
                    f"Time conflict: {task.title} ({start_time}-{end_time}) "
                    f"overlaps with {scheduled_task.title} ({sched_start}-{sched_end})"
                )
        self.scheduled_items.append((task, start_time, end_time))
        self.total_scheduled_minutes += task.duration_minutes

    def calculate_total_minutes(self) -> int:
        """Recalculate total scheduled minutes from scheduled items."""
        total = sum(task.duration_minutes for task, _, _ in self.scheduled_items)
        self.total_scheduled_minutes = total
        return total

    def summarize(self) -> str:
        """Generate a human-readable summary of the daily plan."""
        summary = f"Daily Plan for {self.pet.name} on {self.date}\n"
        summary += f"Owner: {self.owner.name}\n"
        summary += f"Total time allocated: {self.total_scheduled_minutes} minutes\n"
        summary += "\nScheduled Tasks:\n"
        
        for task, start, end in self.scheduled_items:
            summary += f"  • {start.strftime('%H:%M')}-{end.strftime('%H:%M')}: {task.title} ({task.duration_minutes} min, {task.priority})\n"
        
        if self.unscheduled_tasks:
            summary += f"\nUnscheduled ({len(self.unscheduled_tasks)} tasks):\n"
            for task in self.unscheduled_tasks:
                summary += f"  • {task.title} ({task.duration_minutes} min, {task.priority})\n"
        else:
            summary += "\nAll tasks scheduled!\n"
        
        if self.reasoning_notes:
            summary += "\nNotes:\n"
            for note in self.reasoning_notes:
                summary += f"  - {note}\n"
        
        return summary


class Scheduler:
    def __init__(self, ranking_strategy: str = "priority_first") -> None:
        """Initialize scheduler with a ranking strategy."""
        self.ranking_strategy = ranking_strategy

    def generate_plan(self, tasks: list[CareTask], available_minutes: int, owner: Owner, pet: Pet, plan_date: date) -> DailyPlan:
        """Generate a daily plan for a pet given available time and constraints."""
        # Filter tasks due on the given date
        due_tasks = [t for t in tasks if t.is_due_on(plan_date)]
        
        # Rank the tasks
        ranked = self.rank_tasks(due_tasks)
        
        # Schedule them into available time slots
        scheduled_items, unscheduled = self.schedule_tasks(ranked, available_minutes, owner)
        
        # Create and populate the plan
        plan = DailyPlan(
            date=plan_date,
            owner=owner,
            pet=pet,
        )
        
        # Add reasoning notes
        plan.reasoning_notes.append(
            f"Generated plan for {pet.name} on {plan_date}. "
            f"Available time: {available_minutes} min. "
            f"Tasks due: {len(due_tasks)}."
        )
        
        # Add scheduled items
        for task, start_time, end_time in scheduled_items:
            plan.add_scheduled_item(task, start_time, end_time)
        
        plan.unscheduled_tasks = unscheduled
        
        if unscheduled:
            plan.reasoning_notes.append(
                f"{len(unscheduled)} task(s) could not fit in available time."
            )
        
        return plan

    def rank_tasks(self, tasks: list[CareTask]) -> list[CareTask]:
        """Rank tasks by priority and mandatory status.
        
        Priority order:
        1. Mandatory tasks (highest priority first)
        2. High priority
        3. Medium priority
        4. Low priority
        """
        priority_order = {"high": 3, "medium": 2, "low": 1}
        
        def task_sort_key(task: CareTask) -> tuple:
            # Sort by: mandatory (True first), then priority (highest first), then duration (shorter first)
            priority_value = priority_order.get(task.priority, 0)
            return (not task.is_mandatory, -priority_value, task.duration_minutes)
        
        return sorted(tasks, key=task_sort_key)

    def schedule_tasks(
        self,
        ranked_tasks: list[CareTask],
        available_minutes: int,
        owner: Owner,
    ) -> tuple[list[tuple[CareTask, time, time]], list[CareTask]]:
        """Schedule ranked tasks into available time slots.
        
        Uses a greedy approach: fit tasks in priority order until time runs out.
        Respects owner's preferred time blocks if specified.
        """
        scheduled = []
        unscheduled = []
        remaining_minutes = available_minutes
        
        # Default time blocks: 9 AM to 5 PM if not specified
        if not owner.preferred_time_blocks:
            owner.preferred_time_blocks = ["morning", "afternoon"]
        
        # Start at 9 AM
        current_hour = 9
        current_minute = 0
        
        # Try to fit each task
        for task in ranked_tasks:
            if task.duration_minutes <= remaining_minutes:
                # Calculate start time
                start_time = time(current_hour, current_minute)
                
                # Calculate end time by adding duration
                total_minutes = current_hour * 60 + current_minute + task.duration_minutes
                end_hour = total_minutes // 60
                end_minute = total_minutes % 60
                
                # Ensure end time is valid (cap at 18:00 / 6 PM)
                if end_hour > 18:
                    unscheduled.append(task)
                    continue
                
                end_time = time(end_hour, end_minute)
                
                scheduled.append((task, start_time, end_time))
                remaining_minutes -= task.duration_minutes
                
                # Update current time for next task
                current_hour = end_hour
                current_minute = end_minute
            else:
                unscheduled.append(task)
        
        return scheduled, unscheduled

    def produce_unscheduled_list(self, tasks: list[CareTask], scheduled: list[CareTask]) -> list[CareTask]:
        """Return tasks that were not scheduled."""
        scheduled_ids = {t.task_id for t in scheduled}
        return [t for t in tasks if t.task_id not in scheduled_ids]
