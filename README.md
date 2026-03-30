# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Smarter Scheduling Features

Beyond the core scheduling, PawPal+ includes several intelligent features to make life easier:

**Recurring Tasks** — Set a task to repeat daily (like feeding) or weekly (like baths), and the system automatically creates tomorrow's task once today's is done. No need to manually re-add the same tasks every single day.

**Smart Filtering** — Quickly find what you're looking for: filter tasks by pet name, completion status, or combine both. Want to see all incomplete tasks for Mochi? One click.

**Time-Based Sorting** — Tasks can be sorted by their preferred time window (morning vs afternoon), so you can plan around your pet's natural schedule—early birds get their walk at 7 AM, night owls at 5 PM.

**Conflict Detection** — The system watches for scheduling problems in real time. If two tasks overlap, you'll get a friendly warning instead of a silent clash. It tells you exactly what's conflicting and for how long, so you can fix it before the day begins.

These features work together to turn a tedious manual process into an intelligent planning assistant that learns your patterns and helps you stay on top of pet care.

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## Testing PawPal+

To run the test suite:

```bash
python -m pytest
```

Current tests cover the most important scheduler behaviors: basic task completion and pet task management, time-based sorting order, daily recurring task auto-creation for the next day, and conflict detection for overlapping or duplicate time slots. In short, the core planning logic is being checked from a few different angles, not just one happy path.

Confidence Level: ★★★★☆ (4/5)

Why 4/5: all implemented tests are currently passing, including the new sorting, recurrence, and conflict checks. The system looks reliable for core workflows, but there is still room to expand edge-case coverage (for example, invalid time formats, recurrence with missing dates, and additional multi-pet scenarios).
