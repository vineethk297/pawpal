"""
Simple test suite for PawPal+ core functionality.
"""

import pytest
import sys
from pathlib import Path
from datetime import date, time, timedelta

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pawpal_system import Owner, Pet, CareTask, Scheduler


class TestCareTask:
    """Tests for CareTask class."""
    
    def test_task_completion(self):
        """Verify that calling mark_completed() changes the task's completion status."""
        task = CareTask(
            task_id="task_1",
            title="Morning walk",
            category="exercise",
            duration_minutes=30,
            priority="high"
        )
        
        # Initially, task should not be completed
        assert task.is_completed is False
        
        # After marking complete, status should be True
        task.mark_completed()
        assert task.is_completed is True


class TestPet:
    """Tests for Pet class."""
    
    def test_task_addition(self):
        """Verify that adding a task to a Pet increases that pet's task count."""
        pet = Pet(
            pet_id="pet_1",
            name="Mochi",
            species="dog",
            age=3
        )
        
        # Initially, pet should have no tasks
        assert len(pet.tasks) == 0
        
        # Add a task
        task = CareTask(
            task_id="task_1",
            title="Morning walk",
            category="exercise",
            duration_minutes=30,
            priority="high"
        )
        pet.add_task(task)
        
        # After adding, task count should be 1
        assert len(pet.tasks) == 1


class TestSchedulerFeatures:
    """Tests for sorting, recurrence, and conflict detection behaviors."""

    def test_sort_by_time_returns_chronological_order(self):
        """Verify tasks are sorted by due_window_start from earliest to latest."""
        scheduler = Scheduler()
        tasks = [
            CareTask(
                task_id="task_evening",
                title="Evening Play",
                category="enrichment",
                duration_minutes=20,
                priority="low",
                due_window_start=time(18, 0),
            ),
            CareTask(
                task_id="task_morning",
                title="Morning Walk",
                category="exercise",
                duration_minutes=30,
                priority="high",
                due_window_start=time(8, 0),
            ),
            CareTask(
                task_id="task_midday",
                title="Lunch Feeding",
                category="feeding",
                duration_minutes=15,
                priority="high",
                due_window_start=time(12, 0),
            ),
        ]

        sorted_tasks = scheduler.sort_by_time(tasks)
        sorted_ids = [task.task_id for task in sorted_tasks]

        assert sorted_ids == ["task_morning", "task_midday", "task_evening"]

    def test_mark_daily_task_complete_creates_next_day_task(self):
        """Confirm completing a daily task creates a new task due the following day."""
        pet = Pet(
            pet_id="pet_1",
            name="Mochi",
            species="dog",
            age=3,
        )
        today = date(2026, 3, 29)
        daily_task = CareTask(
            task_id="feed_daily",
            title="Daily Feeding",
            category="feeding",
            duration_minutes=15,
            priority="high",
            due_date=today,
            frequency="daily",
        )
        pet.add_task(daily_task)

        next_task = daily_task.mark_completed_recurring(pet)

        assert daily_task.is_completed is True
        assert next_task is not None
        assert next_task.due_date == today + timedelta(days=1)
        assert next_task.is_completed is False
        assert next_task in pet.tasks
        assert len(pet.tasks) == 2

    def test_detect_conflicts_flags_duplicate_times(self):
        """Verify conflict detection reports duplicate/overlapping time slots."""
        scheduler = Scheduler()
        task_a = CareTask(
            task_id="task_a",
            title="Morning Walk",
            category="exercise",
            duration_minutes=30,
            priority="high",
        )
        task_b = CareTask(
            task_id="task_b",
            title="Morning Feeding",
            category="feeding",
            duration_minutes=15,
            priority="high",
        )

        scheduled_items = [
            (task_a, time(9, 0), time(9, 30)),
            (task_b, time(9, 0), time(9, 30)),
        ]

        conflicts = scheduler.detect_conflicts(scheduled_items)

        assert len(conflicts) == 1
        assert "TIME CONFLICT DETECTED" in conflicts[0]
        assert "Morning Walk" in conflicts[0]
        assert "Morning Feeding" in conflicts[0]
