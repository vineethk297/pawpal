"""
Test script to demonstrate recurring task functionality.
Shows how daily and weekly tasks auto-generate next occurrences.
"""

from datetime import date, time
from pawpal_system import Owner, Pet, CareTask

def main():
    print("=" * 70)
    print("🔄 RECURRING TASKS DEMONSTRATION")
    print("=" * 70)
    print()
    
    # Create owner and pet
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
    
    # Create a daily task
    daily_feed = CareTask(
        task_id="feed_daily",
        title="Morning Feeding",
        category="feeding",
        duration_minutes=15,
        priority="high",
        due_date=date.today(),
        due_window_start=time(8, 0),
        due_window_end=time(9, 0),
        is_mandatory=True,
        frequency="daily"
    )
    mochi.add_task(daily_feed)
    
    # Create a weekly task
    weekly_bath = CareTask(
        task_id="bath_weekly",
        title="Weekly Bath",
        category="grooming",
        duration_minutes=45,
        priority="medium",
        due_date=date.today(),
        due_window_start=time(14, 0),
        due_window_end=time(15, 0),
        is_mandatory=False,
        frequency="weekly"
    )
    mochi.add_task(weekly_bath)
    
    # Create a one-time task
    vet_appt = CareTask(
        task_id="vet_checkup",
        title="Vet Appointment",
        category="medical",
        duration_minutes=30,
        priority="high",
        due_date=date.today(),
        due_window_start=time(10, 0),
        due_window_end=time(11, 0),
        is_mandatory=True,
        frequency="one-time"
    )
    mochi.add_task(vet_appt)
    
    print(f"📋 Initial state for {mochi.name}:")
    print(f"   Total tasks: {len(mochi.tasks)}")
    for task in mochi.tasks:
        print(f"   • {task.title:20s} | freq: {task.frequency:10s} | due: {task.due_date}")
    print()
    
    # ====== TEST 1: Daily task recurrence ======
    print("=" * 70)
    print("TEST 1: Complete a DAILY task → Auto-create tomorrow's task")
    print("=" * 70)
    print(f"\nCompleting '{daily_feed.title}' (freq={daily_feed.frequency})...")
    next_daily = daily_feed.mark_completed_recurring(mochi)
    
    print(f"\n✓ Original task status: COMPLETED")
    print(f"  Task ID: {daily_feed.task_id}")
    print(f"  Due date: {daily_feed.due_date}")
    print(f"  is_completed: {daily_feed.is_completed}")
    
    print(f"\n✓ Next occurrence auto-created:")
    print(f"  Task ID: {next_daily.task_id}")
    print(f"  Due date: {next_daily.due_date} (tomorrow)")
    print(f"  is_completed: {next_daily.is_completed}")
    
    print(f"\n📋 Mochi's tasks after:")
    print(f"   Total tasks: {len(mochi.tasks)}")
    for task in mochi.tasks:
        status = "✓ DONE" if task.is_completed else "⚪ TODO"
        print(f"   • {task.title:20s} | freq: {task.frequency:10s} | due: {task.due_date} [{status}]")
    print()
    
    # ====== TEST 2: Weekly task recurrence ======
    print("=" * 70)
    print("TEST 2: Complete a WEEKLY task → Auto-create next week's task")
    print("=" * 70)
    print(f"\nCompleting '{weekly_bath.title}' (freq={weekly_bath.frequency})...")
    next_weekly = weekly_bath.mark_completed_recurring(mochi)
    
    print(f"\n✓ Original task status: COMPLETED")
    print(f"  Task ID: {weekly_bath.task_id}")
    print(f"  Due date: {weekly_bath.due_date}")
    
    print(f"\n✓ Next occurrence auto-created:")
    print(f"  Task ID: {next_weekly.task_id}")
    print(f"  Due date: {next_weekly.due_date} (7 days later)")
    
    print(f"\n📋 Mochi's tasks after:")
    print(f"   Total tasks: {len(mochi.tasks)}")
    for task in mochi.tasks:
        status = "✓ DONE" if task.is_completed else "⚪ TODO"
        print(f"   • {task.title:20s} | freq: {task.frequency:10s} | due: {task.due_date} [{status}]")
    print()
    
    # ====== TEST 3: One-time task ======
    print("=" * 70)
    print("TEST 3: Complete a ONE-TIME task → NO new task created")
    print("=" * 70)
    print(f"\nCompleting '{vet_appt.title}' (freq={vet_appt.frequency})...")
    next_onetime = vet_appt.mark_completed_recurring(mochi)
    
    print(f"\n✓ Original task status: COMPLETED")
    print(f"  Task ID: {vet_appt.task_id}")
    print(f"  Due date: {vet_appt.due_date}")
    
    if next_onetime is None:
        print(f"\n✓ No new task created (one-time tasks don't recur)")
    
    print(f"\n📋 Mochi's tasks after:")
    print(f"   Total tasks: {len(mochi.tasks)}")
    for task in mochi.tasks:
        status = "✓ DONE" if task.is_completed else "⚪ TODO"
        print(f"   • {task.title:20s} | freq: {task.frequency:10s} | due: {task.due_date} [{status}]")
    print()
    
    # ====== TEST 4: Generate next without completing ======
    print("=" * 70)
    print("TEST 4: Preview next occurrence (without marking complete)")
    print("=" * 70)
    preview = next_daily.generate_next_occurrence()
    print(f"\nCurrent task: {next_daily.title}")
    print(f"  Due date: {next_daily.due_date}")
    print(f"  Status: {'COMPLETED' if next_daily.is_completed else 'PENDING'}")
    
    print(f"\nPreview of next occurrence:")
    print(f"  Task ID: {preview.task_id}")
    print(f"  Title: {preview.title}")
    print(f"  Due date: {preview.due_date} (one more day)")
    print(f"  Status: {'COMPLETED' if preview.is_completed else 'PENDING'}")
    
    print(f"\n📋 Note: Preview task NOT added to pet's task list (use mark_completed_recurring for auto-add)")
    print(f"   Mochi's tasks still: {len(mochi.tasks)}")
    print()
    
    # ====== SUMMARY ======
    print("=" * 70)
    print("✅ SUMMARY")
    print("=" * 70)
    print(f"""
When a recurring task is marked complete:
  • Daily tasks: New task due (today + 1 day)
  • Weekly tasks: New task due (today + 7 days)
  • One-time tasks: No new task created
  
New tasks are AUTOMATICALLY added to the pet's task list.
Use mark_completed_recurring(pet) for automatic handling.
Use generate_next_occurrence() to preview without auto-adding.
    """)


if __name__ == "__main__":
    main()
