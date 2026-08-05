import { ScoringType } from '@openapi';

export type TournamentStatus = 'OPEN' | 'ARCHIVED';

export type TournamentFilter = 'ALL' | TournamentStatus;

export interface TournamentMinimal {
  id: number;
  scoring_type?: ScoringType;
  sets_to_win?: number;
}
