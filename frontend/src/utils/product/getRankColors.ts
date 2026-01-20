
/**
 @function

 @description - Helper function to return a border and text color based on the product rank

 @param {number} rank - the product rank number (1, 2, 3, etc)
 */
export function getRankColors(rank: number) {
  if (rank === 1) return {border: "border-amber-500/50", text: "text-amber-500/50"}; // Gold
  if (rank === 2) return {border: "border-zinc-400/50", text: "text-zinc-400/50"};  // Silver
  if (rank === 3) return {border: "border-orange-600/50", text: "text-orange-600/50"}; // Bronze
  return {border: "border-zinc-700/50", text: "text-zinc-700/50"}; // Default
};
