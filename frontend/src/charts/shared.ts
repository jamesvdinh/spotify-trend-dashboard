import type { TimeRange } from "../utils/types/trends";

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
