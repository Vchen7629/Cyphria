import { Sparkles, Flame, Gem, AlertCircle } from "lucide-react";

interface ProductBadgesProps {
  isTopPick?: boolean;
  isMostDiscussed?: boolean;
  isHiddenGem?: boolean;
  hasLimitedData?: boolean;
}
/**
 @component

 @description - Creates badges components based if the product has any of the boolean flags

 @param {boolean} isTopPick - Product is ranked number one
 @param {boolean} isMostDiscussed - Product has the most comment mentions
 @param {boolean} isHiddenGem - TDB
 @param {boolean} hasLimitedData - Product has less mentions than a mimum mention threshold
 */
const ProductBadges = ({ isTopPick, isMostDiscussed, isHiddenGem, hasLimitedData}: ProductBadgesProps) => {
  const badges = [];

  if (isTopPick) {
    badges.push(
      <span key="top" className="inline-flex items-center gap-1 px-1.5 py-0.5 text-[10px] rounded-xl bg-amber-500/15 text-amber-400">
        <Sparkles className="w-3 h-3" />
        Top Pick
      </span>
    );
  }

  if (isMostDiscussed) {
    badges.push(
      <span key="discussed" className="inline-flex items-center gap-1 px-1.5 py-0.5 text-[10px] rounded-xl bg-blue-500/15 text-blue-400">
        <Flame className="w-3 h-3" />
        Most Discussed
      </span>
    );
  }

  if (isHiddenGem) {
    badges.push(
      <span key="gem" className="inline-flex items-center gap-1 px-1.5 py-0.5 text-[10px] rounded-xl bg-purple-500/15 text-purple-400">
        <Gem className="w-3 h-3" />
        Hidden Gem
      </span>
    );
  }

  if (hasLimitedData) {
    badges.push(
      <span key="limited" className="inline-flex items-center gap-1 px-1.5 py-0.5 text-[10px] rounded-xl bg-zinc-700/50 text-zinc-400">
        <AlertCircle className="w-3 h-3" />
        Limited Data
      </span>
    );
  }

  if (badges.length === 0) return null;

  return <div className="flex flex-wrap gap-1.5 mt-1">{badges}</div>;
}

export default ProductBadges