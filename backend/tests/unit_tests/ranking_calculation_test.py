from decimal import Decimal

from heliclockter import datetime_utc

from bracket.logic.ranking.calculation import determine_ranking_for_stage_item
from bracket.logic.ranking.statistics import TeamStatistics
from bracket.models.db.match import (
    MatchWithDetails,
    MatchWithDetailsDefinitive,
    SetScore,
    determine_match_winner_index,
    get_team_score_in_match,
)
from bracket.models.db.ranking import Ranking
from bracket.models.db.stage_item import StageType
from bracket.models.db.stage_item_inputs import StageItemInputFinal
from bracket.models.db.team import Team
from bracket.models.db.util import RoundWithMatches, StageItemWithRounds
from bracket.utils.dummy_records import DUMMY_TEAM1, DUMMY_TEAM2
from bracket.utils.id_types import (
    MatchId,
    RankingId,
    RoundId,
    StageId,
    StageItemId,
    StageItemInputId,
    TeamId,
    TournamentId,
)


def test_determine_ranking_for_stage_item_elimination() -> None:
    tournament_id = TournamentId(-1)
    now = datetime_utc.now()
    stage_item_input1 = StageItemInputFinal(
        id=StageItemInputId(-1),
        team_id=TeamId(-1),
        slot=1,
        tournament_id=tournament_id,
        team=Team(**DUMMY_TEAM1.model_dump(), id=TeamId(-1)),
    )
    stage_item_input2 = StageItemInputFinal(
        id=StageItemInputId(-2),
        team_id=TeamId(-2),
        slot=1,
        tournament_id=tournament_id,
        team=Team(**DUMMY_TEAM2.model_dump(), id=TeamId(-2)),
    )

    ranking = determine_ranking_for_stage_item(
        StageItemWithRounds(
            rounds=[
                RoundWithMatches(
                    id=RoundId(-1),
                    matches=[
                        MatchWithDetailsDefinitive(
                            id=MatchId(-1),
                            stage_item_input1=stage_item_input1,
                            stage_item_input2=stage_item_input2,
                            created=now,
                            duration_minutes=90,
                            margin_minutes=15,
                            round_id=RoundId(-1),
                            stage_item_input1_score=2,
                            stage_item_input2_score=0,
                            stage_item_input1_conflict=False,
                            stage_item_input2_conflict=False,
                        ),
                        MatchWithDetailsDefinitive(
                            id=MatchId(-2),
                            stage_item_input1=stage_item_input1,
                            stage_item_input2=stage_item_input2,
                            created=now,
                            duration_minutes=90,
                            margin_minutes=15,
                            round_id=RoundId(-1),
                            stage_item_input1_score=2,
                            stage_item_input2_score=2,
                            stage_item_input1_conflict=False,
                            stage_item_input2_conflict=False,
                        ),
                        MatchWithDetails(  # This gets ignored in ranking calculation
                            id=MatchId(-3),
                            created=now,
                            duration_minutes=90,
                            margin_minutes=15,
                            round_id=RoundId(-1),
                            stage_item_input1_score=3,
                            stage_item_input2_score=2,
                            stage_item_input1_conflict=False,
                            stage_item_input2_conflict=False,
                        ),
                    ],
                    stage_item_id=StageItemId(-1),
                    created=now,
                    is_draft=False,
                    name="",
                )
            ],
            inputs=[stage_item_input1, stage_item_input2],
            type_name="Single Elimination",
            team_count=4,
            ranking_id=None,
            id=StageItemId(-1),
            stage_id=StageId(-1),
            name="",
            created=now,
            type=StageType.SINGLE_ELIMINATION,
        ),
        Ranking(
            id=RankingId(-1),
            tournament_id=tournament_id,
            created=now,
            win_points=Decimal("3.5"),
            draw_points=Decimal("1.25"),
            loss_points=Decimal("0.0"),
            add_score_points=False,
            position=0,
        ),
    )

    assert ranking == {
        -2: TeamStatistics(wins=0, draws=1, losses=1, points=Decimal("1.25")),
        -1: TeamStatistics(wins=1, draws=1, losses=0, points=Decimal("4.75")),
    }


