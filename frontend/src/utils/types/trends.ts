export type TimeRange = "short_term" | "medium_term" | "long_term";

export interface PersonalVsGlobalRow {
  time_range: TimeRange;
  snapshot_date: string;
  artist_id: string;
  artist_name: string;
  personal_rank: number;
  global_rank: number;
  global_rank_change_7d: number | null;
  global_daily_streams_millions: number | null;
}

export interface TrendsData {
  personal_vs_global: PersonalVsGlobalRow[];
}
