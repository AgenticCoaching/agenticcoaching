# Athlete Setup

Onboard new users into AgenticCoaching and initialize the right structure from day one.

## Supported operating modes

1. **Solo athlete**
   - One person planning and tracking their own training.

2. **Household host (multi-athlete)**
   - One host workspace managing multiple athletes in the same household (e.g., partner setup).

3. **Coach with clients**
   - A professional coach using one agent/workspace to manage multiple client athletes.

## Responsibilities

- Collect onboarding profile fields (identity, goals, constraints, sport priorities, injury context).
- Create standard athlete profile files and folder scaffolding.
- Configure check-in cadence/preferences.
- Set initial coaching mode and role boundaries.
- Produce a setup summary and next actions.

## Output structure (default)

`coaching/athletes/<athlete>/...` for each athlete profile.

For coach-with-clients mode, maintain one athlete folder per client under the same root.

## Skills

- `skills/new-athlete-onboarding.md` — onboarding flow and required fields.
