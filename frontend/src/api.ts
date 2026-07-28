import type { SpotifyProfile } from "./utils/types/profile";
import type { TasteResult } from "./utils/types/taste";
import type { TrendsData } from "./utils/types/trends";
import type { RawEndpointResult } from "./utils/types/apiExplorer";

export const BACKEND_URL = import.meta.env.VITE_BACKEND_URL ?? "http://127.0.0.1:8000";

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

export async function heartbeat(): Promise<void> {
  await fetch(`${BACKEND_URL}/api/heartbeat`, {
    method: "POST",
    credentials: "include",
  });
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

export async function fetchTrends(): Promise<TrendsData | null> {
  const response = await fetch(`${BACKEND_URL}/api/trends`, {
    credentials: "include",
  });
  if (!response.ok) {
    return null;
  }
  return response.json();
}

/**
 * Hits an endpoint directly and returns its raw status + body, bypassing the
 * typed fetchers above - used by the API explorer view so it shows exactly
 * what the backend returns (including error responses), not a parsed shape.
 */
export async function fetchRaw(path: string): Promise<RawEndpointResult> {
  const response = await fetch(`${BACKEND_URL}${path}`, { credentials: "include" });
  let body: unknown = null;
  try {
    body = await response.json();
  } catch {
    // non-JSON or empty body - leave as null
  }
  return { path, status: response.status, ok: response.ok, body };
}
