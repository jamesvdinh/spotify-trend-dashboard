export interface TasteTrack {
  id: string;
  name: string;
  artists: string;
  album_image: string | null;
  external_url: string | null;
  duration_ms: number;
  popularity: number;
}

export interface TasteMetrics {
  top_genre: { name: string; share: number } | null;
  top_artist: { name: string; image: string | null; external_url: string | null } | null;
  avg_popularity: number | null;
  unique_artist_count: number;
}

export interface TasteData {
  top_tracks: TasteTrack[];
  metrics: TasteMetrics;
}

export type TasteResult =
  | { status: "ok"; data: TasteData }
  | { status: "needs_reconnect" }
  | { status: "error" };
