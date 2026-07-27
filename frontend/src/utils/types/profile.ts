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
