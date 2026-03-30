import streamlit as st
from pawpal_system import Owner, Pet, CareTask, Scheduler
from datetime import date

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

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
                for task in pet.tasks:
                    st.write(f"• {task.title} - {task.duration_minutes} min ({task.priority})")
else:
    st.info("No pets yet. Add one above!")

st.divider()

st.subheader("Generate Daily Schedule")
st.caption("Create a schedule for today based on available time and pet tasks.")

if not st.session_state.owner.pets:
    st.warning("⚠️ Add at least one pet and some tasks before generating a schedule.")
else:
    # Let user select which pet to schedule
    pet_names = [pet.name for pet in st.session_state.owner.pets]
    selected_pet_name = st.selectbox("Select pet to schedule", pet_names, key="pet_select_schedule")
    selected_pet = st.session_state.owner.get_pet_by_id(selected_pet_name.lower())
    
    if st.button("Generate Schedule"):
        if not selected_pet.tasks:
            st.error(f"No tasks for {selected_pet.name}. Add tasks first!")
        else:
            # Use the Scheduler to generate a plan
            scheduler = Scheduler(ranking_strategy="priority_first")
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
    
    # Display the plan summary
    st.markdown(plan.summarize())
    
    # Display reasoning notes
    if plan.reasoning_notes:
        with st.expander("💡 How we made these scheduling decisions"):
            for note in plan.reasoning_notes:
                st.write(f"• {note}")
