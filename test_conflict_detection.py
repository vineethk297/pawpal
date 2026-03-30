"""
Demonstrate Scheduler conflict detection (lightweight, non-crashing approach).
Shows how overlapping tasks are detected and reported as warnings.
"""

from datetime import date, time
from pawpal_system import Owner, Pet, CareTask, Scheduler

def main():
    print("=" * 80)
    print("🔍 SCHEDULER CONFLICT DETECTION DEMONSTRATION")
    print("=" * 80)
    print()
    
    # Create owner
    owner = Owner(
        owner_id="owner_1",
        name="Jordan",
        daily_time_budget_minutes=300  # 5 hours available
    )
    
    # Create two pets
    mochi = Pet(
        pet_id="pet_1",
        name="Mochi",
        species="dog",
        age=3
    )
    
    bella = Pet(
        pet_id="pet_2",
        name="Bella",
        species="cat",
        age=5
    )
    
    owner.add_pet(mochi)
    owner.add_pet(bella)
    
    print(f"Owner: {owner.name}")
    print(f"Pets: {mochi.name} (dog), {bella.name} (cat)")
    print()
    
    # ====== SCENARIO 1: Same pet with overlapping tasks ======
    print("=" * 80)
    print("SCENARIO 1: Mochi - Same pet with overlapping tasks")
    print("=" * 80)
    print()
    
    # Create tasks for Mochi that will overlap
    morning_walk = CareTask(
        task_id="walk_1",
        title="Morning Walk",
        category="exercise",
        duration_minutes=30,
        priority="high",
        due_date=date.today(),
        is_mandatory=True
    )
    
    feeding_overlap = CareTask(
        task_id="feed_1",
        title="Morning Feeding",
        category="feeding",
        duration_minutes=20,
        priority="high",
        due_date=date.today(),
        is_mandatory=True
    )
    
    grooming_overlap = CareTask(
        task_id="groom_1",
        title="Brush Teeth",
        category="grooming",
        duration_minutes=15,
        priority="medium",
        due_date=date.today(),
        is_mandatory=False
    )
    
    play_time = CareTask(
        task_id="play_1",
        title="Playtime",
        category="enrichment",
        duration_minutes=25,
        priority="medium",
        due_date=date.today(),
        is_mandatory=False
    )
    
    mochi.add_task(morning_walk)
    mochi.add_task(feeding_overlap)
    mochi.add_task(grooming_overlap)
    mochi.add_task(play_time)
    
    print(f"Mochi's tasks:")
    for task in mochi.tasks:
        print(f"  • {task.title:20s} - {task.duration_minutes} min ({task.priority})")
    print()
    
    # MANUALLY create overlapping schedule to demonstrate conflict detection
    # (Instead of using generate_plan which uses greedy algorithm)
    scheduler = Scheduler()
    
    # Manually create a schedule with intentional conflicts
    overlapping_schedule = [
        (morning_walk, time(9, 0), time(9, 30)),    # 9:00-9:30
        (feeding_overlap, time(9, 15), time(9, 35)),  # 9:15-9:35 (OVERLAPS with walk!)
        (grooming_overlap, time(9, 35), time(9, 50)), # 9:35-9:50
        (play_time, time(10, 0), time(10, 25))      # 10:00-10:25
    ]
    
    print("📅 Proposed schedule for Mochi:")
    for task, start, end in overlapping_schedule:
        print(f"  • {start.strftime('%H:%M')}-{end.strftime('%H:%M')}: {task.title:20s} ({task.duration_minutes} min)")
    print()
    
    # Run conflict detection - this should find the overlap
    conflicts = scheduler.detect_conflicts(overlapping_schedule)
    
    print("🔍 Conflict Detection Results:")
    if conflicts:
        print(f"  ❌ {len(conflicts)} conflict(s) detected:")
        for warning in conflicts:
            print(f"     {warning}")
    else:
        print(f"  ✅ No conflicts detected")
    print()
    
    # ====== SCENARIO 2: Multiple pets with separate schedules ======
    print("=" * 80)
    print("SCENARIO 2: Multiple pets - Checking both schedules for conflicts")
    print("=" * 80)
    print()
    
    # Create tasks for Bella
    bella_feeding = CareTask(
        task_id="bella_feed",
        title="Bella Feeding",
        category="feeding",
        duration_minutes=10,
        priority="high",
        due_date=date.today(),
        is_mandatory=True
    )
    
    bella_litter = CareTask(
        task_id="bella_litter",
        title="Litter Box Cleaning",
        category="hygiene",
        duration_minutes=5,
        priority="high",
        due_date=date.today(),
        is_mandatory=True
    )
    
    bella_play = CareTask(
        task_id="bella_play",
        title="Bella Playtime",
        category="enrichment",
        duration_minutes=15,
        priority="medium",
        due_date=date.today(),
        is_mandatory=False
    )
    
    bella.add_task(bella_feeding)
    bella.add_task(bella_litter)
    bella.add_task(bella_play)
    
    print(f"Bella's tasks:")
    for task in bella.tasks:
        print(f"  • {task.title:20s} - {task.duration_minutes} min ({task.priority})")
    print()
    
    # Create clean schedule for Bella (no conflicts)
    bella_schedule = [
        (bella_feeding, time(8, 0), time(8, 10)),
        (bella_litter, time(8, 10), time(8, 15)),
        (bella_play, time(14, 0), time(14, 15))
    ]
    
    print("📅 Proposed schedule for Bella:")
    for task, start, end in bella_schedule:
        print(f"  • {start.strftime('%H:%M')}-{end.strftime('%H:%M')}: {task.title:20s} ({task.duration_minutes} min)")
    print()
    
    bella_conflicts = scheduler.detect_conflicts(bella_schedule)
    print("🔍 Conflict Detection Results:")
    if bella_conflicts:
        print(f"  ❌ {len(bella_conflicts)} conflict(s) detected:")
        for warning in bella_conflicts:
            print(f"     {warning}")
    else:
        print(f"  ✅ No conflicts detected for Bella")
    print()
    
    # ====== SCENARIO 3: No conflicts ======
    print("=" * 80)
    print("SCENARIO 3: Perfect schedule - No overlaps")
    print("=" * 80)
    print()
    
    perfect_schedule = [
        (morning_walk, time(9, 0), time(9, 30)),
        (feeding_overlap, time(9, 30), time(9, 50)),
        (grooming_overlap, time(9, 50), time(10, 5)),
        (play_time, time(10, 5), time(10, 30))
    ]
    
    print("📅 Perfect schedule for Mochi (sequential, no gaps):")
    for task, start, end in perfect_schedule:
        print(f"  • {start.strftime('%H:%M')}-{end.strftime('%H:%M')}: {task.title:20s} ({task.duration_minutes} min)")
    print()
    
    perfect_conflicts = scheduler.detect_conflicts(perfect_schedule)
    print("🔍 Conflict Detection Results:")
    if perfect_conflicts:
        print(f"  ❌ {len(perfect_conflicts)} conflict(s) detected:")
        for warning in perfect_conflicts:
            print(f"     {warning}")
    else:
        print(f"  ✅ No conflicts detected - Schedule is perfect!")
    print()
    
    # ====== SUMMARY ======
    print("=" * 80)
    print("✅ SUMMARY")
    print("=" * 80)
    print(f"""
Conflict Detection Features:

1. detect_conflicts(scheduled_items)
   - Checks for overlapping tasks in a single schedule
   - Returns list of warning messages (non-crashing)
   - Calculates overlap duration
   
2. Lightweight approach:
   - ✅ Catches conflicts with helpful warnings
   - ✅ Doesn't crash the program
   - ✅ Allows scheduling to continue
   - ✅ Reports multiple conflicts at once
   
3. Use cases:
   - Schedule validation
   - Conflict reports for owners
   - Multi-pet scheduling verification
   - Warning systems for double-booked times
    """)


if __name__ == "__main__":
    main()
