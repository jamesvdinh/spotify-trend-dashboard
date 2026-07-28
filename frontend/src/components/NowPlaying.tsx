import { useEffect, useState } from "react";
import { fetchNowPlaying } from "../api";
import type { NowPlayingData } from "../utils/types/nowPlaying";

type Status = "loading" | "ready" | "error";

const POLL_INTERVAL_MS = 5_000;
const CLOCK_TICK_MS = 1_000;

function formatSecondsAgo(lastUpdatedAt: number, now: number): string {
  const seconds = Math.max(0, Math.round((now - lastUpdatedAt) / 1000));
  if (seconds < 1) return "just now";
  if (seconds === 1) return "1s ago";
  return `${seconds}s ago`;
}

export default function NowPlaying() {
  const [status, setStatus] = useState<Status>("loading");
  const [data, setData] = useState<NowPlayingData | null>(null);
  const [lastUpdatedAt, setLastUpdatedAt] = useState<number | null>(null);
  const [now, setNow] = useState(() => Date.now());

  useEffect(() => {
    let cancelled = false;

    const poll = () => {
      fetchNowPlaying()
        .then((result) => {
          if (cancelled) return;
          if (result) {
            setData(result);
            setStatus("ready");
            setLastUpdatedAt(Date.now());
          } else {
            setStatus("error");
          }
        })
        .catch(() => {
          if (!cancelled) setStatus("error");
        });
    };

    poll();
    const intervalId = setInterval(poll, POLL_INTERVAL_MS);
    return () => {
      cancelled = true;
      clearInterval(intervalId);
    };
  }, []);

  // Ticks the "updated Xs ago" text independently of the poll cadence, so it
  // counts up smoothly instead of jumping every 5s.
  useEffect(() => {
    const tickId = setInterval(() => setNow(Date.now()), CLOCK_TICK_MS);
    return () => clearInterval(tickId);
  }, []);

  if (status === "loading") {
    return null;
  }

  if (status === "error") {
    return (
      <div className="taste-section">
        <div className="now-playing-header">
          <h2 className="section-title">Now playing</h2>
          <span className="now-playing-status now-playing-status-offline">
            <span className="now-playing-dot now-playing-dot-offline" />
            Disconnected
          </span>
        </div>
        <p className="status-text">Couldn't reach the live now-playing feed.</p>
      </div>
    );
  }

  return (
    <div className="taste-section">
      <div className="now-playing-header">
        <h2 className="section-title">Now playing</h2>
        <span className="now-playing-status">
          <span className="now-playing-dot" />
          Live{lastUpdatedAt !== null && ` · updated ${formatSecondsAgo(lastUpdatedAt, now)}`}
        </span>
      </div>

      {data?.is_playing && data.track_name ? (
        <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
          {data.album_image_url && (
            <img
              src={data.album_image_url}
              alt={data.track_name}
              style={{ width: 56, height: 56, borderRadius: 4 }}
            />
          )}
          <p className="status-text">
            {data.track_name} — {data.artist_names}
          </p>
        </div>
      ) : (
        <p className="status-text">Nothing playing right now.</p>
      )}
    </div>
  );
}
