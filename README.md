# HR System Backend

This repository contains a Django-based HR platform organized as modular apps. Each app has a clear responsibility to keep the architecture clean, scalable, and easier to maintain.

## Project Overview

The backend is split into domain-focused Django applications:

1. `accounts` - authentication, identity, and role management (core app)
2. `jobs` - job posting and discovery logic
3. `applications` - candidate applications and CV workflow
4. `assessments` - AI-powered testing and evaluation module
5. `core` (optional but recommended) - shared utilities and cross-cutting concerns

---

## 1) accounts (Core App)

### Goal
Handle authentication and role-based identity for all platform users.

### Why combine users and companies?
Both candidates and recruiters are platform users. A recruiter can also be associated with a company entity, so keeping identity in one app avoids duplicated auth logic.

### Main Models
- `User` (custom Django user)
- `Profile`
- `Role` (Candidate / Recruiter / Admin)
- `Company` (linked to recruiter)

### Features
- Register / login
- Role-based access control
- Profile management

---

## 2) jobs

### Goal
Handle all job-related business logic.

### Main Models
- `Job`
- `JobCategory`
- `Skill`

### Features
- Post job
- Edit job
- Browse jobs
- Search and filter jobs

---

## 3) applications

### Goal
Manage candidate applications as a dedicated domain.

### Why this app is separate (very important)
`applications` is the bridge between users and jobs. Keeping it isolated creates cleaner architecture, reduces coupling, and simplifies future enhancements (status workflows, notifications, analytics).

### Main Models
- `Application`
- `CV`
- `ApplicationStatus` (Pending / Accepted / Rejected)

### Features
- Apply to job
- Upload CV
- Track application status

---

## 4) assessments (AI Module)

### Goal
Provide testing and evaluation after candidate progression (phase 2 intelligence layer).

### Main Models
- `Test`
- `Question`
- `Answer`
- `Result`

### Features
- Generate test (AI)
- Assign test after acceptance
- Countdown system
- Evaluate answers

---

## 5) core (Optional but Powerful)

### Goal
Centralize reusable and cross-app components.

### Typical Contents
- Permissions
- Helpers
- Signals
- Middleware

---

## Architecture Benefits

- Clear separation of concerns
- Easier team collaboration
- Better long-term maintainability
- Simpler testing per domain app
- Scalable for future features (notifications, analytics, interviews, etc.)

## Notes

- Keep app boundaries strict: avoid leaking business logic across apps.
- Prefer service-layer functions for complex workflows spanning multiple apps.
- Add API-level permissions that align with role definitions in `accounts`.
