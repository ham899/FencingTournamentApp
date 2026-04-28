# Data Model

## Entities

### Tournament
- id
- name
- date
- format
- poule_touch_limit
- de_touch_limit
- completed

### Fencer
- id
- display_name

### TournamentEntry
- id
- tournament_id
- fencer_id
- seed

### Poule
- id
- tournament_id
- number

### Match
- id
- tournament_id
- type (poule / de)
- fencer1_entry_id
- fencer2_entry_id
- score1
- score2
- score_to_win
- winner_entry_id
- completed

### DEBracket
- id
- tournament_id
- size

## Computed Values

### Poule Stats
- victories (V)
- matches fenced
- victory ratio
- TS (touches scored)
- TR (touches received)
- indicator (TS - TR)

### Rankings
- Computed dynamically from match results