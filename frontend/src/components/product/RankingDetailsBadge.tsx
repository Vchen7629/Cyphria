import { getGradeColors, getRankColors } from "../../utils/product/GetColors";

interface ProductRankBadgeProps {
  rank: number;
  grade: string;
  approval_percentage: number;
  mentions: number;
}

/**
  @component

  @description - Badge component for each product displaying its letter grade,
  percentage score, amount of comments mentioning the product

  @param {number} rank - the product rank number
  @param {string} grade - the product letter grade (S, A, A-, etc)
  @param {number} approval_percentage - confidence adjusted percentage of positive mentions across all mentions
  @param {number} mentions - number of reddit comments mentioning the product

 */
const ProductRankingDetailsBadge = ({ rank, grade, approval_percentage, mentions }: ProductRankBadgeProps) => {
  const gradeColors = getGradeColors(grade);
  const rankBorder = getRankColors(rank);

  return (
    <div className={`${gradeColors.bg} ${rankBorder.border} border-2 flex flex-col items-center w-[80px] h-[100px] rounded-lg py-2`}>
      <span className={`text-3xl ${gradeColors.text} font-bold`}>{grade}</span>
      <span className="text-md pt-[0.5px] font-bold text-zinc-200">{approval_percentage}%</span>
      <span className="text-[9px] pt-[8px] text-zinc-500">{mentions} opinions</span>
    </div>
  );
};

export default ProductRankingDetailsBadge
