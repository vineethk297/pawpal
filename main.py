"""
Main script to demonstrate PawPal+ scheduling system.
Creates sample owner, pets, and tasks, then generates and displays a daily schedule.
"""

from datetime import date, time
from pawpal_system import Owner, Pet, CareTask, Scheduler


def main():
    print("=" * 60)
    print("PawPal+ Daily Scheduler Demo")
    print("=" * 60)
    print()
    
    # Create an Owner
    owner = Owner(
        owner_id="owner_1",
        name="Jordan",
        daily_time_budget_minutes=180,  # 3 hours available
        preferred_time_blocks=["morning", "afternoon"]
    )
    print(f"✓ Created owner: {owner.name} (available time: {owner.daily_time_budget_minutes} min)")
    print()
    
    # Create Pets
    mochi = Pet(
        pet_id="pet_1",
        name="Mochi",
        species="dog",
        age=3,
        health_notes="Needs daily walks and playtime"
    )
    
    bella = Pet(
        pet_id="pet_2",
        name="Bella",
        species="cat",
        age=5,
        health_notes="Prefers quiet time in mornings"
    )
    
    owner.add_pet(mochi)
    owner.add_pet(bella)
    print(f"✓ Created pets: {mochi.name} (dog) and {bella.name} (cat)")
    print()
    
    # Create Tasks for Mochi (adding OUT OF ORDER)
    task_3 = CareTask(
        task_id="task_3",
        title="Playtime",
        category="enrichment",
        duration_minutes=20,
        priority="medium",
        due_date=date.today(),
        due_window_start=time(14, 0),
        due_window_end=time(17, 0),
        is_mandatory=False,
        frequency="one-time"
    )
    
    task_1 = CareTask(
        task_id="task_1",
        title="Morning walk",
        category="exercise",
        duration_minutes=30,
        priority="high",
        due_date=date.today(),
        due_window_start=time(8, 0),
        due_window_end=time(10, 0),
        is_mandatory=True,
        frequency="daily"
    )
    
    task_2 = CareTask(
        task_id="task_2",
        title="Feeding",
        category="feeding",
        duration_minutes=15,
        priority="high",
        due_date=date.today(),
        due_window_start=time(7, 0),
        due_window_end=time(18, 0),
        is_mandatory=True,
        frequency="daily"
    )
    
    mochi.add_task(task_3)  # Added first (14:00)
    mochi.add_task(task_1)  # Added second (8:00)
    mochi.add_task(task_2)  # Added third (7:00)
    print(f"✓ Added 3 tasks to {mochi.name} (OUT OF ORDER):")
    print(f"  • {task_3.title} ({task_3.due_window_start} - {task_3.due_window_end}) [one-time]")
    print(f"  • {task_1.title} ({task_1.due_window_start} - {task_1.due_window_end}) [daily]")
    print(f"  • {task_2.title} ({task_2.due_window_start} - {task_2.due_window_end}) [daily]")
    print()
    
    # Create Tasks for Bella (adding OUT OF ORDER)
    task_6 = CareTask(
        task_id="task_6",
        title="Interactive play",
        category="enrichment",
        duration_minutes=15,
        priority="medium",
        due_date=date.today(),
        due_window_start=time(17, 0),
        due_window_end=time(19, 0),
        is_mandatory=False,
        frequency="one-time"
    )
    
    task_4 = CareTask(
        task_id="task_4",
        title="Feeding",
        category="feeding",
        duration_minutes=10,
        priority="high",
        due_date=date.today(),
        due_window_start=time(7, 0),
        due_window_end=time(20, 0),
        is_mandatory=True,
        frequency="weekly"  # Weekly recurrence
    )
    
    task_5 = CareTask(
        task_id="task_5",
        title="Litter box cleaning",
        category="hygiene",
        duration_minutes=5,
        priority="high",
        due_date=date.today(),
        due_window_start=time(9, 0),
        due_window_end=time(17, 0),
        is_mandatory=True,
        frequency="daily"  # Daily recurrence
    )
    
    bella.add_task(task_6)  # Added first (17:00)
    bella.add_task(task_4)  # Added second (7:00)
    bella.add_task(task_5)  # Added third (9:00)
    print(f"✓ Added 3 tasks to {bella.name} (OUT OF ORDER):")
    print(f"  • {task_6.title} ({task_6.due_window_start} - {task_6.due_window_end})")
    print(f"  • {task_4.title} ({task_4.due_window_start} - {task_4.due_window_end})")
    print(f"  • {task_5.title} ({task_5.due_window_start} - {task_5.due_window_end})")
    print()
    
    # Get all tasks
    all_tasks = owner.get_all_tasks()
    print(f"✓ Total tasks across all pets: {len(all_tasks)}")
    print()
    
    # Mark some tasks as completed for demonstration
    task_1.mark_completed()
    task_5.mark_completed()
    print("✓ Marked some tasks as completed")
    print()
    
    # Create scheduler
    scheduler = Scheduler(ranking_strategy="priority_first")
    
    print("=" * 60)
    print("SORTING AND FILTERING DEMONSTRATIONS")
    print("=" * 60)
    print()
    
    # DEMO 1: Sort tasks by time
    print("📅 DEMO 1: Tasks sorted by time window (earliest first)")
    print("-" * 60)
    mochi_tasks_unsorted = mochi.tasks
    print(f"Mochi tasks (as added - OUT OF ORDER):")
    for task in mochi_tasks_unsorted:
        window = f"{task.due_window_start}-{task.due_window_end}" if task.due_window_start else "No window"
        print(f"  • {task.title:20s} {window}")
    
    mochi_tasks_sorted = scheduler.sort_by_time(mochi_tasks_unsorted)
    print(f"\nMochi tasks (SORTED by time):")
    for task in mochi_tasks_sorted:
        window = f"{task.due_window_start}-{task.due_window_end}" if task.due_window_start else "No window"
        print(f"  • {task.title:20s} {window}")
    print()
    
    # DEMO 2: Filter by pet name
    print("🐾 DEMO 2: Filter tasks by pet name")
    print("-" * 60)
    mochi_only = owner.filter_tasks_by_pet_name("Mochi")
    bella_only = owner.filter_tasks_by_pet_name("Bella")
    print(f"Tasks for Mochi: {len(mochi_only)} tasks")
    for task in mochi_only:
        print(f"  • {task.title}")
    print(f"\nTasks for Bella: {len(bella_only)} tasks")
    for task in bella_only:
        print(f"  • {task.title}")
    print()
    
    # DEMO 3: Filter by completion status
    print("✅ DEMO 3: Filter tasks by completion status")
    print("-" * 60)
    completed_tasks = owner.filter_tasks_by_completion(completed=True)
    incomplete_tasks = owner.filter_tasks_by_completion(completed=False)
    print(f"Completed tasks ({len(completed_tasks)}):")
    for task in completed_tasks:
        print(f"  • {task.title} (from {task.task_id})")
    print(f"\nIncomplete tasks ({len(incomplete_tasks)}):")
    for task in incomplete_tasks:
        print(f"  • {task.title} (from {task.task_id})")
    print()
    
    # DEMO 4: Combined filtering
    print("🔍 DEMO 4: Combined filter (Mochi's incomplete tasks)")
    print("-" * 60)
    mochi_incomplete = owner.filter_tasks(pet_name="Mochi", completed=False)
    print(f"Found {len(mochi_incomplete)} incomplete tasks for Mochi:")
    for task in mochi_incomplete:
        print(f"  • {task.title}")
    print()
    
    # DEMO 5: Sort time strings
    print("⏰ DEMO 5: Sort time strings in HH:MM format")
    print("-" * 60)
    time_strings = ['14:30', '09:15', '18:00', '12:45', '07:00', '17:00']
    print(f"Unsorted times: {time_strings}")
    sorted_times = scheduler.sort_time_strings(time_strings)
    print(f"Sorted times:   {sorted_times}")
    print()
    
    print("=" * 60)
    print("TODAY'S SCHEDULES")
    print("=" * 60)
    print()
    
    # Generate plan for Mochi
    mochi_tasks = mochi.tasks
    mochi_plan = scheduler.generate_plan(
        tasks=mochi_tasks,
        available_minutes=owner.daily_time_budget_minutes,
        owner=owner,
        pet=mochi,
        plan_date=date.today()
    )
    print(mochi_plan.summarize())
    print()
    
    # Generate plan for Bella
    bella_tasks = bella.tasks
    bella_plan = scheduler.generate_plan(
        tasks=bella_tasks,
        available_minutes=owner.daily_time_budget_minutes,
        owner=owner,
        pet=bella,
        plan_date=date.today()
    )
    print(bella_plan.summarize())
    print()
    
    # DEMO 6: Detect conflicts in schedules (lightweight conflict detection)
    print("=" * 60)
    print("🔍 CONFLICT DETECTION - Check both schedules")
    print("=" * 60)
    print()
    
    # Check for conflicts in each pet's schedule
    mochi_conflicts = scheduler.detect_conflicts(mochi_plan.scheduled_items)
    bella_conflicts = scheduler.detect_conflicts(bella_plan.scheduled_items)
    
    print(f"Checking {mochi.name}'s schedule...")
    if mochi_conflicts:
        print(f"  ❌ {len(mochi_conflicts)} conflict(s) found:")
        for warning in mochi_conflicts:
            print(f"     {warning}")
    else:
        print(f"  ✅ No conflicts - schedule is clean!")
    print()
    
    print(f"Checking {bella.name}'s schedule...")
    if bella_conflicts:
        print(f"  ❌ {len(bella_conflicts)} conflict(s) found:")
        for warning in bella_conflicts:
            print(f"     {warning}")
    else:
        print(f"  ✅ No conflicts - schedule is clean!")
    print()
    
    print("=" * 60)
    print("Schedule generation complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
