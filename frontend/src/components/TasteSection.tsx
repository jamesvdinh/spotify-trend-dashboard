import { useEffect, useState } from "react";
import { fetchTaste, loginUrl, type TasteData } from "../api";
import StatTile from "./StatTile";
import PopularityMeter from "./PopularityMeter";
import TopTracksList from "./TopTracksList";

type Status = "loading" | "ready" | "needs_reconnect" | "error";

export default function TasteSection() {
  const [status, setStatus] = useState<Status>("loading");
  const [data, setData] = useState<TasteData | null>(null);

  useEffect(() => {
    fetchTaste().then((result) => {
      if (result.status === "ok") {
        setData(result.data);
        setStatus("ready");
      } else {
        setStatus(result.status);
      }
    });
  }, []);

  if (status === "loading") {
    return (
      <div className="taste-section">
        <p className="status-text">Loading your taste…</p>
      </div>
    );
  }

  if (status === "needs_reconnect") {
    return (
      <div className="taste-section">
        <div className="reconnect-card">
          <p>
            Showing your top tracks needs an extra permission your account hasn't
            granted yet.
          </p>
          <a className="btn-spotify" href={loginUrl()}>
            Reconnect Spotify
          </a>
        </div>
      </div>
    );
  }

  if (status === "error" || data === null) {
    return (
      <div className="taste-section">
        <p className="error-text">Couldn't load your taste data.</p>
      </div>
    );
  }

  const { metrics, top_tracks } = data;

  return (
    <div className="taste-section">
      <div className="stat-grid">
        <StatTile
          label="Top genre"
          value={metrics.top_genre?.name ?? "Not enough data"}
          hint={metrics.top_genre ? `${metrics.top_genre.share}% of your top artists` : undefined}
        />
        <StatTile label="Top artist" value={metrics.top_artist?.name ?? "Not enough data"} />
        {metrics.avg_popularity !== null && <PopularityMeter value={metrics.avg_popularity} />}
        <StatTile label="Unique artists" value={String(metrics.unique_artist_count)} hint="in your top tracks" />
      </div>

      <div>
        <h2 className="section-title">Top 5 Tracks</h2>
        <TopTracksList tracks={top_tracks} />
      </div>
    </div>
  );
}
