import type { TasteTrack } from "../api";
import { formatClock } from "../format";

export default function TopTracksList({ tracks }: { tracks: TasteTrack[] }) {
  return (
    <ol className="top-tracks-list">
      {tracks.map((track, index) => (
        <li key={track.id} className="track-row">
          <span className="track-rank">{index + 1}</span>
          {track.album_image ? (
            <img className="track-art" src={track.album_image} alt="" />
          ) : (
            <div className="track-art-fallback" aria-hidden="true" />
          )}
          <div className="track-info">
            <span className="track-name">{track.name}</span>
            <span className="track-artists">{track.artists}</span>
          </div>
          <span className="track-duration">{formatClock(track.duration_ms)}</span>
          {track.external_url && (
            <a href={track.external_url} target="_blank" rel="noreferrer" aria-label={`Open ${track.name} in Spotify`}>
              ↗
            </a>
          )}
        </li>
      ))}
    </ol>
  );
}