def test_determine_ranking_for_stage_item_swiss() -> None:
    tournament_id = TournamentId(-1)
    now = datetime_utc.now()
    stage_item_input1 = StageItemInputFinal(
        id=StageItemInputId(-1),
        team_id=TeamId(-1),
        slot=1,
        tournament_id=tournament_id,
        team=Team(**DUMMY_TEAM1.model_dump(), id=TeamId(-1)),
    )
    stage_item_input2 = StageItemInputFinal(
        id=StageItemInputId(-2),
        team_id=TeamId(-2),
        slot=1,
        tournament_id=tournament_id,
        team=Team(**DUMMY_TEAM2.model_dump(), id=TeamId(-2)),
    )

    ranking = determine_ranking_for_stage_item(
        StageItemWithRounds(
            rounds=[
                RoundWithMatches(
                    id=RoundId(-1),
                    matches=[
                        MatchWithDetailsDefinitive(
                            id=MatchId(-1),
                            stage_item_input1=stage_item_input1,
                            stage_item_input2=stage_item_input2,
                            created=now,
                            duration_minutes=90,
                            margin_minutes=15,
                            round_id=RoundId(-1),
                            stage_item_input1_score=2,
                            stage_item_input2_score=0,
                            stage_item_input1_conflict=False,
                            stage_item_input2_conflict=False,
                        ),
                        MatchWithDetailsDefinitive(
                            id=MatchId(-2),
                            stage_item_input1=stage_item_input1,
                            stage_item_input2=stage_item_input2,
                            created=now,
                            duration_minutes=90,
                            margin_minutes=15,
                            round_id=RoundId(-1),
                            stage_item_input1_score=2,
                            stage_item_input2_score=2,
                            stage_item_input1_conflict=False,
                            stage_item_input2_conflict=False,
                        ),
                        MatchWithDetails(  # This gets ignored in ranking calculation
                            id=MatchId(-3),
                            created=now,
                            duration_minutes=90,
                            margin_minutes=15,
                            round_id=RoundId(-1),
                            stage_item_input1_score=3,
                            stage_item_input2_score=2,
                            stage_item_input1_conflict=False,
                            stage_item_input2_conflict=False,
                        ),
                    ],
                    stage_item_id=StageItemId(-1),
                    created=now,
                    is_draft=False,
                    name="",
                )
            ],
            inputs=[stage_item_input1, stage_item_input2],
            type_name="Swiss",
            team_count=4,
            ranking_id=None,
            id=StageItemId(-1),
            stage_id=StageId(-1),
            name="",
            created=now,
            type=StageType.SWISS,
        ),
        Ranking(
            id=RankingId(-1),
            tournament_id=tournament_id,
            created=now,
            win_points=Decimal("3.5"),
            draw_points=Decimal("1.25"),
            loss_points=Decimal("0.0"),
            add_score_points=False,
            position=0,
        ),
    )

    assert ranking == {
        -2: TeamStatistics(wins=0, draws=1, losses=1, points=Decimal("1208")),
        -1: TeamStatistics(wins=1, draws=1, losses=0, points=Decimal("1320")),
    }


def test_determine_ranking_for_stage_item_swiss_no_matches() -> None:
    tournament_id = TournamentId(-1)
    now = datetime_utc.now()
    stage_item_input1 = StageItemInputFinal(
        id=StageItemInputId(-1),
        team_id=TeamId(-1),
        slot=1,
        tournament_id=tournament_id,
        team=Team(**DUMMY_TEAM1.model_dump(), id=TeamId(-1)),
    )
    stage_item_input2 = StageItemInputFinal(
        id=StageItemInputId(-2),
        team_id=TeamId(-2),
        slot=1,
        tournament_id=tournament_id,
        team=Team(**DUMMY_TEAM2.model_dump(), id=TeamId(-2)),
    )

    ranking = determine_ranking_for_stage_item(
        StageItemWithRounds(
            rounds=[
                RoundWithMatches(
                    id=RoundId(-1),
                    matches=[],
                    stage_item_id=StageItemId(-1),
                    created=now,
                    is_draft=False,
                    name="",
                )
            ],
            inputs=[stage_item_input1, stage_item_input2],
            type_name="Swiss",
            team_count=2,
            ranking_id=None,
            id=StageItemId(-1),
            stage_id=StageId(-1),
            name="",
            created=now,
            type=StageType.SWISS,
        ),
        Ranking(
            id=RankingId(-1),
            tournament_id=tournament_id,
            created=now,
            win_points=Decimal("3.5"),
            draw_points=Decimal("1.25"),
            loss_points=Decimal("0.0"),
            add_score_points=False,
            position=0,
        ),
    )

    assert ranking == {
        -2: TeamStatistics(wins=0, draws=0, losses=0, points=Decimal("1200")),
        -1: TeamStatistics(wins=0, draws=0, losses=0, points=Decimal("1200")),
    }


