import { useEffect, useState } from "react";
import { fetchRaw, type RawEndpointResult } from "../api";

const ENDPOINTS = [
  { path: "/api/me", label: "Your Spotify profile" },
  { path: "/api/taste", label: "Live top tracks + taste metrics, straight from the Spotify API" },
  { path: "/api/trends", label: "Personal vs. global trend, from BigQuery via the dbt marts" },
];

export default function ApiExplorer() {
  const [results, setResults] = useState<Record<string, RawEndpointResult | "loading">>({});

  useEffect(() => {
    ENDPOINTS.forEach(({ path }) => {
      setResults((prev) => ({ ...prev, [path]: "loading" }));
      fetchRaw(path).then((result) => {
        setResults((prev) => ({ ...prev, [path]: result }));
      });
    });
  }, []);

  return (
    <div className="api-explorer">
      <h2 className="section-title">What the backend exposes</h2>
      <div className="api-steps">
        {ENDPOINTS.map(({ path, label }, index) => {
          const result = results[path];
          const loading = result === undefined || result === "loading";

          return (
            <div className="api-card" key={path}>
              <div className="api-card-header">
                <span className="api-step-number">{index + 1}</span>
                <div className="api-card-heading">
                  <div className="api-endpoint">GET {path}</div>
                  <div className="api-label">{label}</div>
                </div>
                {!loading && (
                  <span className={`api-status ${result.ok ? "api-status-ok" : "api-status-error"}`}>
                    {result.status}
                  </span>
                )}
              </div>
              <pre className="api-json">{loading ? "Loading…" : JSON.stringify(result.body, null, 2)}</pre>
            </div>
          );
        })}
      </div>
    </div>
  );
}
