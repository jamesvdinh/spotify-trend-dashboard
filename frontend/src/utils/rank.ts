import type { PersonalVsGlobalRow } from "./types/trends";

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
