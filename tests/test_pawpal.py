"""
Simple test suite for PawPal+ core functionality.
"""

import pytest
from datetime import date
from pawpal_system import Pet, CareTask


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
