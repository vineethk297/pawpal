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
    
    # Create Tasks for Mochi
    task_1 = CareTask(
        task_id="task_1",
        title="Morning walk",
        category="exercise",
        duration_minutes=30,
        priority="high",
        due_date=date.today(),
        due_window_start=time(8, 0),
        due_window_end=time(10, 0),
        is_mandatory=True
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
        is_mandatory=True
    )
    
    task_3 = CareTask(
        task_id="task_3",
        title="Playtime",
        category="enrichment",
        duration_minutes=20,
        priority="medium",
        due_date=date.today(),
        due_window_start=time(14, 0),
        due_window_end=time(17, 0),
        is_mandatory=False
    )
    
    mochi.add_task(task_1)
    mochi.add_task(task_2)
    mochi.add_task(task_3)
    print(f"✓ Added 3 tasks to {mochi.name}:")
    print(f"  • {task_1.title} ({task_1.duration_minutes} min, {task_1.priority})")
    print(f"  • {task_2.title} ({task_2.duration_minutes} min, {task_2.priority})")
    print(f"  • {task_3.title} ({task_3.duration_minutes} min, {task_3.priority})")
    print()
    
    # Create Tasks for Bella
    task_4 = CareTask(
        task_id="task_4",
        title="Feeding",
        category="feeding",
        duration_minutes=10,
        priority="high",
        due_date=date.today(),
        due_window_start=time(7, 0),
        due_window_end=time(20, 0),
        is_mandatory=True
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
        is_mandatory=True
    )
    
    task_6 = CareTask(
        task_id="task_6",
        title="Interactive play",
        category="enrichment",
        duration_minutes=15,
        priority="medium",
        due_date=date.today(),
        due_window_start=time(17, 0),
        due_window_end=time(19, 0),
        is_mandatory=False
    )
    
    bella.add_task(task_4)
    bella.add_task(task_5)
    bella.add_task(task_6)
    print(f"✓ Added 3 tasks to {bella.name}:")
    print(f"  • {task_4.title} ({task_4.duration_minutes} min, {task_4.priority})")
    print(f"  • {task_5.title} ({task_5.duration_minutes} min, {task_5.priority})")
    print(f"  • {task_6.title} ({task_6.duration_minutes} min, {task_6.priority})")
    print()
    
    # Get all tasks
    all_tasks = owner.get_all_tasks()
    print(f"✓ Total tasks across all pets: {len(all_tasks)}")
    print()
    
    # Create scheduler and generate plans
    scheduler = Scheduler(ranking_strategy="priority_first")
    
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
    
    print("=" * 60)
    print("Schedule generation complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
