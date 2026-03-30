"""
Unit tests for the PawPal+ scheduling system.
Tests core functionality of Owner, Pet, CareTask, and Scheduler classes.
"""

import pytest
from datetime import date, time
from pawpal_system import Owner, Pet, CareTask, DailyPlan, Scheduler


class TestCareTask:
    """Test suite for CareTask class."""
    
    def test_create_valid_task(self):
        """Test creating a valid CareTask."""
        task = CareTask(
            task_id="task_1",
            title="Morning walk",
            category="exercise",
            duration_minutes=30,
            priority="high"
        )
        assert task.task_id == "task_1"
        assert task.title == "Morning walk"
        assert task.duration_minutes == 30
        assert task.priority == "high"
        assert task.is_completed is False
    
    def test_validate_task_valid(self):
        """Test validate() on a valid task."""
        task = CareTask(
            task_id="task_1",
            title="Feeding",
            category="feeding",
            duration_minutes=15,
            priority="medium"
        )
        assert task.validate() is True
    
    def test_validate_task_empty_title(self):
        """Test validate() rejects empty title."""
        task = CareTask(
            task_id="task_1",
            title="",
            category="feeding",
            duration_minutes=15,
            priority="medium"
        )
        with pytest.raises(ValueError, match="Task title cannot be empty"):
            task.validate()
    
    def test_validate_task_invalid_duration(self):
        """Test validate() rejects non-positive duration."""
        task = CareTask(
            task_id="task_1",
            title="Feeding",
            category="feeding",
            duration_minutes=0,
            priority="medium"
        )
        with pytest.raises(ValueError, match="Task duration must be positive"):
            task.validate()
    
    def test_validate_task_invalid_priority(self):
        """Test validate() rejects invalid priority."""
        task = CareTask(
            task_id="task_1",
            title="Feeding",
            category="feeding",
            duration_minutes=15,
            priority="urgent"
        )
        with pytest.raises(ValueError, match="Priority must be one of"):
            task.validate()
    
    def test_validate_task_invalid_time_window(self):
        """Test validate() rejects invalid time window."""
        task = CareTask(
            task_id="task_1",
            title="Feeding",
            category="feeding",
            duration_minutes=15,
            priority="medium",
            due_window_start=time(10, 0),
            due_window_end=time(9, 0)
        )
        with pytest.raises(ValueError, match="due_window_start must be before due_window_end"):
            task.validate()
    
    def test_is_due_on(self):
        """Test is_due_on() checks task due date."""
        today = date.today()
        task = CareTask(
            task_id="task_1",
            title="Feeding",
            category="feeding",
            duration_minutes=15,
            priority="high",
            due_date=today
        )
        assert task.is_due_on(today) is True
        assert task.is_due_on(date(2026, 1, 1)) is False
    
    def test_is_due_on_no_due_date(self):
        """Test is_due_on() returns False if no due date set."""
        task = CareTask(
            task_id="task_1",
            title="Feeding",
            category="feeding",
            duration_minutes=15,
            priority="high"
        )
        assert task.is_due_on(date.today()) is False
    
    def test_mark_completed(self):
        """Test mark_completed() sets is_completed flag."""
        task = CareTask(
            task_id="task_1",
            title="Feeding",
            category="feeding",
            duration_minutes=15,
            priority="high"
        )
        assert task.is_completed is False
        task.mark_completed()
        assert task.is_completed is True
    
    def test_update_task(self):
        """Test update_task() modifies attributes."""
        task = CareTask(
            task_id="task_1",
            title="Feeding",
            category="feeding",
            duration_minutes=15,
            priority="high"
        )
        task.update_task(duration_minutes=20, priority="medium")
        assert task.duration_minutes == 20
        assert task.priority == "medium"
    
    def test_update_task_invalid_attribute(self):
        """Test update_task() rejects nonexistent attribute."""
        task = CareTask(
            task_id="task_1",
            title="Feeding",
            category="feeding",
            duration_minutes=15,
            priority="high"
        )
        with pytest.raises(AttributeError):
            task.update_task(nonexistent_field="value")


