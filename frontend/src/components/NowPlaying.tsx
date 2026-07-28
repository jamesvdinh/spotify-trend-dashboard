import { useEffect, useState } from "react";
import { fetchNowPlaying } from "../api";
import type { NowPlayingData } from "../utils/types/nowPlaying";

type Status = "loading" | "ready" | "error";

const POLL_INTERVAL_MS = 5_000;

export default function NowPlaying() {
  const [status, setStatus] = useState<Status>("loading");
  const [data, setData] = useState<NowPlayingData | null>(null);

  useEffect(() => {
    let cancelled = false;

    const poll = () => {
      fetchNowPlaying()
        .then((result) => {
          if (cancelled) return;
          if (result) {
            setData(result);
            setStatus("ready");
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

  if (status === "loading" || status === "error" || data === null) {
    return null;
  }

  if (!data.is_playing || !data.track_name) {
    return (
      <div className="taste-section">
        <p className="status-text">Nothing playing right now.</p>
      </div>
    );
  }

  return (
    <div className="taste-section">
      <h2 className="section-title">Now playing</h2>
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
    </div>
  );
}
