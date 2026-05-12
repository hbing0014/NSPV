type ScoreGaugeProps = {
  label: string;
  score: number;
};

export function ScoreGauge({ label, score }: ScoreGaugeProps) {
  return (
    <div className="border border-line bg-white p-4">
      <div className="flex items-center justify-between gap-4">
        <span className="text-sm text-ink/70">{label}</span>
        <span className="text-xl font-semibold text-ink">{score}</span>
      </div>
      <div className="mt-3 h-2 w-full overflow-hidden bg-field">
        <div
          className="h-full bg-accent"
          style={{ width: `${Math.max(0, Math.min(100, score))}%` }}
        />
      </div>
    </div>
  );
}

