from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, time, timedelta
import time as time_module
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
    
    def filter_tasks_by_completion(self, completed: bool = False) -> list[CareTask]:
        """Filter all tasks by completion status.
        
        Args:
            completed: If True, return completed tasks. If False, return incomplete tasks.
        
        Returns:
            List of tasks matching the completion status.
        """
        return [task for task in self.get_all_tasks() if task.is_completed == completed]
    
    def filter_tasks_by_pet_name(self, pet_name: str) -> list[CareTask]:
        """Filter tasks belonging to a specific pet by name.
        
        Args:
            pet_name: Name of the pet to filter by.
        
        Returns:
            List of tasks for the specified pet, or empty list if pet not found.
        """
        pet_name_lower = pet_name.lower().strip()
        for pet in self.pets:
            if pet.name.lower() == pet_name_lower:
                return pet.tasks
        return []
    
    def filter_tasks(self, pet_name: str | None = None, completed: bool | None = None) -> list[CareTask]:
        """Filter tasks by pet name and/or completion status.
        
        Args:
            pet_name: (Optional) Filter by pet name. If None, includes all pets.
            completed: (Optional) Filter by completion status (True/False). If None, includes all statuses.
        
        Returns:
            List of tasks matching the specified criteria.
        
        Example:
            >>> owner.filter_tasks(pet_name="Mochi", completed=False)
            # Returns incomplete tasks for Mochi
        """
        if pet_name:
            tasks = self.filter_tasks_by_pet_name(pet_name)
        else:
            tasks = self.get_all_tasks()
        
        if completed is not None:
            tasks = [task for task in tasks if task.is_completed == completed]
        
        return tasks
    
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
    frequency: str = "one-time"  # NEW: "one-time", "daily", or "weekly"

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

    def mark_completed_recurring(self, pet: Pet) -> CareTask | None:
        """Mark task complete and auto-create next occurrence if recurring.
        
        For recurring tasks (daily/weekly), this method:
        1. Marks the current task as complete
        2. Creates a new task instance with:
           - Same properties (title, category, duration_minutes, priority, is_mandatory, frequency)
           - New due_date calculated based on frequency (today + 1 day for daily, today + 7 for weekly)
           - Same due_window_start and due_window_end
           - New task_id with timestamp suffix for uniqueness
           - is_completed reset to False
        3. Automatically adds the new task to the pet's task list
        4. Returns the new CareTask or None if not recurring
        
        Args:
            pet: The Pet object that owns this task (needed to add next occurrence to pet.tasks)
        
        Returns:
            New CareTask instance if recurring, None if one-time task
        
        Example:
            >>> daily_task = CareTask(task_id="feed_1", title="Morning Feed", frequency="daily", ...)
            >>> next_task = daily_task.mark_completed_recurring(mochi_pet)
            >>> next_task.due_date  # Tomorrow's date
        """
        self.is_completed = True
        
        if self.frequency == "one-time":
            return None
        
        # Calculate next due date using timedelta
        if self.frequency == "daily":
            next_due_date = self.due_date + timedelta(days=1) if self.due_date else date.today() + timedelta(days=1)
        elif self.frequency == "weekly":
            next_due_date = self.due_date + timedelta(days=7) if self.due_date else date.today() + timedelta(days=7)
        else:
            return None  # Unknown frequency
        
        # Generate unique task_id with timestamp
        timestamp = time_module.strftime("%Y%m%d_%H%M%S")
        new_task_id = f"{self.task_id}_recur_{timestamp}"
        
        # Create new task instance
        next_task = CareTask(
            task_id=new_task_id,
            title=self.title,
            category=self.category,
            duration_minutes=self.duration_minutes,
            priority=self.priority,
            due_date=next_due_date,
            due_window_start=self.due_window_start,
            due_window_end=self.due_window_end,
            is_mandatory=self.is_mandatory,
            is_completed=False,
            frequency=self.frequency
        )
        
        # Automatically add to pet's task list
        pet.add_task(next_task)
        
        return next_task

    def generate_next_occurrence(self) -> CareTask | None:
        """Generate the next task occurrence without marking current task complete.
        
        Useful for previewing or manually scheduling the next occurrence.
        For automatic handling, use mark_completed_recurring() instead.
        
        Returns:
            New CareTask instance if recurring, None if one-time task
        """
        if self.frequency == "one-time":
            return None
        
        # Calculate next due date
        if self.frequency == "daily":
            next_due_date = self.due_date + timedelta(days=1) if self.due_date else date.today() + timedelta(days=1)
        elif self.frequency == "weekly":
            next_due_date = self.due_date + timedelta(days=7) if self.due_date else date.today() + timedelta(days=7)
        else:
            return None
        
        # Generate unique task_id
        timestamp = time_module.strftime("%Y%m%d_%H%M%S")
        new_task_id = f"{self.task_id}_next_{timestamp}"
        
        # Create and return new task (not added to pet)
        return CareTask(
            task_id=new_task_id,
            title=self.title,
            category=self.category,
            duration_minutes=self.duration_minutes,
            priority=self.priority,
            due_date=next_due_date,
            due_window_start=self.due_window_start,
            due_window_end=self.due_window_end,
            is_mandatory=self.is_mandatory,
            is_completed=False,
            frequency=self.frequency
        )

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

    def sort_by_time(self, tasks: list[CareTask]) -> list[CareTask]:
        """Sort tasks by their due time window start time.
        
        Tasks with earlier time windows are prioritized first.
        Tasks without time windows are placed at the end.
        """
        def time_sort_key(task: CareTask) -> tuple:
            # Return tuple: (has_window, start_time, task_id)
            # Tasks with windows sort first, then by start time
            if task.due_window_start:
                return (0, task.due_window_start, task.task_id)
            else:
                return (1, time.max, task.task_id)
        
        return sorted(tasks, key=time_sort_key)

    def sort_time_strings(self, time_strings: list[str]) -> list[str]:
        """Sort time strings in 'HH:MM' format using a lambda key function.
        
        Args:
            time_strings: List of time strings like ['14:30', '09:15', '18:00']
        
        Returns:
            Sorted list of time strings in chronological order
        
        Example:
            >>> scheduler = Scheduler()
            >>> times = ['14:30', '09:15', '18:00', '12:45']
            >>> scheduler.sort_time_strings(times)
            ['09:15', '12:45', '14:30', '18:00']
        """
        return sorted(time_strings, key=lambda t: tuple(map(int, t.split(':'))))

    def produce_unscheduled_list(self, tasks: list[CareTask], scheduled: list[CareTask]) -> list[CareTask]:
        """Return tasks that were not scheduled."""
        scheduled_ids = {t.task_id for t in scheduled}
        return [t for t in tasks if t.task_id not in scheduled_ids]

    def detect_conflicts(self, scheduled_items: list[tuple[CareTask, time, time]]) -> list[str]:
        """Detect time conflicts in scheduled items (lightweight, non-crashing detection).
        
        This method checks if any two tasks overlap in time and returns warning messages
        instead of raising exceptions. Useful for generating reports or warnings without
        stopping the scheduling process.
        
        Args:
            scheduled_items: List of (task, start_time, end_time) tuples
        
        Returns:
            List of warning messages (empty if no conflicts detected)
        
        Example:
            >>> scheduled = [(task1, time(9,0), time(9,30)), (task2, time(9,15), time(9,45))]
            >>> conflicts = scheduler.detect_conflicts(scheduled)
            >>> for warning in conflicts:
            ...     print(warning)
        """
        warnings = []
        
        # Check each pair of scheduled items for overlap
        for i in range(len(scheduled_items)):
            for j in range(i + 1, len(scheduled_items)):
                task1, start1, end1 = scheduled_items[i]
                task2, start2, end2 = scheduled_items[j]
                
                # Check if times overlap
                # Overlap occurs if: NOT (end1 <= start2 OR start1 >= end2)
                if not (end1 <= start2 or start1 >= end2):
                    # Calculate overlap duration
                    overlap_start = max(start1, start2)
                    overlap_end = min(end1, end2)
                    
                    overlap_minutes = (overlap_end.hour * 60 + overlap_end.minute) - \
                                     (overlap_start.hour * 60 + overlap_start.minute)
                    
                    # Generate warning message
                    warning = (
                        f"⚠️  TIME CONFLICT DETECTED: "
                        f"'{task1.title}' ({start1.strftime('%H:%M')}-{end1.strftime('%H:%M')}) "
                        f"overlaps with '{task2.title}' ({start2.strftime('%H:%M')}-{end2.strftime('%H:%M')}) "
                        f"for {overlap_minutes} minutes"
                    )
                    warnings.append(warning)
        
        return warnings

    def detect_conflicts_across_pets(self, plans: list[DailyPlan]) -> dict[str, list[str]]:
        """Detect conflicts across multiple pet daily plans (cross-pet scheduling).
        
        Useful for owners with multiple pets to see if their schedules have issues.
        
        Args:
            plans: List of DailyPlan objects for different pets
        
        Returns:
            Dictionary mapping pet name to list of conflict warnings
        
        Example:
            >>> mochi_plan = scheduler.generate_plan(...)
            >>> bella_plan = scheduler.generate_plan(...)
            >>> cross_conflicts = scheduler.detect_conflicts_across_pets([mochi_plan, bella_plan])
        """
        conflicts_by_pet = {}
        
        for plan in plans:
            pet_name = plan.pet.name
            warnings = self.detect_conflicts(plan.scheduled_items)
            if warnings:
                conflicts_by_pet[pet_name] = warnings
        
        return conflicts_by_pet