def test_determine_ranking_for_stage_item_tennis_scores() -> None:
    tournament_id = TournamentId(-1)
    now = datetime_utc.now()
    stage_item_input1 = StageItemInputFinal(
        id=StageItemInputId(-1),
        team_id=TeamId(-1),
        slot=1,
        tournament_id=tournament_id,
        team=Team(**DUMMY_TEAM1.model_dump(), id=TeamId(-1)),
    )
    stage_item_input2 = StageItemInputFinal(
        id=StageItemInputId(-2),
        team_id=TeamId(-2),
        slot=1,
        tournament_id=tournament_id,
        team=Team(**DUMMY_TEAM2.model_dump(), id=TeamId(-2)),
    )

    ranking = determine_ranking_for_stage_item(
        StageItemWithRounds(
            rounds=[
                RoundWithMatches(
                    id=RoundId(-1),
                    matches=[
                        MatchWithDetailsDefinitive(
                            id=MatchId(-1),
                            stage_item_input1=stage_item_input1,
                            stage_item_input2=stage_item_input2,
                            created=now,
                            duration_minutes=90,
                            margin_minutes=15,
                            round_id=RoundId(-1),
                            stage_item_input1_score=0,
                            stage_item_input2_score=0,
                            scores=[
                                SetScore(team1_games=6, team2_games=4),
                                SetScore(team1_games=3, team2_games=6),
                                SetScore(
                                    team1_games=7,
                                    team2_games=6,
                                    team1_tiebreak=7,
                                    team2_tiebreak=3,
                                ),
                            ],
                            stage_item_input1_conflict=False,
                            stage_item_input2_conflict=False,
                        ),
                        MatchWithDetailsDefinitive(
                            id=MatchId(-2),
                            stage_item_input1=stage_item_input1,
                            stage_item_input2=stage_item_input2,
                            created=now,
                            duration_minutes=90,
                            margin_minutes=15,
                            round_id=RoundId(-1),
                            stage_item_input1_score=0,
                            stage_item_input2_score=0,
                            scores=[SetScore(team1_games=4, team2_games=6)],
                            stage_item_input1_conflict=False,
                            stage_item_input2_conflict=False,
                        ),
                    ],
                    stage_item_id=StageItemId(-1),
                    created=now,
                    is_draft=False,
                    name="",
                )
            ],
            inputs=[stage_item_input1, stage_item_input2],
            type_name="Round Robin",
            team_count=4,
            ranking_id=None,
            id=StageItemId(-1),
            stage_id=StageId(-1),
            name="",
            created=now,
            type=StageType.ROUND_ROBIN,
        ),
        Ranking(
            id=RankingId(-1),
            tournament_id=tournament_id,
            created=now,
            win_points=Decimal("3.5"),
            draw_points=Decimal("1.25"),
            loss_points=Decimal("0.0"),
            add_score_points=False,
            position=0,
        ),
    )

    assert ranking == {
        -2: TeamStatistics(wins=1, draws=0, losses=1, points=Decimal("3.5")),
        -1: TeamStatistics(wins=1, draws=0, losses=1, points=Decimal("3.5")),
    }


