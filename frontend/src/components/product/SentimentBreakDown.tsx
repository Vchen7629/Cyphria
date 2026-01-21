import type { Sentiment } from "../../mock/types";

/**
 @component

 @description - Component that displays in the dropdown menu when the user clicks on the view more details button for each product on the topic page. Displays a bar with 
 3 sections  (positive, neutral, negative) with varying widths based on how many positive, neutral, or negative sentiments for the current product

 @param {Sentiment} sentiment - The current product's sentiment metadata object
 */
const SentimentBreakDown = ({ sentiment }: { sentiment: Sentiment }) => {
  const total = sentiment.positive_count + sentiment.neutral_count + sentiment.negative_count;
  if (total === 0) return null;

  const positive = Math.round((sentiment.positive_count / total) * 100);
  const neutral = Math.round((sentiment.neutral_count / total) * 100);
  const negative = 100 - positive - neutral;

  return (
    <div className="space-y-2 animate-fade-in-up">
      <div className="flex justify-between text-xs">
        <span className="text-zinc-500">Sentiment breakdown</span>
        <div className="flex gap-4">
          <span className="text-emerald-400">{positive}% positive</span>
          <span className="text-zinc-400">{neutral}% neutral</span>
          <span className="text-red-400">{negative}% negative</span>
        </div>
      </div>

      <div className="relative">
        <div className="h-2 bg-zinc-800 rounded-full overflow-hidden flex">
          <div className="h-full bg-emerald-500/70 transition-all" style={{ width: `${positive}%` }}/>
          <div className="h-full bg-zinc-500/50 transition-all" style={{ width: `${neutral}%` }}/>
          <div className="h-full bg-red-500/70 transition-all" style={{ width: `${negative}%` }}/>
        </div>
        {/* Hover zones with tooltips */}
        <div className="absolute inset-0 flex">
          <div className="group/segment relative h-full hover:bg-emerald-500/30 cursor-pointer" style={{ width: `${positive}%` }}>
            <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-2 py-1 bg-emerald-600 text-white text-xs rounded invisible opacity-0 group-hover/segment:visible group-hover/segment:animate-fade-in-up [animation-delay:100ms] whitespace-nowrap pointer-events-none z-10">
              {sentiment.positive_count.toLocaleString()} positive
            </div>
          </div>
          <div className="group/segment relative h-full hover:bg-zinc-500/30 cursor-pointer" style={{ width: `${neutral}%` }}>
            <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-2 py-1 bg-zinc-600 text-white text-xs rounded invisible opacity-0 group-hover/segment:visible group-hover/segment:animate-fade-in-up [animation-delay:100ms] whitespace-nowrap pointer-events-none z-10">
              {sentiment.neutral_count.toLocaleString()} neutral
            </div>
          </div>
          <div className="group/segment relative h-full hover:bg-red-500/30 cursor-pointer" style={{ width: `${negative}%` }}>
            <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-2 py-1 bg-red-600 text-white text-xs rounded invisible opacity-0 group-hover/segment:visible group-hover/segment:animate-fade-in-up [animation-delay:100ms] whitespace-nowrap pointer-events-none z-10">
              {sentiment.negative_count.toLocaleString()} negative
            </div>
          </div>
        </div>
      </div>

      <div className="flex items-center justify-between text-xs pt-1">
        <div className="flex">
          <span className="text-zinc-400">Comment Mentions Breakdown: </span>
          <span className="text-emerald-400/80 font-semilight ml-2">{sentiment.positive_count.toLocaleString()} positive</span>
          <span className="text-zinc-500 ml-2">| {sentiment.neutral_count.toLocaleString()} neutral |</span>
          <span className="text-red-400/80 ml-2">{sentiment.negative_count.toLocaleString()} negative</span>
        </div>
        <span className="text-zinc-400">
          {total.toLocaleString()} total mentions | Neutral mentions excluded from grade
        </span>
      </div>
    </div>
  );
}

export default SentimentBreakDown