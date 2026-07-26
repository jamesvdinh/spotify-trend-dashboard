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

export async function logout(): Promise<void> {
  await fetch(`${BACKEND_URL}/auth/logout`, {
    method: "POST",
    credentials: "include",
  });
}

export function loginUrl(): string {
  return `${BACKEND_URL}/auth/login`;
}
