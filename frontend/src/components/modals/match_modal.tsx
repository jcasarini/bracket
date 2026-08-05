import {
  ActionIcon,
  Button,
  Center,
  Checkbox,
  Divider,
  Grid,
  Group,
  Modal,
  NumberInput,
  Text,
} from '@mantine/core';
import { useForm } from '@mantine/form';
import { IconX } from '@tabler/icons-react';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { SWRResponse } from 'swr';

import DeleteButton from '@components/buttons/delete';
import { formatMatchInput1, formatMatchInput2 } from '@components/utils/match';
import { TournamentMinimal } from '@components/utils/tournament';
import {
  MatchWithDetails,
  RoundWithMatches,
  SetScore,
  StagesWithStageItemsResponse,
} from '@openapi';
import { getMatchLookup, getStageItemLookup } from '@services/lookups';
import { deleteMatch, updateMatch } from '@services/match';

function MatchDeleteButton({
  tournamentData,
  match,
  swrStagesResponse,
  swrUpcomingMatchesResponse,
}: {
  tournamentData: TournamentMinimal;
  match: MatchWithDetails;
  swrStagesResponse: SWRResponse<StagesWithStageItemsResponse>;
  swrUpcomingMatchesResponse: SWRResponse | null;
}) {
  const { t } = useTranslation();
  return (
    <DeleteButton
      fullWidth
      onClick={async () => {
        await deleteMatch(tournamentData.id, match.id);
        await swrStagesResponse.mutate();
        if (swrUpcomingMatchesResponse != null) await swrUpcomingMatchesResponse.mutate();
      }}
      style={{ marginTop: '1rem' }}
      size="sm"
      title={t('remove_match_button')}
    />
  );
}

function SetScoreInputs({
  form,
  index,
  team1Name,
  team2Name,
}: {
  form: any;
  index: number;
  team1Name: string;
  team2Name: string;
}) {
  const { t } = useTranslation();
  return (
    <Grid align="flex-end" key={index} mt="sm">
      <Grid.Col span={2}>
        <Text fw={500}>
          {t('sets_label')} {index + 1}
        </Text>
      </Grid.Col>
      <Grid.Col span={3}>
        <NumberInput
          label={team1Name}
          min={0}
          value={form.values.scores[index].team1_games}
          onChange={(value) =>
            form.setFieldValue(`scores.${index}.team1_games`, value === '' ? 0 : Number(value))
          }
        />
      </Grid.Col>
      <Grid.Col span={3}>
        <NumberInput
          label={team2Name}
          min={0}
          value={form.values.scores[index].team2_games}
          onChange={(value) =>
            form.setFieldValue(`scores.${index}.team2_games`, value === '' ? 0 : Number(value))
          }
        />
      </Grid.Col>
      <Grid.Col span={4}>
        <Group align="flex-end" wrap="nowrap">
          <NumberInput
            label={t('tiebreak_label')}
            placeholder="-"
            min={0}
            value={form.values.scores[index].team1_tiebreak ?? undefined}
            onChange={(value) =>
              form.setFieldValue(
                `scores.${index}.team1_tiebreak`,
                value === '' ? null : Number(value),
              )
            }
          />
          <Text pb="sm">:</Text>
          <NumberInput
            label={t('tiebreak_label')}
            placeholder="-"
            min={0}
            value={form.values.scores[index].team2_tiebreak ?? undefined}
            onChange={(value) =>
              form.setFieldValue(
                `scores.${index}.team2_tiebreak`,
                value === '' ? null : Number(value),
              )
            }
          />
        </Group>
      </Grid.Col>
      <Grid.Col span={2}>
        <Center>
          <ActionIcon
            variant="outline"
            color="red"
            aria-label={`${t('remove_set_button')} ${index + 1}`}
            onClick={() => form.removeListItem('scores', index)}
          >
            <IconX size={16} />
          </ActionIcon>
        </Center>
      </Grid.Col>
    </Grid>
  );
}

