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
      <MainstreamGapRecharts rows={rows} />
    </div>
  );
}