class TestPet:
    """Test suite for Pet class."""
    
    def test_create_pet(self):
        """Test creating a Pet."""
        pet = Pet(
            pet_id="pet_1",
            name="Mochi",
            species="dog",
            age=3,
            health_notes="Active and healthy"
        )
        assert pet.name == "Mochi"
        assert pet.species == "dog"
        assert pet.age == 3
    
    def test_add_task_to_pet(self):
        """Test adding a task to a pet."""
        pet = Pet(pet_id="pet_1", name="Mochi", species="dog", age=3)
        task = CareTask(
            task_id="task_1",
            title="Feeding",
            category="feeding",
            duration_minutes=15,
            priority="high"
        )
        pet.add_task(task)
        assert len(pet.tasks) == 1
        assert pet.tasks[0].task_id == "task_1"
    
    def test_get_task_by_id(self):
        """Test retrieving a task by ID."""
        pet = Pet(pet_id="pet_1", name="Mochi", species="dog", age=3)
        task = CareTask(
            task_id="task_1",
            title="Feeding",
            category="feeding",
            duration_minutes=15,
            priority="high"
        )
        pet.add_task(task)
        found_task = pet.get_task_by_id("task_1")
        assert found_task is not None
        assert found_task.title == "Feeding"
    
    def test_get_task_by_id_not_found(self):
        """Test searching for nonexistent task returns None."""
        pet = Pet(pet_id="pet_1", name="Mochi", species="dog", age=3)
        found_task = pet.get_task_by_id("nonexistent")
        assert found_task is None
    
    def test_update_pet_info(self):
        """Test updating pet attributes."""
        pet = Pet(pet_id="pet_1", name="Mochi", species="dog", age=3)
        pet.update_pet_info(age=4, health_notes="Senior dog")
        assert pet.age == 4
        assert pet.health_notes == "Senior dog"
    
    def test_get_care_profile(self):
        """Test getting a care profile summary."""
        pet = Pet(pet_id="pet_1", name="Mochi", species="dog", age=3)
        task = CareTask(
            task_id="task_1",
            title="Feeding",
            category="feeding",
            duration_minutes=15,
            priority="high",
            is_mandatory=True
        )
        pet.add_task(task)
        profile = pet.get_care_profile()
        assert profile["name"] == "Mochi"
        assert profile["task_count"] == 1
        assert profile["mandatory_tasks"] == 1


class TestOwner:
    """Test suite for Owner class."""
    
    def test_create_owner(self):
        """Test creating an Owner."""
        owner = Owner(
            owner_id="owner_1",
            name="Jordan",
            daily_time_budget_minutes=180
        )
        assert owner.name == "Jordan"
        assert owner.daily_time_budget_minutes == 180
    
    def test_add_pet_to_owner(self):
        """Test adding a pet to an owner."""
        owner = Owner(owner_id="owner_1", name="Jordan", daily_time_budget_minutes=180)
        pet = Pet(pet_id="pet_1", name="Mochi", species="dog", age=3)
        owner.add_pet(pet)
        assert len(owner.pets) == 1
        assert owner.pets[0].name == "Mochi"
    
    def test_get_pet_by_id(self):
        """Test retrieving a pet by ID."""
        owner = Owner(owner_id="owner_1", name="Jordan", daily_time_budget_minutes=180)
        pet = Pet(pet_id="pet_1", name="Mochi", species="dog", age=3)
        owner.add_pet(pet)
        found_pet = owner.get_pet_by_id("pet_1")
        assert found_pet is not None
        assert found_pet.name == "Mochi"
    
    def test_get_all_tasks(self):
        """Test retrieving all tasks from all pets."""
        owner = Owner(owner_id="owner_1", name="Jordan", daily_time_budget_minutes=180)
        
        pet1 = Pet(pet_id="pet_1", name="Mochi", species="dog", age=3)
        pet2 = Pet(pet_id="pet_2", name="Bella", species="cat", age=5)
        
        task1 = CareTask(task_id="task_1", title="Walk", category="exercise", 
                        duration_minutes=30, priority="high")
        task2 = CareTask(task_id="task_2", title="Feeding", category="feeding",
                        duration_minutes=15, priority="high")
        
        pet1.add_task(task1)
        pet2.add_task(task2)
        owner.add_pet(pet1)
        owner.add_pet(pet2)
        
        all_tasks = owner.get_all_tasks()
        assert len(all_tasks) == 2
    
    def test_set_time_budget(self):
        """Test setting time budget."""
        owner = Owner(owner_id="owner_1", name="Jordan", daily_time_budget_minutes=180)
        owner.set_time_budget(240)
        assert owner.daily_time_budget_minutes == 240
    
    def test_set_time_budget_negative(self):
        """Test rejecting negative time budget."""
        owner = Owner(owner_id="owner_1", name="Jordan", daily_time_budget_minutes=180)
        with pytest.raises(ValueError, match="Time budget cannot be negative"):
            owner.set_time_budget(-10)
    
    def test_set_preferences(self):
        """Test setting owner preferences."""
        owner = Owner(owner_id="owner_1", name="Jordan", daily_time_budget_minutes=180)
        owner.set_preferences(["morning", "evening"])
        assert owner.preferred_time_blocks == ["morning", "evening"]


