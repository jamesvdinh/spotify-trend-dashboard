import type { TimeRange } from "../utils/types/trends";
import { TIME_RANGES, TIME_RANGE_LABELS } from "./shared";

export default function TimeRangeTabs({
  value,
  onChange,
}: {
  value: TimeRange;
  onChange: (value: TimeRange) => void;
}) {
  return (
    <div className="chart-filter-row" role="tablist" aria-label="Time range">
      {TIME_RANGES.map((range) => (
        <button
          key={range}
          type="button"
          role="tab"
          aria-selected={value === range}
          className={`chart-filter-tab ${value === range ? "chart-filter-tab-active" : ""}`}
          onClick={() => onChange(range)}
        >
          {TIME_RANGE_LABELS[range]}
        </button>
      ))}
    </div>
  );
}