function MatchModalForm({
  tournamentData,
  match,
  swrStagesResponse,
  swrUpcomingMatchesResponse,
  setOpened,
  round,
}: {
  tournamentData: TournamentMinimal;
  match: MatchWithDetails | null;
  swrStagesResponse: SWRResponse<StagesWithStageItemsResponse>;
  swrUpcomingMatchesResponse: SWRResponse | null;
  setOpened: any;
  round: RoundWithMatches | null;
}) {
  if (match == null) {
    return null;
  }

  const { t } = useTranslation();
  const isTennis = tournamentData.scoring_type === 'TENNIS';
  const setsToWin = tournamentData.sets_to_win ?? 2;
  const maxSets = setsToWin * 2 - 1;
  const form = useForm({
    initialValues: {
      stage_item_input1_score: match.stage_item_input1_score,
      stage_item_input2_score: match.stage_item_input2_score,
      scores: (match.scores ?? []).map((setScore) => ({ ...setScore })),
      custom_duration_minutes: match.custom_duration_minutes,
      custom_margin_minutes: match.custom_margin_minutes,
    },

    validate: {
      stage_item_input1_score: (value) => (value >= 0 ? null : t('negative_score_validation')),
      stage_item_input2_score: (value) => (value >= 0 ? null : t('negative_score_validation')),
      scores: (value: SetScore[]) => {
        for (const setScore of value) {
          if ((setScore.team1_tiebreak == null) !== (setScore.team2_tiebreak == null)) {
            return t('tiebreak_pair_validation');
          }
        }
        return null;
      },
      custom_duration_minutes: (value) =>
        value == null || value >= 0 ? null : t('negative_match_duration_validation'),
      custom_margin_minutes: (value) =>
        value == null || value >= 0 ? null : t('negative_match_margin_validation'),
    },
  });

  const [customDurationEnabled, setCustomDurationEnabled] = useState(
    match.custom_duration_minutes != null,
  );
  const [customMarginEnabled, setCustomMarginEnabled] = useState(
    match.custom_margin_minutes != null,
  );

  const stageItemsLookup = getStageItemLookup(swrStagesResponse);
  const matchesLookup = getMatchLookup(swrStagesResponse);

  const team1Name = formatMatchInput1(t, stageItemsLookup, matchesLookup, match);
  const team2Name = formatMatchInput2(t, stageItemsLookup, matchesLookup, match);

  const scoreInputs = isTennis ? (
    <>
      {form.values.scores.map((_: SetScore, index: number) => (
        <SetScoreInputs
          key={index}
          form={form}
          index={index}
          team1Name={team1Name}
          team2Name={team2Name}
        />
      ))}
      <Button
        fullWidth
        mt="lg"
        variant="outline"
        color="indigo"
        disabled={form.values.scores.length >= maxSets}
        onClick={() =>
          form.insertListItem('scores', {
            team1_games: 0,
            team2_games: 0,
            team1_tiebreak: null,
            team2_tiebreak: null,
          })
        }
      >
        {t('add_set_button')}
      </Button>
    </>
  ) : (
    <>
      <NumberInput
        withAsterisk
        label={`${t('score_of_label')} ${team1Name}`}
        placeholder={`${t('score_of_label')} ${team1Name}`}
        {...form.getInputProps('stage_item_input1_score')}
      />
      <NumberInput
        withAsterisk
        mt="lg"
        label={`${t('score_of_label')} ${team2Name}`}
        placeholder={`${t('score_of_label')} ${team2Name}`}
        {...form.getInputProps('stage_item_input2_score')}
      />
    </>
  );

  return (
    <>
      <form
        onSubmit={form.onSubmit(async (values) => {
          const scores = (values.scores ?? []).map((setScore) => ({
            team1_games: Number(setScore.team1_games) || 0,
            team2_games: Number(setScore.team2_games) || 0,
            team1_tiebreak:
              setScore.team1_tiebreak == null ? null : Number(setScore.team1_tiebreak),
            team2_tiebreak:
              setScore.team2_tiebreak == null ? null : Number(setScore.team2_tiebreak),
          }));
          const team1Score = scores.reduce((sum, setScore) => sum + setScore.team1_games, 0);
          const team2Score = scores.reduce((sum, setScore) => sum + setScore.team2_games, 0);
          const updatedMatch = {
            id: match.id,
            round_id: match.round_id,
            stage_item_input1_score: isTennis ? team1Score : values.stage_item_input1_score,
            stage_item_input2_score: isTennis ? team2Score : values.stage_item_input2_score,
            scores: isTennis && scores.length > 0 ? scores : null,
            court_id: match.court_id || null,
            custom_duration_minutes: customDurationEnabled ? values.custom_duration_minutes : null,
            custom_margin_minutes: customMarginEnabled ? values.custom_margin_minutes : null,
          };
          await updateMatch(tournamentData.id, match.id, updatedMatch);
          await swrStagesResponse.mutate();
          if (swrUpcomingMatchesResponse != null) await swrUpcomingMatchesResponse.mutate();
          setOpened(false);
        })}
      >
        {scoreInputs}
        <Divider mt="lg" />

        <Text size="sm" mt="lg">
          {t('custom_match_duration_label')}
        </Text>
        <Grid align="center">
          <Grid.Col span={{ sm: 8 }}>
            <NumberInput
              disabled={!customDurationEnabled}
              rightSection={<Text>{t('minutes')}</Text>}
              placeholder={`${match.duration_minutes}`}
              rightSectionWidth={92}
              {...form.getInputProps('custom_duration_minutes')}
            />
          </Grid.Col>
          <Grid.Col span={{ sm: 4 }}>
            <Center>
              <Checkbox
                checked={customDurationEnabled}
                label={t('customize_checkbox_label')}
                onChange={(event) => {
                  setCustomDurationEnabled(event.currentTarget.checked);
                }}
              />
            </Center>
          </Grid.Col>
        </Grid>

        <Text size="sm" mt="lg">
          {t('custom_match_margin_label')}
        </Text>
        <Grid align="center">
          <Grid.Col span={{ sm: 8 }}>
            <NumberInput
              disabled={!customMarginEnabled}
              placeholder={`${match.margin_minutes}`}
              rightSection={<Text>{t('minutes')}</Text>}
              rightSectionWidth={92}
              {...form.getInputProps('custom_margin_minutes')}
            />
          </Grid.Col>
          <Grid.Col span={{ sm: 4 }}>
            <Center>
              <Checkbox
                checked={customMarginEnabled}
                label={t('customize_checkbox_label')}
                onChange={(event) => {
                  setCustomMarginEnabled(event.currentTarget.checked);
                }}
              />
            </Center>
          </Grid.Col>
        </Grid>

        <Button fullWidth style={{ marginTop: 20 }} color="green" type="submit">
          {t('save_button')}
        </Button>
      </form>
      {round && round.is_draft && (
        <MatchDeleteButton
          swrStagesResponse={swrStagesResponse}
          swrUpcomingMatchesResponse={swrUpcomingMatchesResponse}
          tournamentData={tournamentData}
          match={match}
        />
      )}
    </>
  );
}

export default function MatchModal({
  tournamentData,
  match,
  swrStagesResponse,
  swrUpcomingMatchesResponse,
  opened,
  setOpened,
  round,
}: {
  tournamentData: TournamentMinimal;
  match: MatchWithDetails | null;
  swrStagesResponse: SWRResponse<StagesWithStageItemsResponse>;
  swrUpcomingMatchesResponse: SWRResponse | null;
  opened: boolean;
  setOpened: any;
  round: RoundWithMatches | null;
}) {
  const { t } = useTranslation();

  return (
    <>
      <Modal opened={opened} onClose={() => setOpened(false)} title={t('edit_match_modal_title')}>
        <MatchModalForm
          swrStagesResponse={swrStagesResponse}
          swrUpcomingMatchesResponse={swrUpcomingMatchesResponse}
          tournamentData={tournamentData}
          match={match}
          setOpened={setOpened}
          round={round}
        />
      </Modal>
    </>
  );
}