class TestScheduler:
    """Test suite for Scheduler class."""
    
    def test_rank_tasks_by_priority(self):
        """Test that tasks are ranked correctly by priority."""
        scheduler = Scheduler()
        
        low_task = CareTask(task_id="1", title="Play", category="enrichment",
                           duration_minutes=20, priority="low")
        high_task = CareTask(task_id="2", title="Walk", category="exercise",
                            duration_minutes=30, priority="high")
        med_task = CareTask(task_id="3", title="Feed", category="feeding",
                           duration_minutes=15, priority="medium")
        
        tasks = [low_task, high_task, med_task]
        ranked = scheduler.rank_tasks(tasks)
        
        # High priority should come first, then medium, then low
        assert ranked[0].priority == "high"
        assert ranked[1].priority == "medium"
        assert ranked[2].priority == "low"
    
    def test_rank_tasks_mandatory_first(self):
        """Test that mandatory tasks are ranked first."""
        scheduler = Scheduler()
        
        optional_high = CareTask(task_id="1", title="Play", category="enrichment",
                                duration_minutes=20, priority="high", is_mandatory=False)
        mandatory_low = CareTask(task_id="2", title="Meds", category="medical",
                                duration_minutes=5, priority="low", is_mandatory=True)
        
        tasks = [optional_high, mandatory_low]
        ranked = scheduler.rank_tasks(tasks)
        
        assert ranked[0].is_mandatory is True
        assert ranked[1].is_mandatory is False
    
    def test_generate_plan(self):
        """Test generating a daily plan."""
        owner = Owner(owner_id="owner_1", name="Jordan", daily_time_budget_minutes=120)
        pet = Pet(pet_id="pet_1", name="Mochi", species="dog", age=3)
        
        task = CareTask(task_id="task_1", title="Walk", category="exercise",
                       duration_minutes=30, priority="high", due_date=date.today())
        
        scheduler = Scheduler()
        plan = scheduler.generate_plan(
            tasks=[task],
            available_minutes=120,
            owner=owner,
            pet=pet,
            plan_date=date.today()
        )
        
        assert plan.date == date.today()
        assert plan.owner.name == "Jordan"
        assert plan.pet.name == "Mochi"
        assert len(plan.scheduled_items) > 0
    
    def test_generate_plan_filters_by_date(self):
        """Test that only tasks due on the plan date are scheduled."""
        owner = Owner(owner_id="owner_1", name="Jordan", daily_time_budget_minutes=120)
        pet = Pet(pet_id="pet_1", name="Mochi", species="dog", age=3)
        
        today = date.today()
        tomorrow = date(today.year, today.month, today.day + 1) if today.day < 28 else date(today.year, today.month + 1, 1)
        
        task_today = CareTask(task_id="task_1", title="Walk", category="exercise",
                             duration_minutes=30, priority="high", due_date=today)
        task_tomorrow = CareTask(task_id="task_2", title="Feed", category="feeding",
                                duration_minutes=15, priority="high", due_date=tomorrow)
        
        scheduler = Scheduler()
        plan = scheduler.generate_plan(
            tasks=[task_today, task_tomorrow],
            available_minutes=120,
            owner=owner,
            pet=pet,
            plan_date=today
        )
        
        # Only task_today should be scheduled or in unscheduled list for today
        all_task_ids = {t.task_id for t, _, _ in plan.scheduled_items} | {t.task_id for t in plan.unscheduled_tasks}
        assert "task_1" in all_task_ids
        assert "task_2" not in all_task_ids
    
    def test_schedule_respects_time_limits(self):
        """Test that scheduler respects available time."""
        owner = Owner(owner_id="owner_1", name="Jordan", daily_time_budget_minutes=30)
        pet = Pet(pet_id="pet_1", name="Mochi", species="dog", age=3)
        
        task1 = CareTask(task_id="1", title="Walk", category="exercise",
                        duration_minutes=20, priority="high", due_date=date.today())
        task2 = CareTask(task_id="2", title="Feed", category="feeding",
                        duration_minutes=20, priority="high", due_date=date.today())
        
        scheduler = Scheduler()
        plan = scheduler.generate_plan(
            tasks=[task1, task2],
            available_minutes=30,
            owner=owner,
            pet=pet,
            plan_date=date.today()
        )
        
        # Only one task should fit in 30 minutes
        assert len(plan.scheduled_items) == 1
        assert len(plan.unscheduled_tasks) == 1


