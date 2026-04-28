# System Design

## Architecture

- Frontend: Mobile-friendly web UI
- Backend: Python (FastAPI)
- Database: SQLite (dev) → Cloud DB (prod)

## Responsibilities

### Frontend
- UI rendering
- User interaction
- API calls

### Backend
- Tournament logic
- Poule generation
- Ranking computation
- DE bracket generation

### Database
- Store tournaments and results

## Key Operations

- Create tournament
- Add fencers
- Generate poules
- Record/edit matches
- Compute rankings
- Generate DE bracket
- Update bracket
- Save results

## Data Flow

### Setup
- Create entries
- Assign seeds
- Generate poules

### Match Entry
- Save result
- Recompute stats
- Update rankings

### DE Stage
- Generate bracket
- Advance winners
- Update standings