export const BACKEND_URL = import.meta.env.VITE_BACKEND_URL ?? "http://127.0.0.1:8000";

export interface SpotifyProfile {
  id: string;
  display_name: string | null;
  email: string | null;
  product: string | null;
  followers: number | null;
  images: { url: string; height: number | null; width: number | null }[];
  external_url: string | null;
  country: string | null;
}

export async function fetchProfile(): Promise<SpotifyProfile | null> {
  const response = await fetch(`${BACKEND_URL}/api/me`, {
    credentials: "include",
  });

  if (response.status === 401) {
    return null;
  }
  if (!response.ok) {
    throw new Error(`Failed to load profile: ${response.status}`);
  }
  return response.json();
}

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

export async function fetchTaste(): Promise<TasteResult> {
  const response = await fetch(`${BACKEND_URL}/api/taste`, {
    credentials: "include",
  });

  if (response.status === 409) {
    return { status: "needs_reconnect" };
  }
  if (!response.ok) {
    return { status: "error" };
  }
  return { status: "ok", data: await response.json() };
}

export async function logout(): Promise<void> {
  await fetch(`${BACKEND_URL}/auth/logout`, {
    method: "POST",
    credentials: "include",
  });
}

export function loginUrl(): string {
  return `${BACKEND_URL}/auth/login`;
}
