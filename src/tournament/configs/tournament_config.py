from dataclasses import dataclass

from tournament.configs.de_config import DEConfig
from tournament.configs.poule_config import PouleConfig
from tournament.tournament_type import TournamentType


@dataclass(frozen=True, slots=True)
class TournamentConfig:
    """
    Store immutable settings for a tournament's stage sequence.

    Attributes
    ----------
    tournament_type : TournamentType
        The tournament format, defining the required stage count and order.
    stage_configs : tuple[PouleConfig | DEConfig, ...]
        Settings for each stage in tournament order.
    poule_cut_values : tuple[float, ...] | None
        Proportion of entries eliminated after each poule stage that has a subsequent stage, 
        in poule-stage order. 
        Each value must be a float between 0.0 and 0.99 inclusive.
        Must be None for POULE and DE tournaments.

    Notes
    -----
    The first DE stage in a POULE_DE_POULE_DE tournament must be stopped.
    A tournament's final DE stage must run to completion.
    """
    tournament_type: TournamentType
    stage_configs: tuple[PouleConfig | DEConfig, ...]
    poule_cut_values: tuple[float, ...] | None = None


    def __post_init__(self) -> None:
        """
        Validate the stage configurations against the tournament format.

        Raises
        ------
        TypeError
            If the tournament type is invalid, stage_configs is not a tuple,
            a stage configuration has an incorrect type, or poule_cut_values
            is neither None nor a tuple containing only floats.
        ValueError
            If ``stage_configs`` is empty, the stage count does not match the tournament format, 
            or a DE stage's stopping setting is incompatible with its position in the tournament.
        RuntimeError
            If the tournament type has no implemented validation case.
        """
        location = 'TournamentConfig'

        if not isinstance(self.tournament_type, TournamentType):
            raise TypeError(
                f'Tournament type must be a TournamentType object in {location} - '
                f'got {type(self.tournament_type).__name__}'
            )
        
        if not isinstance(self.stage_configs, tuple):
            raise TypeError(
                f'stage_configs must be a tuple in {location} - got {type(self.stage_configs).__name__}'
            )

        if not self.stage_configs:
            raise ValueError(f'stage_configs cannot be empty in {location}')
        
        for i, item in enumerate(self.stage_configs):
            if not isinstance(item, (PouleConfig, DEConfig)):
                raise TypeError(
                    f'Item at index {i} in stage_configs must be either a PouleConfig or DEConfig - '
                    f'got {type(self.stage_configs[i]).__name__}'
                )
            
        if self.poule_cut_values is not None and not isinstance(self.poule_cut_values, tuple):
            raise TypeError(
                f'poule_cut_values must be a tuple in {location} - got {type(self.poule_cut_values).__name__}'
            )
        
        if self.poule_cut_values is not None:
            for i, cut_value in enumerate(self.poule_cut_values):
                if type(cut_value) is not float:
                    raise TypeError(
                        f'Item at index {i} in poule_cut_values must be a float '
                        f'in {location} - got {type(cut_value).__name__}'
                    )

                if not 0.0 <= cut_value <= 0.99:
                    raise ValueError(
                        f'Item at index {i} in poule_cut_values must be inclusively between '
                        f'0 and 0.99 in {location} - got {cut_value}'
                    )

        match self.tournament_type:
            case TournamentType.POULE:
                if len(self.stage_configs) != 1:
                    raise ValueError(
                        'Can only provide one configuration for a POULE type tournament - '
                        f'got {len(self.stage_configs)}'
                    )

                if not isinstance(self.stage_configs[0], PouleConfig):
                    raise TypeError(
                        'A single PouleConfig must be provided for a POULE type tournament - '
                        f'got {type(self.stage_configs[0]).__name__}'
                    )
                
                if self.poule_cut_values is not None:
                    raise ValueError(
                        'Cannot provide poule_cut_values for a POULE type tournament - '
                        f'got {self.poule_cut_values}'
                    )

            case TournamentType.DE:
                if len(self.stage_configs) != 1:
                    raise ValueError(
                        'Can only provide one configuration for a DE type tournament - '
                        f'got {len(self.stage_configs)}'
                    )

                if not isinstance(self.stage_configs[0], DEConfig):
                    raise TypeError(
                        'A single DEConfig must be provided for a DE type tournament - '
                        f'got {type(self.stage_configs[0]).__name__}'
                    )
                
                if self.stage_configs[0].stop_at_round is not None:
                    raise ValueError(
                        'Cannot end the tournament on a stopped bracket - DE tournament type case'
                    )
                
                if self.poule_cut_values is not None:
                    raise ValueError(
                        'Cannot provide poule_cut_values for a DE type tournament - '
                        f'got {self.poule_cut_values}'
                    )

            case TournamentType.POULE_DE:
                if len(self.stage_configs) != 2:
                    raise ValueError(
                        'Must provide exactly two configurations for a POULE_DE type tournament - '
                        f'got {len(self.stage_configs)}'
                    )

                expected_types, position_names = (PouleConfig, DEConfig), ['first', 'second']

                for i, config in enumerate(self.stage_configs):
                    if not isinstance(config, expected_types[i]):
                        raise TypeError(
                            f'The {position_names[i]} configuration must be a {expected_types[i].__name__} for a POULE_DE tournament'
                            f' - got {type(config).__name__}'
                        )

                if self.stage_configs[1].stop_at_round is not None:
                    raise ValueError(
                        'Cannot end the tournament on a stopped bracket - POULE_DE tournament type case'
                    )
                
                if self.poule_cut_values is None:
                    raise ValueError(
                        'Must provide poule_cut_values for a POULE_DE type tournament - '
                        f'got {self.poule_cut_values}'
                    )
                
                if len(self.poule_cut_values) != 1:
                    raise ValueError(
                        'Must provide exactly one poule_cut_value for a POULE_DE type tournament - '
                        f'got {len(self.poule_cut_values)}'
                    )

            case TournamentType.POULE_DE_POULE_DE:
                if len(self.stage_configs) != 4:
                    raise ValueError(
                        'Must provide exactly four configurations for a POULE_DE_POULE_DE type tournament - '
                        f'got {len(self.stage_configs)}'
                    )

                expected_types, position_names = (PouleConfig, DEConfig, PouleConfig, DEConfig), ['first', 'second', 'third', 'fourth']

                for i, config in enumerate(self.stage_configs):
                    if not isinstance(config, expected_types[i]):
                        raise TypeError(
                            f'The {position_names[i]} configuration must be a {expected_types[i].__name__} for a POULE_DE_POULE_DE tournament'
                            f' - got {type(config).__name__}'
                        )

                if self.stage_configs[1].stop_at_round is None:
                    raise ValueError(
                        'The first DE stage must be a stopped bracket for a POULE_DE_POULE_DE tournament'
                    )

                if self.stage_configs[3].stop_at_round is not None:
                    raise ValueError(
                        'Cannot end the tournament on a stopped bracket - POULE_DE_POULE_DE tournament type case'
                    )
                
                if self.poule_cut_values is None:
                    raise ValueError(
                        'Must provide poule_cut_values for a POULE_DE_POULE_DE type tournament - '
                        f'got {self.poule_cut_values}'
                    )
                
                if len(self.poule_cut_values) != 2:
                    raise ValueError(
                        'Must provide exactly two poule_cut_values for a POULE_DE_POULE_DE type tournament - '
                        f'got {len(self.poule_cut_values)}'
                    )

            case _:
                raise RuntimeError(f'An unknown tournament type was encountered in {location}')