def test_determine_ranking_for_stage_item_tennis_add_score_points() -> None:
    tournament_id = TournamentId(-1)
    now = datetime_utc.now()
    stage_item_input1 = StageItemInputFinal(
        id=StageItemInputId(-1),
        team_id=TeamId(-1),
        slot=1,
        tournament_id=tournament_id,
        team=Team(**DUMMY_TEAM1.model_dump(), id=TeamId(-1)),
    )
    stage_item_input2 = StageItemInputFinal(
        id=StageItemInputId(-2),
        team_id=TeamId(-2),
        slot=1,
        tournament_id=tournament_id,
        team=Team(**DUMMY_TEAM2.model_dump(), id=TeamId(-2)),
    )

    ranking = determine_ranking_for_stage_item(
        StageItemWithRounds(
            rounds=[
                RoundWithMatches(
                    id=RoundId(-1),
                    matches=[
                        MatchWithDetailsDefinitive(
                            id=MatchId(-1),
                            stage_item_input1=stage_item_input1,
                            stage_item_input2=stage_item_input2,
                            created=now,
                            duration_minutes=90,
                            margin_minutes=15,
                            round_id=RoundId(-1),
                            stage_item_input1_score=0,
                            stage_item_input2_score=0,
                            scores=[
                                SetScore(team1_games=6, team2_games=4),
                                SetScore(team1_games=3, team2_games=6),
                                SetScore(team1_games=6, team2_games=2),
                            ],
                            stage_item_input1_conflict=False,
                            stage_item_input2_conflict=False,
                        ),
                    ],
                    stage_item_id=StageItemId(-1),
                    created=now,
                    is_draft=False,
                    name="",
                )
            ],
            inputs=[stage_item_input1, stage_item_input2],
            type_name="Round Robin",
            team_count=4,
            ranking_id=None,
            id=StageItemId(-1),
            stage_id=StageId(-1),
            name="",
            created=now,
            type=StageType.ROUND_ROBIN,
        ),
        Ranking(
            id=RankingId(-1),
            tournament_id=tournament_id,
            created=now,
            win_points=Decimal("3.5"),
            draw_points=Decimal("1.25"),
            loss_points=Decimal("0.0"),
            add_score_points=True,
            position=0,
        ),
    )

    assert ranking == {
        -2: TeamStatistics(wins=0, draws=0, losses=1, points=Decimal("12.0")),
        -1: TeamStatistics(wins=1, draws=0, losses=0, points=Decimal("18.5")),
    }


def test_determine_match_winner_index_tennis() -> None:
    now = datetime_utc.now()
    match = MatchWithDetails(
        id=MatchId(-1),
        created=now,
        duration_minutes=90,
        margin_minutes=15,
        round_id=RoundId(-1),
        stage_item_input1_score=0,
        stage_item_input2_score=0,
        scores=[
            SetScore(team1_games=6, team2_games=4),
            SetScore(team1_games=3, team2_games=6),
            SetScore(team1_games=7, team2_games=6, team1_tiebreak=7, team2_tiebreak=3),
        ],
        stage_item_input1_conflict=False,
        stage_item_input2_conflict=False,
    )
    assert determine_match_winner_index(match) == 0
    assert get_team_score_in_match(match, is_team1=True) == 16
    assert get_team_score_in_match(match, is_team1=False) == 16

    match_unfinished = match.model_copy(update={"scores": [SetScore(team1_games=4, team2_games=6)]})
    assert determine_match_winner_index(match_unfinished) == 1

    match_tied = match.model_copy(update={"scores": []})
    assert determine_match_winner_index(match_tied) is None

    match_standard = match.model_copy(update={"scores": None})
    assert determine_match_winner_index(match_standard) is None

    match_team2_wins_tiebreak = match.model_copy(
        update={
            "scores": [
                SetScore(team1_games=6, team2_games=6, team1_tiebreak=5, team2_tiebreak=7),
                SetScore(team1_games=6, team2_games=4),
            ]
        }
    )
    assert determine_match_winner_index(match_team2_wins_tiebreak) is None

    match_team1_wins_all_tiebreaks = match.model_copy(
        update={
            "scores": [
                SetScore(team1_games=6, team2_games=6, team1_tiebreak=7, team2_tiebreak=5),
                SetScore(team1_games=6, team2_games=6, team1_tiebreak=7, team2_tiebreak=4),
            ]
        }
    )
    assert determine_match_winner_index(match_team1_wins_all_tiebreaks) == 0


def test_determine_match_winner_index_standard() -> None:
    now = datetime_utc.now()
    match = MatchWithDetails(
        id=MatchId(-1),
        created=now,
        duration_minutes=90,
        margin_minutes=15,
        round_id=RoundId(-1),
        stage_item_input1_score=3,
        stage_item_input2_score=2,
        stage_item_input1_conflict=False,
        stage_item_input2_conflict=False,
    )
    assert determine_match_winner_index(match) == 0
    assert get_team_score_in_match(match, is_team1=True) == 3
    assert get_team_score_in_match(match, is_team1=False) == 2
