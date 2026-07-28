export interface NowPlayingData {
  is_playing: boolean;
  track_id?: string | null;
  track_name?: string | null;
  artist_names?: string | null;
  album_image_url?: string | null;
  progress_ms?: number | null;
  duration_ms?: number | null;
}
