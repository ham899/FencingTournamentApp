from dataclasses import dataclass
from TournamentEntry import TournamentEntry

@dataclass
class PouleResult:
    entry: TournamentEntry
    poule_id: int
    matches_fenced: int = 0
    victories: int = 0
    touches_scored: int = 0
    touches_received: int = 0

    def __str__(self):
        return f'{self.entry.fencer.display_name}: V = {self.victories}, TS = {self.touches_scored}, TR = {self.touches_received}'


@dataclass
class PouleResults:
    poule_id: int
    results: dict[int, PouleResult]

    def calculate_ranking(self):
        r = dict()
        for k, v in self.results.items():
            fencer_result = v
            r[v.entry.fencer.display_name] = (fencer_result.victories, fencer_result.touches_scored-fencer_result.touches_received)

        r = dict(sorted(r.items(), key=lambda v: v[1], reverse=True))
        return [key for key in r.keys()]


    def __str__(self):
        ret = ''
        for k, r in self.results.items():
            ret += f'{k} {r.entry.fencer.display_name}: V = {r.victories}, TS = {r.touches_scored}, TR = {r.touches_received}, I = {r.touches_scored - r.touches_received}\n'
        return ret