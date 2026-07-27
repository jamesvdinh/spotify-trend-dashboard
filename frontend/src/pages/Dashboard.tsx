import { useEffect, useState } from "react";
import { Navigate } from "react-router-dom";
import { fetchProfile, logout, type SpotifyProfile } from "../api";
import ProfileCard from "../components/ProfileCard";
import TasteSection from "../components/TasteSection";
import TrendsSection from "../components/TrendsSection";
// import ApiExplorer from "../components/ApiExplorer";

type Status = "loading" | "authed" | "unauthed" | "error";

export default function Dashboard() {
  const [status, setStatus] = useState<Status>("loading");
  const [profile, setProfile] = useState<SpotifyProfile | null>(null);

  useEffect(() => {
    fetchProfile()
      .then((result) => {
        if (result) {
          setProfile(result);
          setStatus("authed");
        } else {
          setStatus("unauthed");
        }
      })
      .catch(() => setStatus("error"));
  }, []);

  if (status === "loading") {
    return (
      <div className="page">
        <p className="status-text">Loading your Spotify profile…</p>
      </div>
    );
  }

  if (status === "unauthed") {
    return <Navigate to="/" replace />;
  }

  if (status === "error" || profile === null) {
    return (
      <div className="page">
        <p className="error-text">
          Couldn't load your profile. Is the backend running?
        </p>
      </div>
    );
  }

  return (
    <div className="page">
      <div className="dashboard">
        <ProfileCard profile={profile} />
        <TasteSection />
        {/* <ApiExplorer /> */}
        <TrendsSection />
        <div className="dashboard-actions">
          <span className="status-text">Connected to Spotify</span>
          <button
            className="btn-ghost"
            onClick={async () => {
              await logout();
              setStatus("unauthed");
            }}
          >
            Log out
          </button>
        </div>
      </div>
    </div>
  );
}
