import { useMemo, useState } from "react";
import {
  Bar,
  BarChart,
  Rectangle,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { TooltipContentProps } from "recharts/types/component/Tooltip";
import type { BarShapeProps } from "recharts/types/cartesian/Bar";
import type { PersonalVsGlobalRow, TimeRange } from "../utils/types/trends";
import { maxGlobalRank, rankFraction } from "../utils/rank";
import { CHART_COLORS, PERSONAL_UNIVERSE_SIZE } from "./shared";
import TimeRangeTabs from "./TimeRangeTabs";

const TOP_N = 20;

interface GapDatum {
  artist_id: string;
  name: string;
  gap: number;
  personal_rank: number;
  global_rank: number;
}

function GapTooltip({ active, payload }: TooltipContentProps) {
  if (!active || !payload || payload.length === 0) return null;
  const d = payload[0].payload as GapDatum;
  return (
    <div className="chart-tooltip chart-tooltip-static">
      <div className="chart-tooltip-title">{d.name}</div>
      <div className="chart-tooltip-row">
        <span>Your rank</span>
        <strong>#{d.personal_rank}</strong>
      </div>
      <div className="chart-tooltip-row">
        <span>Global rank</span>
        <strong>#{d.global_rank}</strong>
      </div>
    </div>
  );
}

export default function MainstreamGapRecharts({
  rows,
}: {
  rows: PersonalVsGlobalRow[];
}) {
  const [timeRange, setTimeRange] = useState<TimeRange>("long_term");

  const data = useMemo<GapDatum[]>(() => {
    const filtered = rows.filter((r) => r.time_range === timeRange);
    const globalMax = maxGlobalRank(filtered);

    const withGap = filtered.map((r) => ({
      artist_id: r.artist_id,
      name: r.artist_name,
      // positive = more mainstream globally than your ranking suggests
      // negative = bigger personal favorite than its global fame ("hidden gem")
      gap:
        rankFraction(r.global_rank, globalMax) -
        rankFraction(r.personal_rank, PERSONAL_UNIVERSE_SIZE),
      personal_rank: r.personal_rank,
      global_rank: r.global_rank,
    }));

    return withGap
      .sort((a, b) => Math.abs(b.gap) - Math.abs(a.gap))
      .slice(0, TOP_N)
      .sort((a, b) => a.gap - b.gap);
  }, [rows, timeRange]);

  const rowHeight = 28;
  // Fixed to the max possible row count (not data.length) so the container
  // never resizes between tabs - ResponsiveContainer needs a tick to
  // re-measure via ResizeObserver on a size change, and that gap between the
  // DOM resizing and Recharts catching up is what caused the visible jerk.
  const height = TOP_N * rowHeight + 40;

  return (
    <div>
      <TimeRangeTabs value={timeRange} onChange={setTimeRange} />
      <div className="chart-legend">
        <span className="chart-legend-item">
          <span
            className="chart-legend-dot"
            style={{ background: CHART_COLORS.divergingNegative }}
          />
          Bigger favorite for you than its fame
        </span>
        <span className="chart-legend-item">
          <span
            className="chart-legend-dot"
            style={{ background: CHART_COLORS.divergingPositive }}
          />
          More mainstream than your ranking
        </span>
      </div>
      <div className="chart-canvas" style={{ height }}>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={data}
            layout="vertical"
            margin={{ top: 8, right: 24, bottom: 8, left: 8 }}
          >
            <XAxis
              type="number"
              domain={[-1, 1]}
              tick={{ fill: "var(--spotify-text-subdued)", fontSize: 11 }}
              stroke="var(--spotify-border)"
              tickFormatter={() => ""}
            />
            <YAxis
              type="category"
              dataKey="name"
              width={130}
              tick={{ fill: "var(--spotify-text-subdued)", fontSize: 11 }}
              stroke="var(--spotify-border)"
            />
            <ReferenceLine x={0} stroke="var(--spotify-border)" />
            <Tooltip
              content={GapTooltip}
              cursor={{ fill: "var(--spotify-elevated-hover)" }}
            />
            <Bar
              dataKey="gap"
              radius={4}
              isAnimationActive={false}
              shape={(props: BarShapeProps) => {
                const datum = props.payload as unknown as GapDatum;
                const fill =
                  datum.gap >= 0
                    ? CHART_COLORS.divergingPositive
                    : CHART_COLORS.divergingNegative;
                return <Rectangle {...props} fill={fill} />;
              }}
            />
          </BarChart>
        </ResponsiveContainer>
      </div>
      {data.length === 0 && (
        <p className="status-text">No overlap data for this time range yet.</p>
      )}
    </div>
  );
}
