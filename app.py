import streamlit as st
from pawpal_system import Owner, Pet, CareTask, Scheduler
from datetime import date, time

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.
"""
)

st.info(
    """
PawPal+ is a pet care planning assistant. It helps a pet owner plan care tasks for their pet(s) based on constraints like time, priority, and preferences.
"""
)


def load_demo_data() -> None:
    """Load a realistic demo dataset with two pets and mixed-priority tasks."""
    owner = st.session_state.owner

    # Avoid duplicating demo records if user clicks multiple times.
    if owner.pets:
        return

    mochi = Pet(
        pet_id="mochi",
        name="Mochi",
        species="dog",
        age=4,
        health_notes="Needs a long morning walk.",
    )
    bella = Pet(
        pet_id="bella",
        name="Bella",
        species="cat",
        age=6,
        health_notes="Prefers calm play in late afternoon.",
    )

    mochi.add_task(
        CareTask(
            task_id="mochi_walk",
            title="Morning Walk",
            category="walking",
            duration_minutes=30,
            priority="high",
            due_date=date.today(),
            due_window_start=time(8, 0),
            due_window_end=time(10, 0),
            is_mandatory=True,
            frequency="daily",
        )
    )
    mochi.add_task(
        CareTask(
            task_id="mochi_feed",
            title="Breakfast Feeding",
            category="feeding",
            duration_minutes=15,
            priority="high",
            due_date=date.today(),
            due_window_start=time(7, 0),
            due_window_end=time(9, 30),
            is_mandatory=True,
            frequency="daily",
        )
    )
    mochi.add_task(
        CareTask(
            task_id="mochi_brush",
            title="Brush Coat",
            category="grooming",
            duration_minutes=20,
            priority="medium",
            due_date=date.today(),
            due_window_start=time(18, 0),
            due_window_end=time(19, 30),
            frequency="weekly",
        )
    )

    bella.add_task(
        CareTask(
            task_id="bella_feed",
            title="Dinner Feeding",
            category="feeding",
            duration_minutes=10,
            priority="high",
            due_date=date.today(),
            due_window_start=time(17, 30),
            due_window_end=time(19, 0),
            is_mandatory=True,
            frequency="daily",
        )
    )
    bella.add_task(
        CareTask(
            task_id="bella_play",
            title="Interactive Play",
            category="enrichment",
            duration_minutes=20,
            priority="medium",
            due_date=date.today(),
            due_window_start=time(16, 0),
            due_window_end=time(18, 30),
            frequency="daily",
        )
    )
    bella.add_task(
        CareTask(
            task_id="bella_litter",
            title="Clean Litter Box",
            category="other",
            duration_minutes=10,
            priority="high",
            due_date=date.today(),
            due_window_start=time(9, 0),
            due_window_end=time(11, 0),
            is_mandatory=True,
            frequency="daily",
        )
    )

    owner.add_pet(mochi)
    owner.add_pet(bella)


def reset_demo_state() -> None:
    """Reset pet, task, and plan state while preserving owner profile inputs."""
    owner = st.session_state.owner
    owner.pets = []
    if "current_plan" in st.session_state:
        del st.session_state.current_plan


with st.sidebar:
    st.header("Interactive Demo")
    st.caption("Use these controls to quickly showcase full functionality.")

    if st.button("Load Demo Data", use_container_width=True):
        load_demo_data()
        st.success("Demo pets and tasks loaded.")
        st.rerun()

    if st.button("Reset Demo", use_container_width=True):
        reset_demo_state()
        st.warning("Demo data reset.")
        st.rerun()

st.divider()

# Initialize Owner in session state (only once)
if "owner" not in st.session_state:
    st.session_state.owner = Owner(
        owner_id="owner_1",
        name="Jordan",
        daily_time_budget_minutes=180,
        preferred_time_blocks=["morning", "afternoon"]
    )

st.subheader("Owner Profile")
col1, col2 = st.columns(2)
with col1:
    owner_name = st.text_input(
        "Owner name", 
        value=st.session_state.owner.name,
        key="owner_name_input"
    )
    if owner_name != st.session_state.owner.name:
        st.session_state.owner.name = owner_name

with col2:
    time_budget = st.number_input(
        "Daily time available (minutes)",
        value=st.session_state.owner.daily_time_budget_minutes,
        min_value=30,
        max_value=1440,
        key="time_budget_input"
    )
    if time_budget != st.session_state.owner.daily_time_budget_minutes:
        st.session_state.owner.set_time_budget(time_budget)

st.divider()

# Pet Management Section
st.subheader("Manage Pets")
pet_name = st.text_input("Pet name", value="Mochi", key="pet_name_new")
species = st.selectbox("Species", ["dog", "cat", "other"], key="species_new")
health_notes = st.text_area("Health notes (optional)", key="health_notes_new")

if st.button("Add Pet"):
    # Check if pet already exists
    existing_pet = st.session_state.owner.get_pet_by_id(pet_name.lower())
    if existing_pet:
        st.error(f"Pet '{pet_name}' already exists!")
    else:
        # Create new Pet and add to owner
        new_pet = Pet(
            pet_id=pet_name.lower(),
            name=pet_name,
            species=species,
            age=1,
            health_notes=health_notes
        )
        st.session_state.owner.add_pet(new_pet)
        st.success(f"✓ Added pet: {pet_name}")
        st.rerun()

# Display pets
st.markdown("### Current Pets")
pets = st.session_state.owner.pets
if pets:
    scheduler_for_display = Scheduler(ranking_strategy="priority_first")
    for pet in pets:
        with st.expander(f"🐾 {pet.name} ({pet.species})"):
            st.write(f"**Health notes:** {pet.health_notes if pet.health_notes else 'None'}")
            st.write(f"**Tasks:** {len(pet.tasks)}")
            
            # Add task to this pet
            st.markdown("#### Add Task to this Pet")
            task_title = st.text_input("Task name", key=f"task_title_{pet.pet_id}")
            task_category = st.selectbox(
                "Category", 
                ["walking", "feeding", "grooming", "medical", "enrichment", "other"],
                key=f"task_category_{pet.pet_id}"
            )
            task_duration = st.number_input(
                "Duration (minutes)",
                value=20,
                min_value=1,
                max_value=240,
                key=f"task_duration_{pet.pet_id}"
            )
            task_priority = st.selectbox(
                "Priority",
                ["low", "medium", "high"],
                key=f"task_priority_{pet.pet_id}"
            )
            
            if st.button(f"Add Task to {pet.name}", key=f"add_task_btn_{pet.pet_id}"):
                if task_title.strip():
                    task = CareTask(
                        task_id=f"{pet.pet_id}_task_{len(pet.tasks) + 1}",
                        title=task_title,
                        category=task_category,
                        duration_minutes=int(task_duration),
                        priority=task_priority,
                        due_date=date.today(),
                        is_mandatory=(task_priority == "high")
                    )
                    pet.add_task(task)
                    st.success(f"✓ Added task: {task_title}")
                    st.rerun()
                else:
                    st.error("Task name cannot be empty!")
            
            # Display tasks for this pet
            if pet.tasks:
                st.markdown(f"**Tasks for {pet.name}:**")

                ranked_tasks = scheduler_for_display.rank_tasks(pet.tasks)
                ranked_rows = [
                    {
                        "Task": task.title,
                        "Category": task.category,
                        "Duration (min)": task.duration_minutes,
                        "Priority": task.priority,
                        "Mandatory": "Yes" if task.is_mandatory else "No",
                        "Due Date": task.due_date.isoformat() if task.due_date else "N/A",
                    }
                    for task in ranked_tasks
                ]
                st.caption("Ranked by scheduler (mandatory/high priority first)")
                st.table(ranked_rows)

                time_sorted_tasks = scheduler_for_display.sort_by_time(pet.tasks)
                time_rows = [
                    {
                        "Task": task.title,
                        "Window Start": task.due_window_start.strftime("%H:%M") if task.due_window_start else "N/A",
                        "Window End": task.due_window_end.strftime("%H:%M") if task.due_window_end else "N/A",
                    }
                    for task in time_sorted_tasks
                ]
                st.caption("Sorted by task time window")
                st.table(time_rows)
else:
    st.info("No pets yet. Add one above!")

st.divider()
st.subheader("Interactive Task Actions")
st.caption("Try completion and recurrence behavior directly from the UI.")

if st.session_state.owner.pets:
    action_pet_names = [pet.name for pet in st.session_state.owner.pets]
    action_pet_name = st.selectbox("Select pet", action_pet_names, key="task_action_pet")
    action_pet = st.session_state.owner.get_pet_by_id(action_pet_name.lower())

    if action_pet and action_pet.tasks:
        task_options = {
            f"{task.title} ({task.priority}, {task.frequency})": task.task_id
            for task in action_pet.tasks
        }
        selected_task_label = st.selectbox(
            "Select task",
            list(task_options.keys()),
            key="task_action_task",
        )
        selected_task_id = task_options[selected_task_label]
        selected_task = action_pet.get_task_by_id(selected_task_id)

        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("Mark Complete", use_container_width=True):
                selected_task.mark_completed()
                st.success(f"Marked '{selected_task.title}' complete.")
                st.rerun()
        with col_b:
            if st.button("Complete + Next Recurrence", use_container_width=True):
                next_task = selected_task.mark_completed_recurring(action_pet)
                if next_task:
                    st.success(
                        f"Completed '{selected_task.title}' and created next occurrence for {next_task.due_date}."
                    )
                else:
                    st.warning("This is a one-time task. Marked complete without recurrence.")
                st.rerun()
    else:
        st.warning("Selected pet has no tasks yet.")
else:
    st.info("Add pets and tasks to enable task actions.")

st.divider()
st.subheader("Task Explorer")
st.caption("Filter tasks by pet and completion status using backend query methods.")

if st.session_state.owner.pets:
    explorer_pet = st.selectbox(
        "Filter by pet",
        ["All Pets"] + [pet.name for pet in st.session_state.owner.pets],
        key="explorer_pet",
    )
    explorer_status = st.selectbox(
        "Filter by status",
        ["All", "Incomplete", "Completed"],
        key="explorer_status",
    )

    pet_filter = None if explorer_pet == "All Pets" else explorer_pet
    if explorer_status == "All":
        completion_filter = None
    elif explorer_status == "Incomplete":
        completion_filter = False
    else:
        completion_filter = True

    filtered_tasks = st.session_state.owner.filter_tasks(
        pet_name=pet_filter,
        completed=completion_filter,
    )

    if filtered_tasks:
        explorer_rows = []
        for task in filtered_tasks:
            owner_pet_name = "Unknown"
            for pet in st.session_state.owner.pets:
                if task in pet.tasks:
                    owner_pet_name = pet.name
                    break
            explorer_rows.append(
                {
                    "Pet": owner_pet_name,
                    "Task": task.title,
                    "Priority": task.priority,
                    "Duration (min)": task.duration_minutes,
                    "Frequency": task.frequency,
                    "Completed": "Yes" if task.is_completed else "No",
                }
            )
        st.table(explorer_rows)
    else:
        st.warning("No tasks match the selected filters.")
else:
    st.info("Task Explorer will appear after you add a pet.")

st.divider()

st.subheader("Generate Daily Schedule")
st.caption("Create a schedule for today based on available time and pet tasks.")

if not st.session_state.owner.pets:
    st.warning("⚠️ Add at least one pet and some tasks before generating a schedule.")
else:
    scheduler = Scheduler(ranking_strategy="priority_first")

    # Let user select which pet to schedule
    pet_names = [pet.name for pet in st.session_state.owner.pets]
    selected_pet_name = st.selectbox("Select pet to schedule", pet_names, key="pet_select_schedule")
    selected_pet = st.session_state.owner.get_pet_by_id(selected_pet_name.lower())

    if selected_pet and selected_pet.tasks:
        st.markdown("#### Scheduler Preview")
        preview_ranked = scheduler.rank_tasks(selected_pet.tasks)
        preview_rows = [
            {
                "Order": idx + 1,
                "Task": task.title,
                "Priority": task.priority,
                "Duration (min)": task.duration_minutes,
                "Mandatory": "Yes" if task.is_mandatory else "No",
            }
            for idx, task in enumerate(preview_ranked)
        ]
        st.table(preview_rows)
        st.success("Scheduler ranking is ready. Click Generate Schedule to build today's plan.")
    elif selected_pet:
        st.warning(f"No tasks found for {selected_pet.name}. Add tasks before generating a schedule.")
    
    if st.button("Generate Schedule"):
        if not selected_pet.tasks:
            st.error(f"No tasks for {selected_pet.name}. Add tasks first!")
        else:
            # Use the Scheduler to generate a plan
            plan = scheduler.generate_plan(
                tasks=selected_pet.tasks,
                available_minutes=st.session_state.owner.daily_time_budget_minutes,
                owner=st.session_state.owner,
                pet=selected_pet,
                plan_date=date.today()
            )
            
            # Store plan in session state for display
            st.session_state.current_plan = plan
            st.success("✓ Schedule generated!")

# Display the generated plan
if "current_plan" in st.session_state:
    plan = st.session_state.current_plan
    st.markdown("---")
    st.subheader(f"📅 Today's Schedule for {plan.pet.name}")

    schedule_rows = [
        {
            "Task": task.title,
            "Start": start.strftime("%H:%M"),
            "End": end.strftime("%H:%M"),
            "Duration (min)": task.duration_minutes,
            "Priority": task.priority,
        }
        for task, start, end in plan.scheduled_items
    ]

    if schedule_rows:
        st.success("Tasks scheduled successfully.")
        st.table(schedule_rows)
    else:
        st.warning("No tasks could be scheduled for today.")

    if plan.unscheduled_tasks:
        unscheduled_rows = [
            {
                "Task": task.title,
                "Duration (min)": task.duration_minutes,
                "Priority": task.priority,
                "Reason": "Insufficient available time",
            }
            for task in plan.unscheduled_tasks
        ]
        st.warning("Some tasks could not be scheduled. See details below.")
        st.table(unscheduled_rows)

    conflict_checker = Scheduler(ranking_strategy="priority_first")
    conflict_warnings = conflict_checker.detect_conflicts(plan.scheduled_items)
    if conflict_warnings:
        for warning in conflict_warnings:
            st.warning(warning)
    else:
        st.success("No schedule conflicts detected.")

    st.caption(f"Total scheduled time: {plan.total_scheduled_minutes} minutes")
    
    # Display reasoning notes
    if plan.reasoning_notes:
        with st.expander("💡 How we made these scheduling decisions"):
            for note in plan.reasoning_notes:
                st.write(f"• {note}")