class TestDailyPlan:
    """Test suite for DailyPlan class."""
    
    def test_create_daily_plan(self):
        """Test creating a DailyPlan."""
        owner = Owner(owner_id="owner_1", name="Jordan", daily_time_budget_minutes=180)
        pet = Pet(pet_id="pet_1", name="Mochi", species="dog", age=3)
        
        plan = DailyPlan(date=date.today(), owner=owner, pet=pet)
        assert plan.date == date.today()
        assert plan.owner.name == "Jordan"
        assert plan.pet.name == "Mochi"
    
    def test_add_scheduled_item(self):
        """Test adding a scheduled item to a plan."""
        owner = Owner(owner_id="owner_1", name="Jordan", daily_time_budget_minutes=180)
        pet = Pet(pet_id="pet_1", name="Mochi", species="dog", age=3)
        plan = DailyPlan(date=date.today(), owner=owner, pet=pet)
        
        task = CareTask(task_id="task_1", title="Walk", category="exercise",
                       duration_minutes=30, priority="high")
        
        plan.add_scheduled_item(task, time(9, 0), time(9, 30))
        assert len(plan.scheduled_items) == 1
        assert plan.total_scheduled_minutes == 30
    
    def test_add_scheduled_item_overlap_detection(self):
        """Test that overlapping items raise an error."""
        owner = Owner(owner_id="owner_1", name="Jordan", daily_time_budget_minutes=180)
        pet = Pet(pet_id="pet_1", name="Mochi", species="dog", age=3)
        plan = DailyPlan(date=date.today(), owner=owner, pet=pet)
        
        task1 = CareTask(task_id="task_1", title="Walk", category="exercise",
                        duration_minutes=30, priority="high")
        task2 = CareTask(task_id="task_2", title="Feed", category="feeding",
                        duration_minutes=15, priority="high")
        
        plan.add_scheduled_item(task1, time(9, 0), time(9, 30))
        
        # Try to add overlapping task
        with pytest.raises(ValueError, match="Time conflict"):
            plan.add_scheduled_item(task2, time(9, 15), time(9, 30))
    
    def test_calculate_total_minutes(self):
        """Test calculating total scheduled minutes."""
        owner = Owner(owner_id="owner_1", name="Jordan", daily_time_budget_minutes=180)
        pet = Pet(pet_id="pet_1", name="Mochi", species="dog", age=3)
        plan = DailyPlan(date=date.today(), owner=owner, pet=pet)
        
        task1 = CareTask(task_id="1", title="Walk", category="exercise",
                        duration_minutes=30, priority="high")
        task2 = CareTask(task_id="2", title="Feed", category="feeding",
                        duration_minutes=15, priority="high")
        
        plan.add_scheduled_item(task1, time(9, 0), time(9, 30))
        plan.add_scheduled_item(task2, time(9, 30), time(9, 45))
        
        total = plan.calculate_total_minutes()
        assert total == 45
    
    def test_summarize_plan(self):
        """Test generating a plan summary."""
        owner = Owner(owner_id="owner_1", name="Jordan", daily_time_budget_minutes=180)
        pet = Pet(pet_id="pet_1", name="Mochi", species="dog", age=3)
        plan = DailyPlan(date=date.today(), owner=owner, pet=pet)
        
        task = CareTask(task_id="task_1", title="Walk", category="exercise",
                       duration_minutes=30, priority="high")
        
        plan.add_scheduled_item(task, time(9, 0), time(9, 30))
        plan.reasoning_notes.append("Test note")
        
        summary = plan.summarize()
        assert "Mochi" in summary
        assert "Jordan" in summary
        assert "Walk" in summary
        assert "30 minutes" in summary or "09:00" in summary


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
