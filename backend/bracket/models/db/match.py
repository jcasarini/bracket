from decimal import Decimal

from heliclockter import datetime_utc, timedelta
from pydantic import BaseModel, Field, model_validator

from bracket.models.db.court import Court
from bracket.models.db.shared import BaseModelORM
from bracket.models.db.stage_item_inputs import StageItemInput
from bracket.utils.id_types import CourtId, MatchId, RoundId, StageItemInputId
from bracket.utils.types import assert_some


class SetScore(BaseModel):
    team1_games: int = Field(0, ge=0)
    team2_games: int = Field(0, ge=0)
    team1_tiebreak: int | None = Field(default=None, ge=0)
    team2_tiebreak: int | None = Field(default=None, ge=0)

    @model_validator(mode="after")
    def tiebreaks_come_in_pairs(self) -> "SetScore":
        if (self.team1_tiebreak is None) != (self.team2_tiebreak is None):
            raise ValueError("Both tiebreak scores must be set together")
        return self


def determine_match_winner_index(match: "Match") -> int | None:
    """
    Determine the index of the winning stage item input.

    Returns 0 when the first input won, 1 when the second input won and None
    when the match ended in a draw or hasn't been decided yet.

    When a match has set scores (tennis scoring), the winner is determined by
    counting the sets won. Otherwise the regular scores are compared.
    """
    if match.scores is not None:
        team1_sets_won = sum(
            1 for set_score in match.scores if set_score.team1_games > set_score.team2_games
        )
        team2_sets_won = sum(
            1 for set_score in match.scores if set_score.team2_games > set_score.team1_games
        )
        if team1_sets_won > team2_sets_won:
            return 0
        if team2_sets_won > team1_sets_won:
            return 1
        return None

    if match.stage_item_input1_score > match.stage_item_input2_score:
        return 0
    if match.stage_item_input2_score > match.stage_item_input1_score:
        return 1
    return None


def get_team_score_in_match(match: "Match", is_team1: bool) -> int:
    """
    Get the score of a team in a match, used for adding score points to a ranking.

    For tennis scoring this is the total number of games won across all sets.
    """
    if match.scores is not None:
        return sum(
            set_score.team1_games if is_team1 else set_score.team2_games
            for set_score in match.scores
        )
    return match.stage_item_input1_score if is_team1 else match.stage_item_input2_score


class MatchBaseInsertable(BaseModelORM):
    created: datetime_utc
    start_time: datetime_utc | None = None
    duration_minutes: int
    margin_minutes: int
    custom_duration_minutes: int | None = None
    custom_margin_minutes: int | None = None
    position_in_schedule: int | None = None
    round_id: RoundId
    stage_item_input1_score: int
    stage_item_input2_score: int
    scores: list[SetScore] | None = None
    court_id: CourtId | None = None
    stage_item_input1_conflict: bool
    stage_item_input2_conflict: bool

    @property
    def end_time(self) -> datetime_utc:
        assert self.start_time
        return self.start_time + timedelta(minutes=self.duration_minutes + self.margin_minutes)


class MatchInsertable(MatchBaseInsertable):
    stage_item_input1_id: StageItemInputId | None = None
    stage_item_input2_id: StageItemInputId | None = None
    stage_item_input1_winner_from_match_id: MatchId | None = None
    stage_item_input2_winner_from_match_id: MatchId | None = None


class Match(MatchInsertable):
    id: MatchId
    stage_item_input1: StageItemInput | None = None
    stage_item_input2: StageItemInput | None = None

    def get_winner(self) -> StageItemInput | None:
        match determine_match_winner_index(self):
            case 0:
                return self.stage_item_input1
            case 1:
                return self.stage_item_input2

        return None


class MatchWithDetails(Match):
    """
    MatchWithDetails has zero or one defined stage item inputs, but not both.
    """

    court: Court | None = None


def get_match_hash(
    stage_item_input1_id: StageItemInputId | None, stage_item_input2_id: StageItemInputId | None
) -> str:
    return f"{stage_item_input1_id}-{stage_item_input2_id}"


class MatchWithDetailsDefinitive(Match):
    stage_item_input1: StageItemInput  # pyrefly: ignore [bad-override]
    stage_item_input2: StageItemInput  # pyrefly: ignore [bad-override]
    court: Court | None = None

    @property
    def stage_item_inputs(self) -> list[StageItemInput]:
        return [self.stage_item_input1, self.stage_item_input2]

    @property
    def stage_item_input_ids(self) -> list[StageItemInputId]:
        return [assert_some(self.stage_item_input1_id), assert_some(self.stage_item_input2_id)]

    def get_input_ids_hashes(self) -> list[str]:
        return [
            get_match_hash(self.stage_item_input1_id, self.stage_item_input2_id),
            get_match_hash(self.stage_item_input2_id, self.stage_item_input1_id),
        ]


class MatchBody(BaseModelORM):
    round_id: RoundId
    stage_item_input1_score: int = 0
    stage_item_input2_score: int = 0
    scores: list[SetScore] | None = None
    court_id: CourtId | None = None
    custom_duration_minutes: int | None = None
    custom_margin_minutes: int | None = None


class MatchCreateBodyFrontend(BaseModelORM):
    round_id: RoundId
    court_id: CourtId | None = None
    stage_item_input1_id: StageItemInputId | None = None
    stage_item_input2_id: StageItemInputId | None = None
    stage_item_input1_winner_from_match_id: MatchId | None = None
    stage_item_input2_winner_from_match_id: MatchId | None = None


class MatchCreateBody(MatchCreateBodyFrontend):
    duration_minutes: int
    margin_minutes: int
    custom_duration_minutes: int | None = None
    custom_margin_minutes: int | None = None


class MatchRescheduleBody(BaseModelORM):
    old_court_id: CourtId
    old_position: int
    new_court_id: CourtId
    new_position: int


class MatchFilter(BaseModel):
    elo_diff_threshold: int
    only_recommended: bool
    limit: int
    iterations: int


class SuggestedMatch(BaseModel):
    stage_item_input1: StageItemInput
    stage_item_input2: StageItemInput
    elo_diff: Decimal
    swiss_diff: Decimal
    is_recommended: bool
    times_played_sum: int
    player_behind_schedule_count: int

    @property
    def stage_item_input_ids(self) -> list[int]:
        return [self.stage_item_input1.id, self.stage_item_input2.id]
