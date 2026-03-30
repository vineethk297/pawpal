"""
Simple test demonstrating conflict detection in main workflow.
Avoids Unicode character encoding issues.
"""

from datetime import date, time
from pawpal_system import Owner, Pet, CareTask, Scheduler, DailyPlan

def simple_conflict_demo():
    print("=" * 70)
    print("CONFLICT DETECTION IN PAWPAL SCHEDULER")
    print("=" * 70)
    print()
    
    # Setup
    owner = Owner(
        owner_id="owner_1",
        name="Jordan",
        daily_time_budget_minutes=180
    )
    
    mochi = Pet(
        pet_id="pet_1",
        name="Mochi",
        species="dog",
        age=3
    )
    owner.add_pet(mochi)
    
    # Create tasks
    walk = CareTask(
        task_id="walk",
        title="Morning Walk",
        category="exercise",
        duration_minutes=30,
        priority="high",
        due_date=date.today()
    )
    
    feed = CareTask(
        task_id="feed",
        title="Feeding",
        category="feeding",
        duration_minutes=15,
        priority="high",
        due_date=date.today()
    )
    
    groom = CareTask(
        task_id="groom",
        title="Grooming",
        category="grooming",
        duration_minutes=20,
        priority="medium",
        due_date=date.today()
    )
    
    mochi.add_task(walk)
    mochi.add_task(feed)
    mochi.add_task(groom)
    
    # Generate normal plan
    scheduler = Scheduler()
    plan = scheduler.generate_plan(
        tasks=mochi.tasks,
        available_minutes=owner.daily_time_budget_minutes,
        owner=owner,
        pet=mochi,
        plan_date=date.today()
    )
    
    print("Generated Schedule:")
    print("-" * 70)
    for task, start, end in plan.scheduled_items:
        print(f"  {start.strftime('%H:%M')}-{end.strftime('%H:%M')}: {task.title:20s} ({task.duration_minutes} min)")
    print()
    
    # Check for conflicts (should be none)
    conflicts = scheduler.detect_conflicts(plan.scheduled_items)
    print("Conflict Detection Results (Normal Schedule):")
    print("-" * 70)
    if conflicts:
        print("CONFLICTS DETECTED:")
        for warning in conflicts:
            print(f"  {warning}")
    else:
        print("  [OK] No conflicts detected in schedule")
    print()
    
    # Now create a schedule WITH conflicts
    print("=" * 70)
    print("TEST: Schedule WITH Intentional Conflicts")
    print("=" * 70)
    print()
    
    conflicting_schedule = [
        (walk, time(9, 0), time(9, 30)),      # 9:00-9:30
        (feed, time(9, 15), time(9, 35)),     # 9:15-9:35 (OVERLAPS!)
        (groom, time(9, 35), time(9, 55))     # 9:35-9:55
    ]
    
    print("Conflicting Schedule:")
    print("-" * 70)
    for task, start, end in conflicting_schedule:
        print(f"  {start.strftime('%H:%M')}-{end.strftime('%H:%M')}: {task.title:20s} ({task.duration_minutes} min)")
    print()
    
    # Check for conflicts (should find overlap)
    conflicts = scheduler.detect_conflicts(conflicting_schedule)
    print("Conflict Detection Results (Conflicting Schedule):")
    print("-" * 70)
    if conflicts:
        print(f"  [{len(conflicts)} CONFLICT(S) DETECTED]:")
        for warning in conflicts:
            print(f"    {warning}")
    else:
        print("  [OK] No conflicts detected")
    print()
    
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print("""
The detect_conflicts() method:
  - Returns a list of warning messages (non-crashing)
  - Calculates overlap duration for each conflict
  - Works with any schedule (single or multiple pets)
  - Allows the program to continue running
  - Provides detailed information about each conflict
    """)


if __name__ == "__main__":
    simple_conflict_demo()
