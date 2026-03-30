# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

I settled on five core classes that map directly to the problem domain:

**Owner** holds the person who is managing pet care. It stores their name, how much time they have available each day, and their preferred time blocks (morning, afternoon, etc.). The responsibility of this class is to represent what the owner can feasibly do—it's the constraint setter for scheduling.

**Pet** represents the animal being cared for. It holds the pet's name, species, age, and any health notes. Its responsibility is to give context about *what* needs care; different animals have different care profiles.

**CareTask** is the unit of work—a specific action like "morning walk" or "feeding." Each task knows its duration in minutes, priority level (low, medium, high), whether it's mandatory, and what category it falls into. This class is the building block that the scheduler works with.

**DailyPlan** is the output: a schedule for a single day. It holds a list of scheduled tasks with their time slots, any tasks that didn't fit, total minutes used, and reasoning notes that explain why certain choices were made. Its responsibility is to present the plan clearly and justify it to the user.

**Scheduler** is the engine that makes the decisions. It takes a list of tasks and the owner's available time, ranks tasks by priority and urgency, fits them into the available time slots, and produces a DailyPlan. It's responsible for the actual scheduling logic and deciding which tasks make the cut.

This structure separates data (Owner, Pet, CareTask, DailyPlan) from logic (Scheduler), making the system flexible and testable.

**b. Design changes**

Yes, the design evolved as I reviewed the skeleton and thought through the data flow. I made several key changes:

First, I added a `due_date` field to CareTask. The initial design only had time windows (start and end times), but tasks need to know *which day* they're meant for. Without this, I couldn't properly implement `is_due_on(target_date)`, and the scheduler wouldn't be able to distinguish between tasks for today vs. tomorrow.

Second, I added explicit `owner` and `pet` references to DailyPlan. Initially, DailyPlan was just a container of times and tasks, but it had no way to know *whose* plan it was. In practice, when displaying the plan to the user in Streamlit or when auditing decisions, I need to know which owner's time budget was used and which pet's tasks made the schedule. This makes the plan self-contained and traceable.

Third, I changed the Scheduler method signatures to accept the `owner` object directly, not just `available_minutes`. This was crucial because Owner holds the `preferred_time_blocks` (e.g., "only in the morning"). The scheduler needs to respect these preferences, so it should have access to the full Owner object, not just a number.

Fourth, I implemented validation in `DailyPlan.add_scheduled_item()` to detect time conflicts. The initial stub just added tasks blindly, but a malformed plan could be created silently with overlapping tasks. Now it checks for overlaps and raises a clear error, catching bugs early. It also auto-updates `total_scheduled_minutes` so the two stay synchronized.

These changes reduced the risk of inconsistent state and made the domain model more complete.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
