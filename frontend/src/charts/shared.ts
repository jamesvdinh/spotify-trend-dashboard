import type { PersonalVsGlobalRow, TimeRange } from "../api";

// Validated against this app's dark chart surface (#121212) with the dataviz
// skill's validator - both pairs pass lightness/chroma/CVD/contrast checks.
export const CHART_COLORS = {
  personal: "#008300", // identity: the user's own top artists
  global: "#3987e5", // identity: the Kworb global leaderboard
  divergingPositive: "#3987e5", // diverging pole: more mainstream than personal rank suggests
  divergingNegative: "#e66767", // diverging pole: bigger personal favorite than its global fame
  neutral: "#898781",
} as const;

export const TIME_RANGE_LABELS: Record<TimeRange, string> = {
  short_term: "Last 4 weeks",
  medium_term: "Last 6 months",
  long_term: "All time",
};

export const TIME_RANGES: TimeRange[] = ["short_term", "medium_term", "long_term"];

// The user's top-artists snapshot is fetched with limit=50 (see
// backend/ingestion/spotify_snapshot.py), so 50 is the personal ranking's fixed
// universe size.
export const PERSONAL_UNIVERSE_SIZE = 50;

/** Largest global_rank present in the rows - a proxy for the global chart's
 * universe size (Kworb's leaderboard covers ~3000 artists; using the observed
 * max keeps the normalization honest about what we actually queried). */
export function maxGlobalRank(rows: PersonalVsGlobalRow[]): number {
  return rows.reduce((max, r) => Math.max(max, r.global_rank), 1);
}

/** Normalizes a rank to 0..1 within its universe, where 1 = best possible rank (#1). */
export function rankFraction(rank: number, universeMax: number): number {
  if (universeMax <= 1) return 1;
  return 1 - (rank - 1) / (universeMax - 1);
}
