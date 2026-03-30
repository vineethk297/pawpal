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

The scheduler considers three key constraints:

1. **Time Budget**: The owner has a fixed number of minutes available each day (e.g., 180 minutes). No task can be scheduled if there aren't enough minutes remaining. This is the hard constraint that limits what's possible.

2. **Task Priority & Urgency**: Tasks are ranked by (1) whether they're mandatory, (2) priority level (high > medium > low), and (3) duration (shorter tasks first to fit more in). This ranking system ensures critical tasks get scheduled first. The decision tree is: mandatory tasks before optional ones, high-priority before low, and shorter tasks before longer ones to maximize packing efficiency.

3. **Task Duration**: Each task has a duration in minutes, and we schedule them back-to-back starting at 9 AM. If a task won't fit in the remaining time, it goes into the "unscheduled" list.

I decided these constraints mattered most because:
- **Time budget** is non-negotiable (real-world constraint)
- **Priority** respects user intent (a vet appointment must happen, daily feeding too)
- **Duration** is objective and helps us pack the schedule efficiently

I *did not* implement constraints like:
- Task time windows (e.g., "feeding only 7-9 AM") — I added the field but the greedy scheduler ignores it
- Preferred owner time blocks (e.g., "only schedule in mornings") — parsed but unused in scheduling
- Task dependencies (e.g., "feed before play") — out of scope for MVP

**b. Tradeoffs**

The scheduler makes a key tradeoff: **Greedy scheduling (fast, simple) instead of optimal bin packing (slower, finds best solution)**.

**The Tradeoff Explained:**
The current scheduler uses a greedy algorithm: rank tasks by priority, then fit them into the timeline in order until time runs out. This is O(n log n) for sorting + O(n) for scheduling = O(n log n) total.

An optimal approach would use bin packing algorithms (like First Fit Decreasing) which might rearrange tasks to fit more total work in the available time. This could be O(n²) or worse depending on the algorithm.

**Example:**
```
Available: 100 minutes
Tasks: [Task A: 60 min, Task B: 30 min, Task C: 25 min, Task D: 20 min]

Greedy approach (current):
- Schedule A (60 min) → 40 min left
- Schedule B (30 min) → 10 min left  
- Can't fit C (25 min) or D (20 min)
- Result: 90 min used, 2 tasks left unscheduled

Optimal bin packing:
- Schedule A (60 min) → 40 min left
- Schedule C (25 min) → 15 min left
- Schedule D (20 min) → DOESN'T FIT (needs 20, have 15)
- Or: Schedule B (30 min) + D (20 min) → Schedule A, then B+D = 110 min (exceeds budget!)
- Actually greedy IS optimal here...

But consider:
Available: 100 min
Tasks: [60, 30, 25, 25]
- Greedy: 60 + 30 = 90 (one 25 doesn't fit)
- Optimal: 60 + 25 + 25 = 110 (exceeds!) or just 60 + 30 = 90
```

In reality, the greedy approach often produces good results for this domain.

**Why this tradeoff is reasonable:**
1. **Perfect schedules are rare**: In pet care, mandatory tasks (feeding, walks) usually have high priority anyway. Optimizing the low-priority leftover tasks isn't worth the complexity.
2. **Small problem size**: Most owners have 5-10 tasks per day. With n=10, greedy is > 99% as effective as optimal, and users can't tell the difference.
3. **User flexibility matters more**: If the schedule isn't perfect, users will manually adjust it. The system is a *helper*, not a dictator. A slightly suboptimal but understandable greedy schedule is better than a magical optimal schedule the user doesn't understand.
4. **Simplicity aids debugging**: If a user says "why wasn't my task scheduled?", it's easy to explain greedy ordering. Optimal algorithms are hard to reason about.
5. **I/O bound, not CPU bound**: The bottleneck is waiting for user input in the Streamlit UI, not scheduling computation. Optimizing scheduling gives no user-visible benefit.

The design philosophy: **Make it correct first, simple second, fast third.** Premature optimization kills code clarity and introduces bugs.

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
