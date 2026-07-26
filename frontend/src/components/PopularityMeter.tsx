import StatTile from "./StatTile";

export default function PopularityMeter({ value }: { value: number }) {
  const rounded = Math.round(value);
  return (
    <StatTile label="Avg. track popularity" value={String(rounded)} hint="out of 100">
      <div
        className="meter-track"
        role="progressbar"
        aria-valuenow={rounded}
        aria-valuemin={0}
        aria-valuemax={100}
      >
        <div className="meter-fill" style={{ width: `${rounded}%` }} />
      </div>
    </StatTile>
  );
}
