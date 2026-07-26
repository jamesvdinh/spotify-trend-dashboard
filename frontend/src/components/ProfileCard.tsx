import type { SpotifyProfile } from "../api";

export default function ProfileCard({ profile }: { profile: SpotifyProfile }) {
  const avatarUrl = profile.images?.[0]?.url;
  const initial = (profile.display_name ?? profile.id ?? "?").charAt(0).toUpperCase();

  return (
    <div className="profile-card">
      {avatarUrl ? (
        <img className="profile-avatar" src={avatarUrl} alt="" />
      ) : (
        <div className="profile-avatar-fallback">{initial}</div>
      )}
      <div className="profile-info">
        <span className="profile-eyebrow">Profile</span>
        <h1 className="profile-name">{profile.display_name ?? profile.id}</h1>
        <div className="profile-meta">
          {profile.product && <span className="badge">{profile.product}</span>}
          {profile.email && <span>{profile.email}</span>}
          {profile.followers !== null && <span>{profile.followers} followers</span>}
          {profile.country && <span>{profile.country}</span>}
        </div>
        {profile.external_url && (
          <a className="btn-ghost" style={{ width: "fit-content", marginTop: "0.5rem" }} href={profile.external_url} target="_blank" rel="noreferrer">
            Open in Spotify
          </a>
        )}
      </div>
    </div>
  );
}
