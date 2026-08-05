import { MatchWithDetails } from '@openapi';
import dayjs from 'dayjs';
import { formatStageItemInput } from './stage_item_input';
import { Translator } from './types';

export interface SchedulerSettings {
  eloThreshold: number;
  setEloThreshold: any;
  limit: number;
  setLimit: any;
  iterations: number;
  setIterations: any;
  onlyRecommended: string;
  setOnlyRecommended: any;
}

export function getMatchStartTime(match: MatchWithDetails) {
  return dayjs(match.start_time || '');
}

export function getSetsWon(match: MatchWithDetails, isTeam1: boolean): number {
  if (match.scores == null) return 0;
  return match.scores.filter((setScore) => {
    if (setScore.team1_games !== setScore.team2_games) {
      return isTeam1
        ? setScore.team1_games > setScore.team2_games
        : setScore.team2_games > setScore.team1_games;
    }
    const team1Tiebreak = setScore.team1_tiebreak;
    const team2Tiebreak = setScore.team2_tiebreak;
    if (team1Tiebreak == null || team2Tiebreak == null || team1Tiebreak === team2Tiebreak) {
      return false;
    }
    return isTeam1 ? team1Tiebreak > team2Tiebreak : team2Tiebreak > team1Tiebreak;
  }).length;
}

export function getMatchScoreString(match: MatchWithDetails, isTeam1: boolean): string {
  if (match.scores != null && match.scores.length > 0) {
    return match.scores
      .map((setScore) => {
        const games = isTeam1 ? setScore.team1_games : setScore.team2_games;
        const tiebreak = isTeam1 ? setScore.team1_tiebreak : setScore.team2_tiebreak;
        return tiebreak != null ? `${games}(${tiebreak})` : `${games}`;
      })
      .join(' ');
  }
  return String(isTeam1 ? match.stage_item_input1_score : match.stage_item_input2_score);
}

export function getMatchWinnerIndex(match: MatchWithDetails): 0 | 1 | null {
  if (match.scores != null && match.scores.length > 0) {
    const team1Sets = getSetsWon(match, true);
    const team2Sets = getSetsWon(match, false);
    if (team1Sets > team2Sets) return 0;
    if (team2Sets > team1Sets) return 1;
    return null;
  }
  if (match.stage_item_input1_score > match.stage_item_input2_score) return 0;
  if (match.stage_item_input2_score > match.stage_item_input1_score) return 1;
  return null;
}

export function getMatchEndTime(match: MatchWithDetails) {
  return getMatchStartTime(match).add(match.duration_minutes + match.margin_minutes, 'minutes');
}

export function isMatchHappening(match: MatchWithDetails) {
  return getMatchStartTime(match) < dayjs() && getMatchEndTime(match) > dayjs();
}

export function isMatchInTheFutureOrPresent(match: MatchWithDetails) {
  return getMatchEndTime(match) > dayjs();
}

export function isMatchInTheFuture(match: MatchWithDetails) {
  return getMatchStartTime(match) > dayjs();
}

export function formatMatchInput1(
  t: Translator,
  stageItemsLookup: any,
  matchesLookup: any,
  match: MatchWithDetails,
): string {
  const formatted = formatStageItemInput(match.stage_item_input1, stageItemsLookup);
  if (formatted != null) return formatted;

  if (match.stage_item_input1_winner_from_match_id == null) {
    return t('empty_slot');
  }
  const winner = matchesLookup[match.stage_item_input1_winner_from_match_id].match;
  const match_1 = formatMatchInput1(t, stageItemsLookup, matchesLookup, winner);
  const match_2 = formatMatchInput2(t, stageItemsLookup, matchesLookup, winner);
  return `Winner of match ${match_1} - ${match_2}`;
}

export function formatMatchInput2(
  t: Translator,
  stageItemsLookup: any,
  matchesLookup: any,
  match: MatchWithDetails,
): string {
  const formatted = formatStageItemInput(match.stage_item_input2, stageItemsLookup);
  if (formatted != null) return formatted;

  if (match.stage_item_input2_winner_from_match_id == null) {
    return t('empty_slot');
  }
  const winner = matchesLookup[match.stage_item_input2_winner_from_match_id].match;
  const match_1 = formatMatchInput1(t, stageItemsLookup, matchesLookup, winner);
  const match_2 = formatMatchInput2(t, stageItemsLookup, matchesLookup, winner);
  return `Winner of match ${match_1} - ${match_2}`;
}
