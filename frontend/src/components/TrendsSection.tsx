import { useEffect, useState } from "react";
import { fetchTrends, type PersonalVsGlobalRow } from "../api";
import MainstreamGapRecharts from "../charts/MainstreamGapRecharts";

type Status = "loading" | "ready" | "error";

export default function TrendsSection() {
  const [status, setStatus] = useState<Status>("loading");
  const [rows, setRows] = useState<PersonalVsGlobalRow[]>([]);

  useEffect(() => {
    fetchTrends().then((data) => {
      if (data) {
        setRows(data.personal_vs_global);
        setStatus("ready");
      } else {
        setStatus("error");
      }
    });
  }, []);

  if (status === "loading") {
    return (
      <div className="taste-section">
        <p className="status-text">Loading your trend data…</p>
      </div>
    );
  }

  if (status === "error") {
    return (
      <div className="taste-section">
        <p className="error-text">Couldn't load trend data.</p>
      </div>
    );
  }

  return (
    <div className="taste-section">
      <h2 className="section-title">Your taste vs. the world</h2>
      <p className="status-text">
        A single derived number per artist: how much more (or less) mainstream they are globally than your own
        ranking implies. Red bars are bigger favorites for you than their global fame; blue bars are more mainstream
        than your ranking suggests.
      </p>
      <MainstreamGapRecharts rows={rows} />
    </div>
  );
}
