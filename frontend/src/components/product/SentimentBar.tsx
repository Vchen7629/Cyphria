import type { Sentiment } from "../../mock/types";

interface SentimentBarProps {
  sentiment: Sentiment;
}

const SentimentBar = ({ sentiment }: SentimentBarProps) => {
  const total = sentiment.positive_count + sentiment.neutral_count + sentiment.negative_count;
  if (total === 0) return null;

  const positive = Math.round((sentiment.positive_count / total) * 100);
  const neutral = Math.round((sentiment.neutral_count / total) * 100);

  return (
    <div className="space-y-2">
      <div className="flex justify-between text-xs">
        <span className="text-zinc-500">Sentiment breakdown</span>
        <div className="flex gap-4">
          <span className="text-emerald-400">{positive}% positive</span>
          <span className="text-zinc-400">{neutral}% neutral</span>
          <span className="text-red-400">{100 - positive - neutral}% negative</span>
        </div>
      </div>
      <div className="h-1.5 bg-zinc-800 rounded-full overflow-hidden flex">
        <div
          className="h-full bg-emerald-500/70 transition-all"
          style={{ width: `${positive}%` }}
        />
        <div
          className="h-full bg-zinc-500/50 transition-all"
          style={{ width: `${neutral}%` }}
        />
        <div
          className="h-full bg-red-500/70 transition-all"
          style={{ width: `${100 - positive - neutral}%` }}
        />
      </div>
    </div>
  );
}

export default SentimentBar