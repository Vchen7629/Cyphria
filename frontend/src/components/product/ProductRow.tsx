import { useState } from "react";
import { ChevronDown } from "lucide-react";
import type { ProductV3, Sentiment, Comment } from "../../mock/types";
import ProductRankingDetailsBadge from './RankingDetailsBadge'
import ProductBadges from "./ProductBadges";
import { Trophy } from "lucide-react";
import { getRankColors } from "../../utils/product/getRankColors";
import SentimentBar from "./SentimentBar";
import TopComments from "./TopComments";


interface ProductRowProps {
  product: ProductV3;
  sentiment?: Sentiment;
  comments?: Comment[];
}

const ProductRow = ({ product, sentiment, comments = [] }: ProductRowProps) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const trophyRankColor = getRankColors(product.rank)

  const defaultSentiment: Sentiment = sentiment || {
    positive_count: Math.round(product.approval_percentage * 10),
    neutral_count: Math.round((100 - product.approval_percentage) * 5),
    negative_count: Math.round((100 - product.approval_percentage) * 5),
  };

  return (
    <li className="border-b border-zinc-800/40 last:border-0">
      <div className="w-full py-4 px-4 flex items-start gap-4 text-left hover:bg-zinc-900/20 transition-colors">
        <ProductRankingDetailsBadge 
          rank={product.rank}
          grade={product.grade} 
          approval_percentage={product.approval_percentage} 
          mentions={product.mention_count}
        />

        <div className="flex-1 min-w-0">
          <header className="flex items-center gap-2 mb-1">
            {[1, 2, 3].includes(product.rank) && (
              <Trophy className={trophyRankColor.text}/>
            )}
            <h3 className="text-base font-medium text-zinc-200">
              {product.product_name}
            </h3>
            <ProductBadges
              isTopPick={product.is_top_pick}
              isMostDiscussed={product.is_most_discussed}
              isHiddenGem={product.is_hidden_gem}
              hasLimitedData={product.has_limited_data}
            />
          </header>

          <p className="text-sm text-zinc-500 leading-relaxed line-clamp-2">
            {product.tldr_summary}
          </p>

          <section className="flex items-center space-x-2 mt-2">
            <button 
              onClick={() => setIsExpanded(!isExpanded)}
              className="flex items-center space-x-1 px-2 py-1 rounded-xl text-xs bg-zinc-900 border border-zinc-700 text-zinc-500"
            >
              <span className="flex items-center">View more details</span>
              <ChevronDown
                className={`w-4 h-4 transition-transform ${isExpanded ? "rotate-180" : ""}`}
              />
            </button>
            <button
              className="flex items-center space-x-1 px-2 py-1 rounded-md text-xs bg-gray-700 border border-zinc-700 text-zinc-500"
            >
              <span className="flex items-center">View Prices</span>
            </button>
          </section>
        </div>
      </div>
      {isExpanded && (
        <div className="px-4 pb-4 pt-2 space-y-4 border-t border-zinc-800/40 mt-3 ml-12">
          <SentimentBar sentiment={defaultSentiment} />
          <TopComments comments={comments} />
        </div>
      )}
    </li>
  );
}

export default ProductRow