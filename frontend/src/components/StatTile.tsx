import type { ReactNode } from "react";

interface StatTileProps {
  label: string;
  value: string;
  hint?: string;
  children?: ReactNode;
}

export default function StatTile({ label, value, hint, children }: StatTileProps) {
  return (
    <div className="stat-tile">
      <span className="stat-tile-label">{label}</span>
      <span className="stat-tile-value">{value}</span>
      {children}
      {hint && <span className="stat-tile-hint">{hint}</span>}
    </div>
  );
}
