import { ProductV3 } from "../../mock/types"
import { getGradeColors } from "../../utils/product/GetGradeColors";

interface TopMentionProductProps {
    product: ProductV3
}

const TopMentionedProductCard = ({ product }: TopMentionProductProps) => {
    const gradeColors = getGradeColors(product.grade);

    return (
        <li
            className="flex items-center space-x-1 py-1.5 px-2.5 bg-zinc-900 border border-zinc-700 rounded-lg w-fit"
        >
            <div className={`flex items-center justify-center w-7 h-5 rounded-lg border ${gradeColors.border} ${gradeColors.bg}`}>
                <span className="text-xs font-semibold">{product.grade}</span>
            </div>
            <div className="text-xs min-w-0 flex-1">{product.product_name}</div>
        </li>
    )
}

export default TopMentionedProductCard