
/**
 @function

 @description - Helper function to return different background, text, border color based
 on the product letter grade (S, A+, A, etc)

 @param {string} grade = The product letter grade
 */
export function getGradeColors(grade: string) {
  if (grade === "S") {
    return { bg: "bg-amber-950/40", text: "text-amber-300", border: "border-amber-500/50" };
  }
  if (grade.startsWith("A")) {
    return { bg: "bg-teal-950/40", text: "text-teal-300", border: "border-teal-500/50" };
  }
  if (grade.startsWith("B")) {
    return { bg: "bg-sky-950/40", text: "text-sky-300", border: "border-sky-500/50" };
  }
  if (grade.startsWith("C")) {
    return { bg: "bg-stone-800/40", text: "text-stone-300", border: "border-stone-500/50" };
  }
  if (grade.startsWith("D")) {
    return { bg: "bg-orange-950/40", text: "text-orange-300", border: "border-orange-500/50" };
  }
  if (grade === "F") {
    return { bg: "bg-red-950/40", text: "text-red-300", border: "border-red-500/50" };
  }
  return { bg: "bg-zinc-800/40", text: "text-zinc-400", border: "border-zinc-500/50" };
};

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
